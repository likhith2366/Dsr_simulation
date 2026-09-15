"""
sim_client.py — every HTTP call to the DSR simulator goes through here.

The simulator (../simulator_web_v23.py) is a FastAPI server on port 8050.
The agents never import simulator code; they only use its REST API:

    GET  /api/text/state     full world state as JSON
    POST /api/load           load the fault scenario (starts a game)
    POST /api/text/execute   advance ONE time step with a batch of commands
    POST /api/shutdown       stop the server

Things about the simulator that are not obvious and cost us debugging time
are documented at the function they affect. Summary:
  1. The "case" field sent to /api/load is IGNORED. The simulator always reads
     scenario files from cases/case1/. To change the scenario, edit case1.
  2. Hidden regions must be passed explicitly on load (see case_unknown_regions).
  3. A unit that is busy accepts only "continue" (see forced_cmd).
  4. There is no "Success" status. The game is scored, not won (see is_over).
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import requests

SIM_URL   = "http://127.0.0.1:8050"
SIM_DIR   = Path(__file__).resolve().parent.parent   # .../reference_simulator
CASE      = "case1"                                  # see note 1 above

# Number of time steps before the game ends. The simulator's own default is 20.
# We raised it because the crews now start far north and ~20 steps cannot fit
# the travel plus the repairs. Raise it further if you make the map bigger.
MAX_STEPS = 40


# ════════════════════════════════════════════════ server lifecycle

def is_up() -> bool:
    """True if something is answering on the simulator port."""
    try:
        return requests.get(f"{SIM_URL}/api/text/state", timeout=3).status_code == 200
    except requests.exceptions.RequestException:
        return False


def ensure_running(retries: int = 20, delay: float = 1.5) -> bool:
    """
    Start the simulator if it is not already running. Returns True once it answers.

    It is started DETACHED on Windows so that it survives the agent process
    that launched it — both agents need it, and either may exit first.
    Consequence: nothing stops it automatically. Kill it yourself, or call
    shutdown(), or free the port with:
        Get-NetTCPConnection -LocalPort 8050 | % { Stop-Process -Id $_.OwningProcess }
    Its stdout/stderr go to agents/sim_stderr.log.
    """
    if is_up():
        return True

    print("[SIM] starting simulator...", flush=True)
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008  # DETACHED_PROCESS
    log = open(SIM_DIR / "agents" / "sim_stderr.log", "w")
    subprocess.Popen(
        [sys.executable, "simulator_web_v23.py"],
        cwd=str(SIM_DIR), stdout=log, stderr=log, creationflags=flags,
    )
    for i in range(retries):
        if is_up():
            return True
        print(f"[SIM]   waiting... ({i+1}/{retries})", flush=True)
        time.sleep(delay)
    return False


def shutdown() -> None:
    """Ask the simulator to exit. Silently ignores it if already down."""
    try:
        requests.post(f"{SIM_URL}/api/shutdown", timeout=5)
    except requests.exceptions.RequestException:
        pass


# ════════════════════════════════════════════════ scenario loading

def case_unknown_regions(case: str = CASE) -> list[dict]:
    """
    Read the hidden ("unknown") regions from cases/<case>/UnknownState_v1.json.

    SIMULATOR QUIRK — why we read this file ourselves:
    Most scenario files are found through a search path that includes
    cases/case1/. The unknown-region loader does NOT use that path; it reads
    reference_simulator/UnknownState_v1.json at the root, which does not exist.
    So if /api/load is called without regions, the simulator silently uses []
    and NOTHING is hidden — every fault is visible from step 1 and the scout
    has no purpose. (Symptom: the agents print "[MAP] 0 hidden regions".)
    Passing the regions explicitly on load fixes it.

    Also note: sending "unknown_regions": [] explicitly also reveals everything.
    """
    path = SIM_DIR / "cases" / case / "UnknownState_v1.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("unknown_regions", [])


def load_case(case: str = CASE, max_time_step: int = MAX_STEPS) -> str:
    """
    Load the fault scenario: resets faults, units, score, and applies hidden regions.
    Called exactly once per run, by whichever agent boots first (blackboard.py).
    """
    regions = case_unknown_regions(case)
    body    = {"case": case, "unknown_regions": regions, "max_time_step": max_time_step}
    print(f"[SIM] loading {case} with {len(regions)} hidden regions, "
          f"{max_time_step} step limit", flush=True)
    r = requests.post(f"{SIM_URL}/api/load", json=body, timeout=10)
    r.raise_for_status()
    return r.json().get("message", "")


# ════════════════════════════════════════════════ reading state

def get_state() -> dict:
    """
    Full world state. The keys the agents use:

      state["objects"]["RC1" | "RC2" | "PAC1" | "MPS1"]
          position, state (Idle/Moving/Analyzing/Repairing), move_speed,
          inspection_range, remaining_resources (RC only), repair_speed (RC),
          repairable_faults: [{name, maximum_amount}]  <- what it can repair
                                                          RIGHT NOW, from where
                                                          it stands
      state["faults"]
          ONLY faults already discovered. Undiscovered faults are filtered out
          by the simulator entirely, so "a fault is in this list" means
          "someone has inspected it". Fields: name, position, active
          (False once fully repaired), remaining_repair_resource (None until a
          crew has analyzed it).
      state["unknown_regions"]   the hidden rectangles loaded at start
      state["switches"]          S1..S8, "opened"/"closed". NOT USED YET.
      state["game"]              status, score, current_power, power_history
    """
    r = requests.get(f"{SIM_URL}/api/text/state", timeout=10)
    r.raise_for_status()
    return r.json()


def hidden_regions() -> list[dict]:
    """The hidden rectangles as the simulator reports them after load."""
    return get_state().get("unknown_regions", [])


def status(state: dict) -> str:
    return state.get("game", {}).get("status", "ongoing")


def is_over(state: dict) -> bool:
    """
    True when the game has ended.

    IMPORTANT: the simulator only ever reports Ready, Running,
    "Score locked at zero", or Completed. There is NO "Success" state —
    "success"/"failure" below are checked for safety but never occur.
    "Completed" is the normal ending: the step limit was reached.
    A run is judged by state["game"]["score"], not by status.
    """
    return status(state).lower() in ("success", "failure", "completed")


def summary(state: dict) -> str:
    """One-line JSON snapshot for the round header in the agent logs."""
    objs = state["objects"]
    return json.dumps({
        "status":  status(state),
        "visible": [f["name"] for f in state.get("faults", [])],
        "PAC1":    objs["PAC1"]["position"],
        "RC1":     {k: objs["RC1"][k] for k in ("position", "state", "remaining_resources")},
        "RC2":     {k: objs["RC2"][k] for k in ("position", "state", "remaining_resources")},
    })


# ════════════════════════════════════════════════ acting

def execute(commands: dict) -> dict:
    """
    Advance the simulator by exactly ONE time step.

    `commands` maps unit name to command, e.g.
        {"PAC1": {"type": "move", "waypoints": [[-4, -6]]},
         "RC1":  {"type": "repair", "fault": "A", "amount": 5},
         "RC2":  {"type": "continue"}}
    Units left out default to "continue".

    Every call is a clock tick. That is why the blackboard batches all agents'
    commands into ONE call per round — two separate calls would cost two steps.

    If ANY command in the batch is illegal the whole batch is rejected
    (HTTP 400) and the clock does NOT advance. Repeating the same bad command
    therefore deadlocks the run; see forced_cmd and rc_agent.clamp_repair.

    NOT SENT YET: the API also accepts a top-level "switch_commands" key,
    e.g. {"S1": "closed"}. Switches are what actually restore power (and score).
    No agent issues them, which is why every run so far scored 0.
    """
    body = {"mobile_commands": commands}
    print(f"  [SIM]  POST {json.dumps(body)}", flush=True)
    r    = requests.post(f"{SIM_URL}/api/text/execute", json=body, timeout=10)
    resp = r.json() if r.ok else {"ok": False, "message": f"HTTP {r.status_code}: {r.text[:200]}"}
    print(f"  [SIM]  -> ok={resp.get('ok')} {resp.get('message','')[:100]}", flush=True)
    return resp


def forced_cmd(unit: dict) -> dict | None:
    """
    Return {"type": "continue"} if the unit is busy, otherwise None.

    A unit that is Moving, Analyzing or Repairing accepts ONLY "continue".
    Anything else gets the whole batch rejected (see execute).

    Watch out for "Analyzing": a unit locks into it automatically for one step
    the instant it comes within inspection range of an undiscovered fault —
    including mid-journey. PAC1 hit this: the scout sent it a move while it
    was analyzing, and the run deadlocked.

    When this returns a command there is no decision to make, so the agents
    skip the LLM call entirely.
    """
    if unit.get("state") in ("Moving", "Analyzing", "Repairing"):
        return {"type": "continue"}
    return None
