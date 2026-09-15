"""
blackboard.py — the shared memory the two agents communicate through.

WHAT A BLACKBOARD IS
    A classic multi-agent pattern: independent agents never call or message
    each other. Instead they all read and write one shared data store. Each
    agent posts facts about what it sees or does; the others pick those facts
    up on their next turn. Here there are two agents, each its own OS process:
        SCOUT      (scout_agent.py) — drives PAC1, finds hidden faults
        CONTROLLER (rc_agent.py)    — drives RC1 + RC2, repairs faults

WHY THERE IS NO ORCHESTRATOR
    An earlier version had run_agents.py calling scout then controller in a
    loop. It was removed: the board itself carries the turn-taking. Each agent
    puts its commands in `pending`; whichever agent's submission completes the
    set sends the merged batch to the simulator and starts the next round.

STORAGE
    The board is a JSON file (blackboard.json, next to this file) so two
    separate processes can share it. Writes are guarded by a lock file
    (blackboard.lock) and written atomically (tmp file + os.replace).

    blackboard.json
      round    int     current round (== simulator time step being decided)
      booted   bool    simulator started and scenario loaded
      over     bool    game ended; both agents exit when they see this
      pending  {agent_name: {unit: command}}   this round's submissions so far
      posts    [ {step, author, kind, ...fields} ]   append-only message log

POST KINDS (the "messages")
      kind         written by     fields              meaning
      discovered   SCOUT          fault, position     a fault became visible
      explored     SCOUT or CTRL  region              a hidden region was entered
      scouting     SCOUT          target              where PAC1 is heading
      assigned     CONTROLLER     crew, fault         a crew committed to a fault
      needs_both   CONTROLLER     fault, needed       fault bigger than any one
                                                      crew's remaining resources
      repaired     CONTROLLER     fault               a fault is fully repaired

    Agents never read the raw JSON into their prompts. brief_for_scout() and
    brief_for_controller() turn the OTHER agent's posts into short plain-text
    lines that are pasted into the LLM prompt.

ONE ROUND, END TO END
    1. both agents sync() and read the simulator state
    2. each calls observe() -> buffers posts about what changed
    3. each calls act()     -> decides its units' commands (LLM if needed)
    4. each calls submit()  -> under the lock: write buffered posts, add
                               commands to `pending`
    5. the submit that completes `pending` also calls sim_client.execute()
       with the merged commands, increments `round`, clears `pending`
    6. the other agent, blocked in wait_for_next_round(), sees the new round

TO START FRESH: delete blackboard.json, or run either agent with --reset.
A stale board from a previous run will otherwise make the agents think the
game is already booted/over.
"""

import json
import os
import time
from pathlib import Path

import sim_client

# Every name here must submit before a round can flush. Adding a third agent
# (e.g. a switch operator) means adding its name here — and it MUST then be
# running, or every round will wait forever for its submission.
EXPECTED = ("SCOUT", "CONTROLLER")

BOARD = Path(__file__).resolve().parent / "blackboard.json"
LOCK  = Path(__file__).resolve().parent / "blackboard.lock"

# If a lock file is older than this, its owner is assumed to have crashed
# while holding it, and the lock is broken. Must exceed the longest time the
# lock is legitimately held — booting the simulator takes ~10-30 s.
STALE = 90.0


# ════════════════════════════════════════════════ file lock

class _Lock:
    """
    Cross-process mutex using exclusive file creation.

    os.open with O_CREAT | O_EXCL fails if the file already exists, and the OS
    guarantees only one process can win that race. Holding the lock = owning
    blackboard.lock. Usage:  with _Lock(): ...read, modify, write...

    Only disk reads/writes happen under the lock. The slow LLM call happens
    OUTSIDE it, otherwise one agent thinking would freeze the other.
    """

    def __init__(self, path: Path = LOCK, timeout: float = 120.0):
        self.path, self.timeout, self.fd = path, timeout, None

    def __enter__(self):
        deadline = time.time() + self.timeout
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, str(os.getpid()).encode())   # owner pid, for debugging
                return self
            except FileExistsError:
                # someone else holds it — break it if abandoned, else retry
                try:
                    if time.time() - self.path.stat().st_mtime > STALE:
                        print("  [BB]   breaking stale lock", flush=True)
                        self.path.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue   # released between our attempt and the stat
                if time.time() > deadline:
                    raise TimeoutError("blackboard lock timed out")
                time.sleep(0.15)

    def __exit__(self, *exc):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        self.path.unlink(missing_ok=True)


# ════════════════════════════════════════════════ raw file access

def _blank() -> dict:
    """A board for a run that has not started."""
    return {"round": 1, "booted": False, "over": False, "pending": {}, "posts": []}


def _read() -> dict:
    """Load the board. A missing or corrupt file is treated as a blank board."""
    if not BOARD.exists():
        return _blank()
    try:
        return json.loads(BOARD.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _blank()


def _write(data: dict) -> None:
    """Write atomically: a reader never sees a half-written file."""
    tmp = BOARD.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, BOARD)


def reset() -> None:
    """Clear the board (and any leftover lock) so a new run starts clean."""
    LOCK.unlink(missing_ok=True)
    _write(_blank())


# ════════════════════════════════════════════════ agent-facing handle

class Blackboard:
    """
    One agent's view of the shared board. Each agent process makes exactly one:
        bb = Blackboard("SCOUT")   or   Blackboard("CONTROLLER")

    `self.data` is a local copy of the file; call sync() to refresh it.
    Posts are BUFFERED locally by post()/post_once() and only reach the file
    on the next submit(), so all of an agent's writes for a round land in one
    locked operation.
    """

    def __init__(self, me: str):
        if me not in EXPECTED:
            raise ValueError(f"unknown agent {me!r}")
        self.me      = me
        self.data    = _read()
        self._buffer = []        # posts waiting for the next submit()

    # ── state ──────────────────────────────────────────────────
    @property
    def round(self) -> int:
        return self.data["round"]

    @property
    def over(self) -> bool:
        return self.data["over"]

    def sync(self) -> None:
        """Re-read the file. Call before trusting round/over/posts."""
        self.data = _read()

    # ── boot ───────────────────────────────────────────────────
    def boot_if_needed(self) -> list[dict]:
        """
        Start the simulator and load the scenario — exactly once per run.

        Both agents call this at startup, in any order. The lock ensures only
        the first one does the work; the second sees booted=True and skips.
        The lock is held for the whole boot on purpose, so the second agent
        waits here instead of reading a half-loaded simulator.

        Returns the hidden regions, which both agents use for searching.
        """
        with _Lock():
            data = _read()
            if not data["booted"]:
                print(f"  [BB]   {self.me} claiming boot", flush=True)
                if not sim_client.ensure_running():
                    raise RuntimeError("simulator failed to start")
                print(f"  [SIM] {sim_client.load_case()}", flush=True)
                time.sleep(2.0)   # let the simulator settle after load
                data["booted"] = True
                _write(data)
            self.data = data
        return sim_client.hidden_regions()

    def wait_for_boot(self, timeout: float = 90.0) -> None:
        """Block until some agent has booted. Currently unused: boot_if_needed covers it."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.sync()
            if self.data["booted"]:
                return
            time.sleep(0.4)
        raise TimeoutError("simulator never booted")

    # ── writing posts ──────────────────────────────────────────
    def post(self, kind: str, **data) -> None:
        """Buffer a post. It is stamped with a step and written on submit()."""
        self._buffer.append({"author": self.me, "kind": kind, **data})

    def post_once(self, kind: str, **data) -> None:
        """
        Buffer a post only if the same kind + fields is not already on the board.

        Agents re-observe the same world every round (fault B stays visible for
        the whole game), so without this the board would fill with duplicates.
        Matching ignores author and step: if either agent already posted it,
        it is not posted again.
        """
        cand = {"author": self.me, "kind": kind, **data}
        if cand in self._buffer:
            return
        for p in self.data["posts"]:
            if p.get("kind") == kind and all(p.get(k) == v for k, v in data.items()):
                return
        self._buffer.append(cand)

    # ── reading posts ──────────────────────────────────────────
    def _of_kind(self, *kinds: str) -> list[dict]:
        return [p for p in self.data["posts"] if p.get("kind") in kinds]

    def _values(self, kind: str, key: str) -> list:
        return [p[key] for p in self.data["posts"] if p.get("kind") == kind and key in p]

    def explored_regions(self) -> set[str]:
        """Regions entered by ANY unit (scout or crew). Both agents use this."""
        return set(self._values("explored", "region"))

    def repaired_faults(self) -> set[str]:
        return set(self._values("repaired", "fault"))

    def open_assignments(self) -> dict[str, str]:
        """
        crew -> fault it is currently committed to.

        Replays "assigned" posts in order; a later assignment for the same crew
        overwrites the earlier one, and a crew whose fault has been repaired is
        dropped.
        """
        done, out = self.repaired_faults(), {}
        for p in self._of_kind("assigned"):
            if p["fault"] not in done:
                out[p["crew"]] = p["fault"]
            else:
                out.pop(p["crew"], None)
        return out

    # ── what each agent sees of the other ──────────────────────
    # These two strings are the actual "messages" as the LLMs receive them.
    # Each is pasted into the prompt under "FROM THE BLACKBOARD".

    def brief_for_scout(self) -> str:
        """
        The controller's side of the board, rendered for the scout's prompt.
        Example:
            crews busy: RC1 on fault A, RC2 on fault C
            faults closed: B
            fault D needs BOTH crews (40 repair)
        """
        lines = []
        if assigned := self.open_assignments():
            lines.append("  crews busy: " + ", ".join(f"{c} on fault {f}" for c, f in assigned.items()))
        if done := sorted(self.repaired_faults()):
            lines.append(f"  faults closed: {', '.join(done)}")
        for p in self._of_kind("needs_both"):
            if p["fault"] not in self.repaired_faults():
                lines.append(f"  fault {p['fault']} needs BOTH crews ({p['needed']} repair)")
        return "\n".join(lines) or "  (controller has posted nothing yet)"

    def brief_for_controller(self) -> str:
        """
        The scout's side of the board, rendered for the controller's prompt.
        Example:
            fault B at [-4, -4] (found round 3)
            regions swept: CentralBlock, EastCorridor
            scout heading to [0, -16]
        Note "regions swept" includes regions the controller's own crews
        entered — explored posts come from both agents.
        """
        lines = [f"  fault {p['fault']} at {p['position']} (found round {p['step']})"
                 for p in self._of_kind("discovered")]
        if swept := sorted(self.explored_regions()):
            lines.append(f"  regions swept: {', '.join(swept)}")
        if heading := self._values("scouting", "target"):
            lines.append(f"  scout heading to {heading[-1]}")
        return "\n".join(lines) or "  (scout has found nothing yet)"

    # ── the round ──────────────────────────────────────────────
    def already_submitted(self) -> bool:
        """True if this agent's commands for the current round are already in."""
        self.sync()
        return self.me in self.data["pending"]

    def submit(self, commands: dict, seen_round: int) -> str:
        """
        Put this agent's commands (and buffered posts) on the board.

        Args:
            commands:   {unit_name: command} for the units this agent owns.
            seen_round: the round number the agent read BEFORE deciding. If the
                        round has moved on since, the decision is out of date
                        and is discarded.

        Returns one of:
            "flushed" — this submission completed the round; the batch was sent
                        to the simulator and the round number advanced
            "waiting" — stored; the other agent has not submitted yet
            "stale"   — round advanced while this agent was deciding; nothing
                        stored, the agent should loop and decide again
            "over"    — the game has ended

        Posts are stamped with `step` = the round being submitted.
        Note: on "stale" the post buffer is kept and goes out next submit.
        """
        with _Lock():
            data = _read()
            if data["over"]:
                return "over"
            if data["round"] != seen_round:
                return "stale"

            # 1. flush buffered posts into the shared log
            for post in self._buffer:
                data["posts"].append({"step": data["round"], **post})
                print(f"  [BB]   + [{data['round']:>2}] {post['author']:<10} "
                      f"{post['kind']:<10} "
                      + ", ".join(f"{k}={v}" for k, v in post.items()
                                  if k not in ("author", "kind")), flush=True)
            self._buffer.clear()

            # 2. record this agent's commands for the round
            data["pending"][self.me] = commands

            # 3. if every expected agent is in, this agent closes the round
            if set(data["pending"]) >= set(EXPECTED):
                merged = {}
                for agent_cmds in data["pending"].values():
                    merged.update(agent_cmds)   # units never overlap between agents
                print(f"  [BB]   round {data['round']} complete -> flushing", flush=True)
                sim_client.execute(merged)      # ONE tick for all units
                data["over"]    = sim_client.is_over(sim_client.get_state())
                data["round"]  += 1
                data["pending"] = {}
                _write(data)
                self.data = data
                return "flushed"

            _write(data)
            self.data = data
            return "waiting"

    def wait_for_next_round(self, seen_round: int, timeout: float = 180.0) -> bool:
        """
        Block until the other agent closes the round. False if the game ended.

        Polls the file every 0.3 s. Raises TimeoutError after `timeout` — the
        usual cause is that the other agent process is not running or crashed.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.sync()
            if self.data["over"]:
                return False
            if self.data["round"] != seen_round:
                return True
            time.sleep(0.3)
        raise TimeoutError(f"{self.me} waited too long for round {seen_round} to close")

    # ── record ─────────────────────────────────────────────────
    def dump(self) -> str:
        """Every post as one line — printed by both agents when they exit."""
        return "\n".join(
            f"[{p['step']:>2}] {p['author']:<10} {p['kind']:<10} "
            + ", ".join(f"{k}={v}" for k, v in p.items()
                        if k not in ("step", "author", "kind"))
            for p in self.data["posts"]
        )
