## Setup and Run

Prerequisites

- Python 3.9+
- Webcam

Create virtual environment

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
```

Install dependencies

```bash
pip install -r requirements.txt
```

Optional: place sounds

- Put `correct.wav` and `fail.wav` in `assets/sounds/`.

Run

```bash
python main.py
```

Notes

- Camera is mirrored in `core/camera_handler.py`. UI must not flip/rotate frames.
- If you see absl/protobuf warnings, they are suppressed in `main.py`.
