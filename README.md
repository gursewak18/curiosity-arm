# Curiosity Arm

Complete AI robotic arm learning project with one interactive dashboard, switchable full-space 2D and 3D views, autonomous AI-style control, hardware-ready Arduino communication, and robotics math tests.

## What Works Now

- Unified interactive dashboard with 2D/3D view switching
- 2-link robotic arm simulation
- 2D digital twin mode
- 3D digital twin mode
- AI autonomous controller demo
- Industrial workcell target cycle: inspect, pick, verify, place, standby
- Keyboard joint control
- Mouse target tracking
- Forward kinematics
- Inverse kinematics
- Joint limits
- Clean project architecture for AI and hardware stages
- Unit tests for core robotics math

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

If `pygame` is not installed yet, install it with:

```powershell
pip install pygame numpy
```

## Controls

| Key / Input | Action |
| --- | --- |
| Q / W | Rotate shoulder joint |
| A / S | Rotate elbow joint |
| Mouse click | Move arm endpoint toward target using inverse kinematics |
| SPACE | Toggle AI autonomous controller |
| TAB | Move to next AI workcell task |
| 1 / 2 | Switch between full 2D and full 3D workspace |
| Left / Right | Rotate 3D camera in 3D mode |
| R | Reset arm |
| ESC | Quit |

## Run Modes

```powershell
python main.py --mode 2d
python main.py --mode ai
python main.py --mode 3d
python main.py --mode 3d-ai
```

- `dashboard`: one interface with switchable full-space 2D/3D views, AI control, task status, and hardware simulation controls
- `2d`: manual 2D simulator with optional AI toggle
- `ai`: starts the 2D simulator with AI autonomy enabled
- `3d`: 3D digital twin view
- `3d-ai`: 3D digital twin with AI autonomy enabled

Smoke-test a mode without leaving the window open:

```powershell
python main.py --mode dashboard --frames 120
```

## Project Structure

```text
curiosity-arm/
|-- main.py
|-- config.py
|-- requirements.txt
|-- simulation/
|   |-- arm.py
|   |-- dashboard.py
|   |-- inverse_kinematics.py
|   |-- joints.py
|   |-- kinematics.py
|   |-- renderer.py
|   `-- renderer_3d.py
|-- controls/
|   `-- keyboard.py
|-- ai/
|   |-- arm_controller.py
|   |-- hand_tracking.py
|   |-- object_detection.py
|   `-- voice_control.py
|-- hardware/
|   |-- arduino_controller.py
|   |-- serial_communication.py
|   `-- servo_manager.py
|-- docs/
|-- assets/
|-- datasets/
`-- tests/
```

## Development

Run tests:

```powershell
python -m unittest discover tests
```

## Version Plan

1. Keyboard robotic arm
2. Mouse tracking
3. Inverse kinematics
4. Hand tracking AI
5. Object detection AI
6. Real hardware integration
7. Autonomous AI robotics
