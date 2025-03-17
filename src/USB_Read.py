import os
import evdev
import json
from evdev import ecodes, InputDevice, categorize

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

    def select_device(self, devices):
        """Prompt user to choose a device from the list."""
        while True:
            try:
                selected_index = int(input("\nSelect a device number from the list: "))
                if 0 <= selected_index < len(devices):
                    print(f"✅ Selected: {devices[selected_index].name}")
                    return devices[selected_index]
                else:
                    print("❌ Invalid selection. Try again.")
            except ValueError:
                print("❌ Please enter a valid number.")

    def read_controller(self):
        devices = self.list_usb_devices()
        if not devices:
            print("❌ No devices found. Try reconnecting or pressing a button.")
            return

        device = self.select_device(devices)
        device_name = device.name  # Unique identifier for profiles

        # Create an empty profile if none exists for this device
        if device_name not in self.scan_code_map:
            self.scan_code_map[device_name] = {}

        print(f"\nReading data from {device.name}...")

        for event in device.read_loop():
            if event.type == ecodes.EV_MSC and event.code == ecodes.MSC_SCAN:
                scan_code = str(event.value)  # Ensure scan code is treated as string

                # Check if the scan code is already labeled
                if scan_code in self.scan_code_map[device_name]:
                    print(f"{self.scan_code_map[device_name][scan_code]}: Pressed")
                else:
                    # Assign a label for unknown scan codes
                    label = input(f"\nDetected Scan Code {scan_code}. Enter a label (e.g., 'Button A'): ")
                    self.scan_code_map[device_name][scan_code] = label
                    print(f"✅ Assigned: {scan_code} -> {label}")
                    self.save_profiles()

            # Detect EV_KEY (important for PS5 buttons)
            elif event.type == ecodes.EV_KEY:
                key_state = "Pressed" if event.value == 1 else "Released"
                print(f"Button Code {event.code}: {key_state}")

# Run the Code
usb_reader = USBRead()  # Create an instance of the class
usb_reader.read_controller()  # Start reading inputs
