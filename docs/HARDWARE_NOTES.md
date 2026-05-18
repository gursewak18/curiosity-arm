# Hardware Notes

Start hardware slowly and safely.

## First Hardware Goal

Move one servo from Python through Arduino.

## Suggested Parts

- Arduino UNO or compatible board
- 2 or more servo motors
- External 5V servo power supply
- Breadboard
- Jumper wires
- Robotic arm frame

## Important Safety Notes

- Do not power multiple servos directly from the Arduino 5V pin.
- Use a separate servo power supply.
- Connect Arduino ground and servo power ground together.
- Test one servo before connecting the full arm.

## Python to Arduino Command Format

The current Python hardware layer sends commands like:

```text
S:90;E:120
```

Where:

- `S` is shoulder angle
- `E` is elbow angle

