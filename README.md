# RealSim

RealSim is a Python-based hardware interaction project designed to run on a Raspberry Pi. It combines three main capabilities:

- reading input events from USB devices such as keyboards, mice, and controllers
- displaying status and messages on a small OLED screen
- generating output signals for external hardware using GPIO

The project appears to be an experiment or prototype for simulating or bridging real-world controller input into hardware-level signal output.

## Features

- Detects and lists connected USB input devices using `evdev`
- Maps raw device event codes to human-readable input names through configurable controller profiles
- Filters input from a specific device and selected buttons or controls
- Displays startup, runtime, and input messages on a 128x64 OLED display over I2C
- Generates hardware output signals using Raspberry Pi GPIO with `pigpio`
- Includes support for:
  - PPM signal generation for RC-style receivers
  - basic Crossfire/CRSF-style frame generation

## How It Works

The main entry point is `RealSim.py`.

On startup, the application:

1. initializes the OLED display
2. initializes the signal generator on GPIO pin `18`
3. initializes USB input handling
4. shows a startup message on the display
5. lists available USB devices
6. continuously listens for specific inputs from the device named `Microsoft Wired Keyboard 400`

When one of the configured inputs (`A`, `B`, or `Enter`) is detected, the app prints the event and shows it on the OLED display.

## Repository Structure

```text
.
├── RealSim.py                  # Main application loop
├── sync-to-pi.sh               # Helper script to sync the project to a Raspberry Pi
└── src/
    ├── Display.py              # OLED display wrapper
    ├── USB_Read.py             # USB input discovery, mapping, and filtering
    ├── signal_generator.py     # GPIO-based signal generation
    └── controller_profiles.json# Saved device/input name mappings
```

## Components

### `RealSim.py`
Creates and connects the main runtime components:

- `Display()` for OLED output
- `SignalGenerator(18)` for GPIO signal generation
- `USBRead()` for device scanning and event reading

It currently monitors a keyboard named `Microsoft Wired Keyboard 400` and listens for:

- `A`
- `B`
- `Enter`

### `src/Display.py`
Wraps an SSD1306 OLED display connected over I2C.

Responsibilities:
- initialize the display using `adafruit_ssd1306`, `board`, and `busio`
- render text messages using Pillow
- clear the display when shutting down

### `src/USB_Read.py`
Handles USB device input using Linux input events via `evdev`.

Responsibilities:
- list available input devices
- load and save controller/input mappings from `controller_profiles.json`
- prompt for naming devices and raw input codes when an unknown device is encountered
- read non-blocking events from devices
- filter for specific named inputs from a target device

### `src/signal_generator.py`
Uses `pigpio` to drive GPIO output.

Implemented signal methods:
- `generate_ppm(...)` for pulse-position modulation style output
- `generate_crossfire(...)` for a simple Crossfire/CRSF-like byte stream

### `src/controller_profiles.json`
Stores saved mappings between Linux event device paths, device names, and input code labels.

Example mapped devices include:
- a mouse (`HP150`)
- a PS4 controller
- a Microsoft keyboard

## Requirements

This project is intended for Linux, likely a Raspberry Pi environment, because it depends on:

- GPIO access
- I2C hardware access
- Linux input event devices in `/dev/input`

Python dependencies inferred from the code:

```bash
pip install evdev pigpio pillow adafruit-circuitpython-ssd1306
```

You may also need system-level support for:

- `pigpio` daemon or library setup
- I2C enabled on the Raspberry Pi
- permissions to access `/dev/input/event*`

## Running the Project

Activate your virtual environment if you use one:

```bash
source .venv/bin/activate
```

Run the main program:

```bash
python RealSim.py
```

## Notes

- `USB_Read.py` currently uses an absolute profile path:
  `/home/nadav/RealSim2.0/src/controller_profiles.json`
  
  If you run the project from a different location, this path may need to be updated.

- `sync-to-pi.sh` is tailored to the original developer environment and Raspberry Pi IP/path.

- The signal generator is initialized in the main script, but signal output is not yet actively driven by the detected keyboard inputs.

## Possible Next Improvements

- make paths relative instead of absolute
- add a `requirements.txt`
- document hardware wiring for the OLED and GPIO output pin
- connect USB input events to generated output signals
- add structured logging and configuration
- add support for multiple controller profiles and device auto-detection

## License

No license is currently specified in this repository.
