"""
scout_agent.py — the SCOUT agent. Controls PAC1. Runs as its own process.

    python scout_agent.py            join / start a run
    python scout_agent.py --reset    wipe blackboard.json first (fresh run)

Start it together with rc_agent.py in a second terminal (see README.md).
Neither agent works alone: a round only advances once both have submitted.

ROLE
    PAC1 is a Patrol & Assessment Crew: fast (move_speed 10), wide inspection
    range (4), but it CANNOT repair. Faults start hidden inside "unknown
    regions" and are invisible in the simulator state until some unit comes
    within inspection range. The scout's job is to go uncover them.

    The repair crews also discover faults as they travel (range 2). In
    practice the crews found 3 of 4 faults and the scout found the one in the
    region no crew was heading to.

BLACKBOARD CONTRACT
    writes  discovered  — every fault visible in the state
            explored    — a region PAC1 has entered
            scouting    — the target PAC1 was just sent to
    reads   brief_for_scout(): which crews are on which faults, what is
            repaired, which fault needs both crews

WHAT THE LLM DECIDES vs WHAT CODE DECIDES
    LLM : which unexplored region to go to next (only when PAC1 is Idle and
          at least one region is unexplored).
    Code: "continue" while busy, "stay" when every region is explored.
    In the reference run the LLM was called 3 times in 40 rounds.
"""

import json
import sys
import time

import sim_client
from blackboard import Blackboard, reset
from llm_client import llm, extract_json

ME         = "SCOUT"      # must match an entry in blackboard.EXPECTED
MAX_ROUNDS = 45           # safety stop, independent of the simulator's limit

SYSTEM_PROMPT = """You are the SCOUT controlling PAC1, a fast patrol unit in a power grid disaster.
Faults are hidden inside unexplored regions and only your inspection reveals them.
You cannot repair anything. Your job is to uncover faults so the repair crews have work.

Decide where PAC1 goes next:
- Send it to the centre of an UNEXPLORED region, by coordinates.
- Prefer the region nearest to PAC1's current position.
- The repair crews are already handling the faults listed as assigned, so
  uncovering new faults elsewhere is worth more than revisiting their area.
- If every region is explored, stay.

Valid commands:
  move: {"type": "move", "waypoints": [[x, y]]}
  stay: {"type": "stay"}

Output ONLY the JSON command. No explanation, no markdown."""


# ── geometry helpers (also imported by rc_agent.py) ─────────────
# Regions are axis-aligned rectangles from UnknownState_v1.json:
#   {"name": ..., "lower_left": [x0, y0], "upper_right": [x1, y1]}

def region_centre(region: dict) -> list[int]:
    """Integer centre of a region — the coordinate we suggest as a move target.
    The centre need not be on a road: off-road pixels are passable, just slow
    (1 pixel per step, vs move_speed on a road — see movement_cost in
    simulator_core_v23.py)."""
    (x0, y0), (x1, y1) = region["lower_left"], region["upper_right"]
    return [round((x0 + x1) / 2), round((y0 + y1) / 2)]


def inside(pos, region) -> bool:
    """True if position [x, y] lies within the region (edges included)."""
    (x0, y0), (x1, y1) = region["lower_left"], region["upper_right"]
    return x0 <= pos[0] <= x1 and y0 <= pos[1] <= y1


class ScoutAgent:
    def __init__(self, bb: Blackboard, regions: list[dict]):
        self.bb      = bb
        self.regions = regions   # hidden regions for this scenario, fixed for the run

    def observe(self, state: dict) -> None:
        """
        Buffer posts about what is newly true. Called every round before act().

        "explored" is approximate: a region counts as explored once PAC1's
        position is inside it, not once every pixel in it has been inspected.
        With inspection range 4 and small regions this has been good enough.
        """
        pac = state["objects"]["PAC1"]
        for region in self.regions:
            if region["name"] not in self.bb.explored_regions() and inside(pac["position"], region):
                self.bb.post("explored", region=region["name"])

        # The simulator only lists discovered faults, so anything in the list
        # has been revealed — by PAC1 or by a crew. The scout posts all of them,
        # so the "discovered" author is SCOUT even when a crew found the fault.
        for f in state.get("faults", []):
            self.bb.post_once("discovered", fault=f["name"], position=str(f["position"]))

    def unexplored(self) -> list[dict]:
        """Regions no unit (scout or crew) has entered yet, per the board."""
        swept = self.bb.explored_regions()
        return [r for r in self.regions if r["name"] not in swept]

    def act(self, state: dict) -> dict:
        """Return PAC1's command for this round."""
        pac = state["objects"]["PAC1"]

        # 1. Busy (Moving / Analyzing) -> only "continue" is legal. No LLM call.
        #    Analyzing happens automatically the instant PAC1 finds a fault;
        #    sending a move then gets the whole batch rejected (see sim_client).
        if busy := sim_client.forced_cmd(pac):
            print(f"  [{ME}] busy ({pac.get('state')}) -> continue", flush=True)
            return busy

        # 2. Nothing left to explore -> stay. No LLM call.
        remaining = self.unexplored()
        if not remaining:
            print(f"  [{ME}] every region swept -> stay", flush=True)
            return {"type": "stay"}

        # 3. A real choice: ask the LLM which region to go to.
        #    The prompt is pre-digested text (not raw state JSON). Small models
        #    reason badly over raw JSON; a short list of options works far better.
        region_txt = "\n".join(f"  - {r['name']}, centre {region_centre(r)}" for r in remaining)
        user_msg = (
            f"PAC1 is at {pac['position']}, moves {pac['move_speed']}/step, "
            f"inspects {pac['inspection_range']} around itself.\n\n"
            f"UNEXPLORED REGIONS ({len(remaining)} left):\n{region_txt}\n\n"
            f"FROM THE BLACKBOARD — what the repair crews are doing:\n"
            f"{self.bb.brief_for_scout()}\n\n"
            f"Where does PAC1 go next?"
        )

        print(f"\n  [{ME}] >>> LLM", flush=True)
        print(f"  [{ME}]     {user_msg}", flush=True)

        t0  = time.time()
        raw = llm(SYSTEM_PROMPT, user_msg, prefill='{"type":', budget=60)
        cmd = extract_json(raw, {"type": "stay"})   # unparseable reply -> stay

        print(f"  [{ME}] <<< ({time.time() - t0:.1f}s) {raw}", flush=True)
        print(f"  [{ME}]     CMD {json.dumps(cmd)}", flush=True)

        # Tell the controller where PAC1 is going, so it can send crews elsewhere.
        if cmd.get("type") == "move" and cmd.get("waypoints"):
            self.bb.post("scouting", target=str(cmd["waypoints"][-1]))
        return cmd


def main() -> None:
    """
    The agent's own loop. Structure is identical in rc_agent.py:

        boot (or join) -> repeat:
            if game over / round cap          -> exit
            if already submitted this round   -> wait for the other agent
            read state, observe, act, submit
            if submit said "waiting"          -> wait for the other agent
    """
    if "--reset" in sys.argv:
        print("[BB] resetting board", flush=True)
        reset()

    bb = Blackboard(ME)
    print("=" * 66, flush=True)
    print(f"{ME} — PAC1, discovering hidden faults", flush=True)
    print("=" * 66, flush=True)

    regions = bb.boot_if_needed()
    print(f"[MAP] {len(regions)} hidden regions: "
          + ", ".join(f"{r.get('name','?')} {region_centre(r)}" for r in regions), flush=True)
    # "[MAP] 0 hidden regions" means hiding failed — see sim_client.case_unknown_regions

    agent = ScoutAgent(bb, regions)

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

            seen  = bb.round                 # remember which round we decide for
            state = sim_client.get_state()
            print(f"\n{'='*66}\nROUND {seen}  {sim_client.summary(state)}", flush=True)
            if sim_client.is_over(state):
                print(f"[{ME}] terminal status", flush=True)
                break

            agent.observe(state)
            result = bb.submit({"PAC1": agent.act(state)}, seen_round=seen)
            print(f"  [{ME}] submit -> {result}", flush=True)

            if result == "over":
                break
            if result == "waiting" and not bb.wait_for_next_round(seen):
                break
            # "flushed" or "stale": loop straight back and read the new round

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
