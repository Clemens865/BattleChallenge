# Task 104: Finite State Machine Compiler

## Objective

Implement a compiler that reads a custom DSL for finite state machines and generates executable Python code, plus a runtime library to execute the generated machines.

## Required Output Files

### 1. `compiler.py`
A module that provides:
- `parse(source: str) -> dict` — Parse DSL source into an AST (dict structure)
- `compile(source: str) -> str` — Compile DSL source into executable Python code
- `compile_file(path: str) -> str` — Read a .fsm file and compile it

The compiler must handle syntax errors gracefully with clear error messages including line numbers.

### 2. `runtime.py`
A module that provides:
- `StateMachine` base class with:
  - `current_state` property
  - `send(event, **context)` method — send an event, trigger transition
  - `can_send(event)` method — check if event is valid in current state
  - `reset()` method — return to initial state
  - `history` property — list of (state, event, new_state) tuples
  - `on_enter(state, callback)` — register enter callback
  - `on_exit(state, callback)` — register exit callback
  - `on_transition(callback)` — register global transition callback

### 3. `examples/turnstile.fsm`
```
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
```

### 4. `examples/traffic_light.fsm`
```
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
```

## DSL Specification

### Basic syntax
```
machine MachineName {
  initial StateName

  state StateName {
    on event_name -> TargetState
    on event_name -> TargetState / action_name
    on event_name [guard_func] -> TargetState / action_name
  }
}
```

### Features the compiler MUST support

1. **Basic transitions**: `on event -> State`
2. **Actions**: `on event -> State / action_name` (action is called during transition)
3. **Guards**: `on event [guard_name] -> State` (transition only if guard returns True)
4. **Multiple guards**: Same event can have multiple transitions with different guards (first matching wins)
5. **Nested states**: States can contain sub-states with their own transitions
   ```
   state Active {
     initial Running
     state Running { on pause -> Paused }
     state Paused { on resume -> Running }
     on stop -> Inactive  # applies to all sub-states
   }
   ```
6. **Timeout transitions**: `after 5s -> State` (auto-transition after duration)
7. **Entry/exit actions**: `entry / action_name` and `exit / action_name` within state blocks

### Generated code requirements
- The generated Python code must define a class that extends `StateMachine` from `runtime.py`
- The generated code must be valid, importable Python
- Actions and guards are method stubs that can be overridden

## Constraints

- No external dependencies
- Compiler must report meaningful syntax errors with line numbers
- Generated code must be human-readable (proper indentation, comments)
- Each file must be at least 10 lines

## Scoring

**Binary**: ALL tests must pass or score is 0. Tests cover:
- Parsing valid DSL files
- Syntax error reporting
- Code generation and execution
- State transitions with actions
- Guard conditions
- Nested states
- Timeout transitions
- History tracking
- Enter/exit callbacks
- Generated code importability
- Invalid event handling (should raise or return False)
