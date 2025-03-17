import os
import evdev
import json
from evdev import ecodes, InputDevice, categorize
import select

PROFILE_PATH = "/home/nadav/RealSim2.0/src/controller_profiles.json"

class USBRead:
    def __init__(self):
        print("USB init")
        self.scan_code_map = self.load_profiles()

    def load_profiles(self):
        """Load saved profiles or create an empty map."""
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, 'r') as file:
                print("✅ Profiles loaded successfully.")
                return json.load(file)
        print("⚠️ No profiles found. Starting fresh.")
        return {}

    def save_profiles(self):
        """Save the current scan code map to a JSON file."""
        with open(PROFILE_PATH, 'w') as file:
            json.dump(self.scan_code_map, file, indent=4)
        print("✅ Profile saved successfully.")

    def list_usb_devices(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        print("\nAvailable Devices:")
        for idx, device in enumerate(devices):
            print(f"{idx}: {device.name} ({device.path})")
        return devices

    def name_device_and_inputs(self):
        """Assign names to devices and their inputs."""
        devices = self.list_usb_devices()
        for device in devices:
            device_name = input(f"Enter a name for device '{device.name}': ")
            self.scan_code_map[device.path] = {"device_name": device_name, "inputs": {}}

            print(f"Now assign names for {device_name}'s inputs. Press the button or move the joystick to identify inputs.")
            for event in device.read_loop():
                if event.type in [ecodes.EV_ABS, ecodes.EV_KEY, ecodes.EV_REL]:
                    input_name = input(f"Detected code {event.code}. Enter a name for this input: ")
                    self.scan_code_map[device.path]["inputs"][str(event.code)] = input_name  # Fixed key as string for consistency
                    self.save_profiles()

    def get_values(self):
        """Return the latest values from all connected USB devices, including named devices and inputs."""
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        values = {}

        device_fds = {device.fd: device for device in devices}
        try:
            while True:
                r, _, _ = select.select(device_fds.keys(), [], [])
                for fd in r:
                    device = device_fds[fd]
                    for event in device.read():
                        if event.type in [ecodes.EV_ABS, ecodes.EV_KEY, ecodes.EV_REL]:
                            device_name = self.scan_code_map.get(device.path, {}).get("device_name", device.name)
                            input_name = self.scan_code_map.get(device.path, {}).get("inputs", {}).get(str(event.code), f"Code {event.code}")  # Fixed to match string keys
                            values[device_name] = {"input": input_name, "value": event.value}
                            print(f"Device: {device_name}, Input: {input_name}, Value: {event.value}")
        except KeyboardInterrupt:
            print("Exiting program.")

# Run the Code
usb_reader = USBRead()  # Create an instance of the class
usb_reader.name_device_and_inputs()  # Assign device and input names
usb_reader.get_values()  # Start reading inputs
