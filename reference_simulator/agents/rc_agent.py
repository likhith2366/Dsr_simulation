"""
rc_agent.py — the CONTROLLER agent. Controls RC1 and RC2. Runs as its own process.

    python rc_agent.py            join / start a run
    python rc_agent.py --reset    wipe blackboard.json first (fresh run)

Start it together with scout_agent.py in a second terminal (see README.md).
Neither agent works alone: a round only advances once both have submitted.

ROLE
    RC1 and RC2 are Repair Crews. They repair faults (the only units that can)
    and also discover faults as they travel (inspection range 2).
        RC1: move_speed 8, repair_speed 5, total_resources 30
        RC2: move_speed 6, repair_speed 8, total_resources 40
    Repairing spends the crew's resources one-for-one. A crew must stand
    exactly on the fault's coordinate to repair it.

    One controller decides for BOTH crews in a single LLM call. An earlier
    version gave each crew its own LLM call; they kept picking the same fault
    and acted on different clock ticks. Deciding jointly fixed both.

SCENARIO THIS WAS TUNED FOR (cases/case1)
    Faults A=10, B=8, C=8, D=40 repair. D is larger than either crew can pay
    alone, so both crews must work it. Total need 66 vs total resources 70.

BLACKBOARD CONTRACT
    writes  assigned    — crew committed to a fault (for the scout to read)
            needs_both  — a fault exceeds every crew's remaining resources
            repaired    — a fault became inactive
            explored    — a region a crew entered (crews search too)
    reads   brief_for_controller(): faults found, regions swept, scout's target

WHAT THE LLM DECIDES vs WHAT CODE DECIDES
    LLM : for each Idle crew — which fault to go to, when to repair, or which
          region to search when nothing is known.
    Code: "continue" while busy (forced_cmd), "stay" when nothing is left,
          repair amounts clamped to the legal max (clamp_repair), moves to the
          crew's own position redirected (fix_noop_move).
    In the reference run the LLM made 16 of the 80 crew commands. The guards
    each exist because a run broke without them — see their docstrings.

KNOWN INEFFICIENCY
    If ONE crew is busy and the other Idle, the LLM is still asked for both
    crews and the busy crew's answer is thrown away (overwritten with
    "continue"). Asking only about the free crew would be cleaner.
"""

import json
import sys
import time

import sim_client
from blackboard  import Blackboard, reset
from llm_client  import llm, extract_json
from scout_agent import region_centre, inside

ME         = "CONTROLLER"   # must match an entry in blackboard.EXPECTED
MAX_ROUNDS = 45             # safety stop, independent of the simulator's limit

SYSTEM_PROMPT = """You are the CONTROLLER managing two repair crews (RC1 and RC2) in a power grid disaster.
Faults are hidden until someone inspects the area holding them. A scout unit is
searching too, but your crews also inspect 2 around themselves as they travel,
so they find faults on their own. Never leave a crew standing still.

Priority for each crew, in order:
1. Crew can repair a fault right now (listed under CAN REPAIR NOW) -> repair it.
2. A known fault still needs work -> send the crew to its coordinates.
   Send the two crews to DIFFERENT faults so they work in parallel.
   EXCEPTION: if a fault needs more repair than one crew's remaining resources,
   send BOTH crews to that same fault. They repair it together, each contributing per step.
3. Nothing known to repair -> SEARCH. Send the crew to the centre of an
   UNSEARCHED AREA so it uncovers faults while it travels. Send the two crews
   to DIFFERENT areas, and prefer areas the scout is not already heading to.
4. Only if every fault is repaired and every area searched -> stay.

Valid commands per crew:
  move:   {"type": "move", "waypoints": [[x, y]]}
  repair: {"type": "repair", "fault": "FAULT_NAME", "amount": N}
  stay:   {"type": "stay"}

Output EXACTLY this JSON structure - no explanation, no markdown:
{"RC1": <command>, "RC2": <command>}"""

STAY_BOTH = {"RC1": {"type": "stay"}, "RC2": {"type": "stay"}}   # fallback if reply is unparseable

forced_cmd = sim_client.forced_cmd   # busy units accept only "continue"


def dist(a, b) -> float:
    """Straight-line distance. Only used to rank/describe; real travel follows
    roads (see _find_fastest_path in the simulator) and can be longer."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


# ════════════════════════════════════════════════ guards on LLM output
# Each of these corrects a specific failure observed in a real run.

def fix_noop_move(cmd: dict, rc: dict, faults: list[dict]) -> dict:
    """
    Replace a move to the crew's CURRENT position.

    Observed: a crew with 12 resources stood at [0,-16] while the only
    remaining fault was at [-4,-8]. The model ordered "move to [0,-16]" six
    rounds running. The simulator accepts such a move as success, so no error
    surfaced — the clock just ran out.

    Fix: redirect to the nearest active fault that is somewhere else.
    This is a code decision, not the model's.
    """
    if cmd.get("type") != "move" or not cmd.get("waypoints"):
        return cmd
    if list(cmd["waypoints"][-1]) != list(rc["position"]):
        return cmd   # a real move — leave it alone

    reachable = [f for f in faults if list(f["position"]) != list(rc["position"])]
    if not reachable:
        return {"type": "stay"}
    target = min(reachable, key=lambda f: dist(rc["position"], f["position"]))
    print(f"  [{ME}] no-op move dropped -> redirecting to fault "
          f"{target['name']} at {target['position']}", flush=True)
    return {"type": "move", "waypoints": [list(target["position"])]}


def clamp_repair(cmd: dict, rc: dict) -> dict:
    """
    Cap a repair amount at what the simulator allows this step.

    The legal maximum is in rc["repairable_faults"][i]["maximum_amount"]
    (min of repair_speed, remaining fault need, remaining crew resources).

    Observed: the model asked RC1 (repair_speed 5) to repair 10. The
    simulator rejected the batch with HTTP 400, the clock did not advance,
    and the model repeated the same command forever — a deadlock.

    Also: a repair on a fault the crew is not standing on becomes "stay".
    """
    if cmd.get("type") != "repair":
        return cmd
    allowed = {f["name"]: f["maximum_amount"] for f in rc.get("repairable_faults", [])}
    name = cmd.get("fault")
    if name not in allowed:
        return {"type": "stay"}
    cmd["amount"] = min(int(cmd.get("amount", allowed[name])), allowed[name])
    return cmd


class RCAgent:
    def __init__(self, bb: Blackboard, regions: list[dict] | None = None):
        self.bb      = bb
        self.regions = regions or []   # hidden regions, for searching

    def unsearched(self) -> list[dict]:
        """Regions no unit (crew or scout) has entered yet, per the board."""
        swept = self.bb.explored_regions()
        return [r for r in self.regions if r["name"] not in swept]

    def observe(self, state: dict) -> None:
        """Buffer posts about what changed. Called every round before act()."""
        # Crews discover faults while travelling, so they clear regions too.
        # Posting "explored" stops the scout from wasting a trip there.
        for region in self.regions:
            if region["name"] in self.bb.explored_regions():
                continue
            if any(inside(state["objects"][c]["position"], region) for c in ("RC1", "RC2")):
                self.bb.post("explored", region=region["name"])

        for f in state.get("faults", []):
            if not f.get("active"):
                self.bb.post_once("repaired", fault=f["name"])
                continue
            need = f.get("remaining_repair_resource")
            if need is None:          # not analyzed yet — size unknown
                continue
            budgets = [state["objects"][c]["remaining_resources"] for c in ("RC1", "RC2")]
            if need > max(budgets):
                # Posts again whenever `needed` changes (post_once matches on
                # all fields), so the board shows D shrinking: 40 -> 32 -> 19.
                self.bb.post_once("needs_both", fault=f["name"], needed=need)

    def act(self, state: dict) -> dict:
        """Return {"RC1": command, "RC2": command} for this round."""
        faults   = [f for f in state.get("faults", []) if f.get("active")]  # discovered AND unrepaired
        rc1, rc2 = state["objects"]["RC1"], state["objects"]["RC2"]
        f1, f2   = forced_cmd(rc1), forced_cmd(rc2)

        # 1. Both busy -> no decision to make. No LLM call.
        if f1 and f2:
            print(f"  [{ME}] both crews busy -> continue", flush=True)
            return {"RC1": f1, "RC2": f2}

        # 2. Nothing to repair and nowhere to search -> stay. No LLM call.
        #    Note: at this point the job the agents know about is done, but the
        #    score is still 0 because no one closes switches (see README).
        unsearched = self.unsearched()
        if not faults and not unsearched:
            print(f"  [{ME}] nothing left to repair or search -> stay", flush=True)
            return {"RC1": f1 or {"type": "stay"}, "RC2": f2 or {"type": "stay"}}

        # 3. Build the prompt. Everything is pre-computed into plain text:
        #    distances, "ALREADY THERE", affordability. qwen3:4b is unreliable at
        #    comparing coordinates or scanning a JSON array itself — an earlier
        #    version gave it the raw fault list and it declared "all fixed" with
        #    two faults still active.
        crews     = {"RC1": rc1, "RC2": rc2}
        fault_txt = ("\n".join(self._fault_line(f, crews) for f in faults) if faults
                     else "  (none discovered yet — go and search)")
        area_txt  = ("\n".join(f"  - {r['name']}, centre {region_centre(r)}" for r in unsearched)
                     if unsearched else "  (all areas searched)")

        user_msg = (
            f"{self._crew_line('RC1', rc1)}\n{self._crew_line('RC2', rc2)}\n\n"
            f"FAULTS DISCOVERED AND STILL ACTIVE ({len(faults)}):\n{fault_txt}\n\n"
            f"UNSEARCHED AREAS ({len(unsearched)}):\n{area_txt}\n\n"
            f"FROM THE BLACKBOARD — what the scout has reported:\n"
            f"{self.bb.brief_for_controller()}\n\n"
            "Decide commands for BOTH RC1 and RC2."
        )

        print(f"\n  [{ME}] >>> LLM", flush=True)
        print(f"  [{ME}]     {user_msg}", flush=True)

        t0   = time.time()
        raw  = llm(SYSTEM_PROMPT, user_msg, prefill='{"RC1":')
        cmds = extract_json(raw, dict(STAY_BOTH))

        # 4. Sanitize, in this order:
        for key in ("RC1", "RC2"):                    # malformed entry -> stay
            if not isinstance(cmds.get(key), dict):
                cmds[key] = {"type": "stay"}
        if f1: cmds["RC1"] = f1                       # busy crew -> continue (discards LLM answer)
        if f2: cmds["RC2"] = f2
        for crew, rc in (("RC1", rc1), ("RC2", rc2)):
            cmds[crew] = clamp_repair(cmds[crew], rc)
            cmds[crew] = fix_noop_move(cmds[crew], rc, faults)

        print(f"  [{ME}] <<< ({time.time() - t0:.1f}s) {raw}", flush=True)
        print(f"  [{ME}]     RC1 {json.dumps(cmds['RC1'])}", flush=True)
        print(f"  [{ME}]     RC2 {json.dumps(cmds['RC2'])}", flush=True)
        # Compare the RAW line with the RC1/RC2 lines in the log to see
        # exactly where code overrode the model.

        # 5. Tell the scout which faults are now spoken for.
        for crew in ("RC1", "RC2"):
            cmd = cmds[crew]
            if cmd.get("type") == "repair":
                self.bb.post_once("assigned", crew=crew, fault=cmd["fault"])
            elif cmd.get("type") == "move" and cmd.get("waypoints"):
                target = list(cmd["waypoints"][-1])
                for f in faults:   # a move counts as an assignment only if it targets a fault
                    if list(f["position"]) == target:
                        self.bb.post_once("assigned", crew=crew, fault=f["name"])
        return cmds

    # ── prompt helpers ─────────────────────────────────────────
    @staticmethod
    def _fault_line(f: dict, crews: dict | None = None) -> str:
        """
        One fault as a prompt line, e.g.
          - Fault D at [-4, -8] — needs 8 repair  [RC1 9 away; RC2 ALREADY THERE,
            only 0 resources — cannot finish alone]
        """
        need = f.get("remaining_repair_resource")
        txt  = f"needs {need} repair" if need is not None else "repair amount unknown until analyzed"
        line = f"  - Fault {f['name']} at {f['position']} — {txt}"
        if crews:
            # Spell out distance and affordability: the model is unreliable at
            # comparing coordinates itself and will send crews to where they
            # already stand if left to work it out.
            parts = []
            for name, rc in crews.items():
                d = dist(rc["position"], f["position"])
                where = "ALREADY THERE" if d == 0 else f"{d:.0f} away"
                if need is not None and rc["remaining_resources"] < need:
                    where += f", only {rc['remaining_resources']} resources — cannot finish alone"
                parts.append(f"{name} {where}")
            line += "  [" + "; ".join(parts) + "]"
        return line

    @staticmethod
    def _crew_line(name: str, rc: dict) -> str:
        """
        One crew as a prompt line, e.g.
          RC1: at [12, -8], 30 resources left, repairs 5/step. CAN REPAIR NOW: A (up to 5/step)
        "CAN REPAIR NOW" comes straight from the simulator's repairable_faults.
        """
        can     = rc.get("repairable_faults", [])
        can_txt = ", ".join(f"{c['name']} (up to {c['maximum_amount']}/step)" for c in can) or "nothing here"
        return (f"{name}: at {rc['position']}, {rc['remaining_resources']} resources left, "
                f"repairs {rc['repair_speed']}/step. CAN REPAIR NOW: {can_txt}")


def main() -> None:
    """Same loop as scout_agent.main — see the docstring there."""
    if "--reset" in sys.argv:
        print("[BB] resetting board", flush=True)
        reset()

    bb = Blackboard(ME)
    print("=" * 66, flush=True)
    print(f"{ME} — RC1 + RC2, repairing what the scout finds", flush=True)
    print("=" * 66, flush=True)

    regions = bb.boot_if_needed()
    print(f"[MAP] {len(regions)} hidden regions: "
          + ", ".join(f"{r.get('name','?')} {region_centre(r)}" for r in regions), flush=True)
    agent = RCAgent(bb, regions)

    try:
        while True:
            bb.sync()
            if bb.over:
                print(f"\n[{ME}] run is over", flush=True)
                break
            if bb.round > MAX_ROUNDS:
                print(f"\n[{ME}] hit round cap {MAX_ROUNDS}", flush=True)
                break
            if bb.already_submitted():
                if not bb.wait_for_next_round(bb.round):
                    break
                continue

            seen  = bb.round
            state = sim_client.get_state()
            print(f"\n{'='*66}\nROUND {seen}  {sim_client.summary(state)}", flush=True)
            if sim_client.is_over(state):
                print(f"[{ME}] terminal status", flush=True)
                break

            agent.observe(state)
            result = bb.submit(agent.act(state), seen_round=seen)
            print(f"  [{ME}] submit -> {result}", flush=True)

            if result == "over":
                break
            if result == "waiting" and not bb.wait_for_next_round(seen):
                break

    except KeyboardInterrupt:
        print(f"\n[{ME}] stopped", flush=True)
    finally:
        bb.sync()
        print("\n" + "=" * 66, flush=True)
        print("BLACKBOARD", flush=True)
        print("=" * 66, flush=True)
        print(bb.dump(), flush=True)


if __name__ == "__main__":
    main()
