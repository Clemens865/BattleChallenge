"""Outcome-based tests for task-104: Finite state machine compiler."""
import importlib.util
import os
import sys
import tempfile
import textwrap
import time
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())


def _load_module(name, filename=None):
    filename = filename or f"{name}.py"
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"{filename} not found in {OUTPUT_DIR}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # Add OUTPUT_DIR to sys.path so compiler can import runtime
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def compiler():
    return _load_module("compiler")


@pytest.fixture(scope="module")
def runtime():
    return _load_module("runtime")


# ===========================================================================
# Helper: compile DSL and load the generated class
# ===========================================================================

def _compile_and_load(compiler_mod, source: str, class_name: str = None):
    """Compile DSL source, exec the generated code, return the SM class."""
    code = compiler_mod.compile(source)
    assert isinstance(code, str) and len(code) > 0, "Compiler returned empty code"
    ns = {}
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    exec(code, ns)
    if class_name:
        assert class_name in ns, f"Generated code does not define {class_name}"
        return ns[class_name]
    # Find the first class that's a subclass of StateMachine
    runtime_mod = _load_module("runtime")
    for val in ns.values():
        if isinstance(val, type) and issubclass(val, runtime_mod.StateMachine) and val is not runtime_mod.StateMachine:
            return val
    pytest.fail("No StateMachine subclass found in generated code")


# ===========================================================================
# SECTION 1: File existence (4 tests)
# ===========================================================================

REQUIRED_FILES = ["compiler.py", "runtime.py", "examples/turnstile.fsm", "examples/traffic_light.fsm"]


@pytest.mark.parametrize("filepath", REQUIRED_FILES)
def test_file_exists(filepath):
    path = os.path.join(OUTPUT_DIR, filepath)
    assert os.path.isfile(path), f"{filepath} not found"


@pytest.mark.parametrize("filepath", ["compiler.py", "runtime.py"])
def test_file_min_lines(filepath):
    path = os.path.join(OUTPUT_DIR, filepath)
    if not os.path.isfile(path):
        pytest.skip(f"{filepath} not found")
    with open(path) as f:
        lines = f.readlines()
    assert len(lines) >= 10, f"{filepath} has only {len(lines)} lines"


# ===========================================================================
# SECTION 2: Compiler API (4 tests)
# ===========================================================================

def test_compiler_has_parse(compiler):
    assert callable(getattr(compiler, "parse", None))


def test_compiler_has_compile(compiler):
    assert callable(getattr(compiler, "compile", None))


def test_compiler_has_compile_file(compiler):
    assert callable(getattr(compiler, "compile_file", None))


def test_parse_returns_dict(compiler):
    source = textwrap.dedent("""\
    machine Simple {
      initial A
      state A { on go -> B }
      state B { on back -> A }
    }
    """)
    result = compiler.parse(source)
    assert isinstance(result, dict)


# ===========================================================================
# SECTION 3: Runtime API (4 tests)
# ===========================================================================

def test_runtime_has_statemachine(runtime):
    assert hasattr(runtime, "StateMachine")


def test_runtime_current_state(runtime):
    assert hasattr(runtime.StateMachine, "current_state") or "current_state" in dir(runtime.StateMachine)


def test_runtime_send_method(runtime):
    assert callable(getattr(runtime.StateMachine, "send", None))


def test_runtime_history(runtime):
    assert hasattr(runtime.StateMachine, "history") or "history" in dir(runtime.StateMachine)


# ===========================================================================
# SECTION 4: Turnstile example (5 tests)
# ===========================================================================

TURNSTILE_DSL = textwrap.dedent("""\
machine Turnstile {
  initial Locked

  state Locked {
    on coin -> Unlocked / ring_bell
    on push -> Locked / sound_alarm
  }

  state Unlocked {
    on coin -> Unlocked / refund
    on push -> Locked
  }
}
""")


def test_turnstile_initial_state(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    assert sm.current_state == "Locked"


def test_turnstile_coin_unlocks(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    sm.send("coin")
    assert sm.current_state == "Unlocked"


def test_turnstile_push_stays_locked(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    sm.send("push")
    assert sm.current_state == "Locked"


def test_turnstile_full_cycle(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    sm.send("coin")
    assert sm.current_state == "Unlocked"
    sm.send("push")
    assert sm.current_state == "Locked"


def test_turnstile_double_coin(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    sm.send("coin")
    sm.send("coin")
    assert sm.current_state == "Unlocked"


# ===========================================================================
# SECTION 5: Traffic light example (3 tests)
# ===========================================================================

TRAFFIC_DSL = textwrap.dedent("""\
machine TrafficLight {
  initial Red

  state Red {
    on timer -> Green
    on emergency -> Red / activate_siren
  }

  state Green {
    on timer -> Yellow
    on emergency -> Red / activate_siren
  }

  state Yellow {
    on timer -> Red
    on emergency -> Red / activate_siren
  }
}
""")


def test_traffic_full_cycle(compiler):
    cls = _compile_and_load(compiler, TRAFFIC_DSL)
    sm = cls()
    assert sm.current_state == "Red"
    sm.send("timer")
    assert sm.current_state == "Green"
    sm.send("timer")
    assert sm.current_state == "Yellow"
    sm.send("timer")
    assert sm.current_state == "Red"


def test_traffic_emergency_from_green(compiler):
    cls = _compile_and_load(compiler, TRAFFIC_DSL)
    sm = cls()
    sm.send("timer")  # Red -> Green
    sm.send("emergency")
    assert sm.current_state == "Red"


def test_traffic_history(compiler):
    cls = _compile_and_load(compiler, TRAFFIC_DSL)
    sm = cls()
    sm.send("timer")
    sm.send("timer")
    assert len(sm.history) >= 2


# ===========================================================================
# SECTION 6: Guards (4 tests)
# ===========================================================================

GUARD_DSL = textwrap.dedent("""\
machine Guarded {
  initial Idle

  state Idle {
    on submit [is_valid] -> Processing
    on submit [is_invalid] -> Error
  }

  state Processing {
    on done -> Idle
  }

  state Error {
    on retry -> Idle
  }
}
""")


def test_guard_parse(compiler):
    result = compiler.parse(GUARD_DSL)
    assert isinstance(result, dict)


def test_guard_compile(compiler):
    code = compiler.compile(GUARD_DSL)
    assert "is_valid" in code
    assert "is_invalid" in code


def test_guard_first_match_wins(compiler):
    cls = _compile_and_load(compiler, GUARD_DSL)
    sm = cls()
    # Override guard: is_valid returns True
    sm.is_valid = lambda **kwargs: True
    sm.is_invalid = lambda **kwargs: False
    sm.send("submit")
    assert sm.current_state == "Processing"


def test_guard_second_match(compiler):
    cls = _compile_and_load(compiler, GUARD_DSL)
    sm = cls()
    sm.is_valid = lambda **kwargs: False
    sm.is_invalid = lambda **kwargs: True
    sm.send("submit")
    assert sm.current_state == "Error"


# ===========================================================================
# SECTION 7: Actions (3 tests)
# ===========================================================================

def test_action_called(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    called = []
    sm.ring_bell = lambda **kwargs: called.append("ring_bell")
    sm.send("coin")
    assert "ring_bell" in called


def test_action_sound_alarm(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    called = []
    sm.sound_alarm = lambda **kwargs: called.append("sound_alarm")
    sm.send("push")
    assert "sound_alarm" in called


def test_action_refund(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    sm.send("coin")
    called = []
    sm.refund = lambda **kwargs: called.append("refund")
    sm.send("coin")
    assert "refund" in called


# ===========================================================================
# SECTION 8: Reset and can_send (3 tests)
# ===========================================================================

def test_reset(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    sm.send("coin")
    assert sm.current_state == "Unlocked"
    sm.reset()
    assert sm.current_state == "Locked"


def test_can_send_valid(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    assert sm.can_send("coin") is True
    assert sm.can_send("push") is True


def test_can_send_invalid(compiler):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    assert sm.can_send("nonexistent_event") is False


# ===========================================================================
# SECTION 9: Enter/exit callbacks (3 tests)
# ===========================================================================

def test_on_enter_callback(compiler, runtime):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    entered = []
    sm.on_enter("Unlocked", lambda: entered.append("entered_unlocked"))
    sm.send("coin")
    assert "entered_unlocked" in entered


def test_on_exit_callback(compiler, runtime):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    exited = []
    sm.on_exit("Locked", lambda: exited.append("exited_locked"))
    sm.send("coin")
    assert "exited_locked" in exited


def test_on_transition_callback(compiler, runtime):
    cls = _compile_and_load(compiler, TURNSTILE_DSL)
    sm = cls()
    transitions = []
    sm.on_transition(lambda src, evt, dst: transitions.append((src, evt, dst)))
    sm.send("coin")
    assert len(transitions) == 1
    assert transitions[0] == ("Locked", "coin", "Unlocked")


# ===========================================================================
# SECTION 10: Syntax errors (3 tests)
# ===========================================================================

def test_syntax_error_no_initial(compiler):
    bad = "machine Bad { state A { on go -> B } state B { on back -> A } }"
    with pytest.raises(Exception) as exc_info:
        compiler.compile(bad)
    assert "initial" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()


def test_syntax_error_invalid_transition(compiler):
    bad = textwrap.dedent("""\
    machine Bad {
      initial A
      state A { on -> B }
    }
    """)
    with pytest.raises(Exception):
        compiler.compile(bad)


def test_syntax_error_missing_brace(compiler):
    bad = textwrap.dedent("""\
    machine Bad {
      initial A
      state A { on go -> B
    """)
    with pytest.raises(Exception):
        compiler.compile(bad)


# ===========================================================================
# SECTION 11: Generated code quality (2 tests)
# ===========================================================================

def test_generated_code_is_valid_python(compiler):
    code = compiler.compile(TURNSTILE_DSL)
    # Should be compilable
    compile(code, "<test>", "exec")


def test_generated_code_has_comments_or_docstrings(compiler):
    code = compiler.compile(TURNSTILE_DSL)
    assert "#" in code or '"""' in code or "'''" in code, "Generated code should have comments or docstrings"


# ===========================================================================
# SECTION 12: compile_file (1 test)
# ===========================================================================

def test_compile_file(compiler):
    turnstile_path = os.path.join(OUTPUT_DIR, "examples", "turnstile.fsm")
    if not os.path.isfile(turnstile_path):
        pytest.skip("examples/turnstile.fsm not found")
    code = compiler.compile_file(turnstile_path)
    assert isinstance(code, str) and len(code) > 0
    compile(code, "<test>", "exec")
