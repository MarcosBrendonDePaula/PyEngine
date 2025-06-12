# State Machine and Timer Demo

This example demonstrates the usage of the `StateMachineComponent` and `TimerComponent`.

## How to Run

From the `PyEngine` root directory, run:

```bash
python3 examples/state_timer_demo/state_timer_demo_main.py
```

## Controls

- **W, A, S, D:** Move the red square.
- **Spacebar:** Make the square attack (turns blue) and enter a cooldown period. During cooldown, it cannot attack again and will return to the 'idle' (red) state after the timer expires.


