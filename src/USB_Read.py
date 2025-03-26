import os
import evdev
import json
import select
import fcntl
from evdev import ecodes, InputDevice

PROFILE_PATH = "/home/nadav/RealSim2.0/src/controller_profiles.json"

class USBRead:
    def __init__(self):
        print("USB init")
        self.scan_code_map = self.load_profiles()

    def load_profiles(self):
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, 'r') as file:
                print("✅ Profiles loaded successfully.")
                return json.load(file)
        print("⚠️ No profiles found. Starting fresh.")
        return {}

    def save_profiles(self):
        with open(PROFILE_PATH, 'w') as file:
            json.dump(self.scan_code_map, file, indent=4)
        print("✅ Profile saved successfully.")

    def list_usb_devices(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        print("\nAvailable Devices:")
        for idx, device in enumerate(devices):
            print(f"{idx}: {device.name} ({device.path})")
        return devices

    def name_device_and_inputs(self, device):
        device_name = input(f"Enter a name for device '{device.name}': ")
        self.scan_code_map[device.path] = {"device_name": device_name, "inputs": {}}

        print(f"Now assign names for {device_name}'s inputs. Press the button or move the joystick to identify inputs.")
        for event in device.read_loop():
            if event.type in [ecodes.EV_ABS, ecodes.EV_KEY, ecodes.EV_REL]:
                input_name = input(f"Detected code {event.code}. Enter a name for this input: ")
                self.scan_code_map[device.path]["inputs"][str(event.code)] = input_name
                self.save_profiles()
            elif event.type == ecodes.EV_SYN:
                continue

    def get_values(self, target_device_name=None, target_input_name=None):
        print("Reading USB devices...")
        values = {}

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        for device in devices:
            if target_device_name and device.name != target_device_name:
                continue

            try:
                device.grab()
                fd_flags = fcntl.fcntl(device.fd, fcntl.F_GETFL)
                fcntl.fcntl(device.fd, fcntl.F_SETFL, fd_flags | os.O_NONBLOCK)

                if device.path not in self.scan_code_map:
                    self.name_device_and_inputs(device)

                try:
                    for event in device.read():
                        if event.type in [ecodes.EV_ABS, ecodes.EV_KEY, ecodes.EV_REL]:
                            device_name = self.scan_code_map.get(device.path, {}).get("device_name", device.name)
                            input_name = self.scan_code_map.get(device.path, {}).get("inputs", {}).get(
                                str(event.code), f"Code {event.code}"
                            )

                            if (target_input_name is None or input_name == target_input_name):
                                values.setdefault(device_name, []).append({"input": input_name, "value": event.value})
                                print(f"Device: {device_name}, Input: {input_name}, Value: {event.value}")

                except BlockingIOError:
                    continue
                except Exception as e:
                    print(f"⚠️ Read error from {device.path}: {e}")
                finally:
                    try:
                        device.ungrab()
                    except Exception:
                        pass

            except Exception as e:
                print(f"❌ Couldn't grab or configure device {device.path}: {e}")

        if not values:
            print("⚠️ No matching input detected.")
        return values

    def get_filtered_input(self, target_device_name, target_input_names):
        if isinstance(target_input_names, str):
            target_input_names = [target_input_names]

        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            if device.name == target_device_name:
                try:
                    device.grab()
                    print(f"🔒 Grabbed device {path}")

                    fd_flags = fcntl.fcntl(device.fd, fcntl.F_GETFL)
                    fcntl.fcntl(device.fd, fcntl.F_SETFL, fd_flags | os.O_NONBLOCK)

                    if device.path not in self.scan_code_map:
                        self.name_device_and_inputs(device)
                        print("🔧 Device named and inputs assigned.")

                    try:
                        for event in device.read():
#                            print(f"Raw event: code={event.code}, value={event.value}")
                            if event.type in [ecodes.EV_ABS, ecodes.EV_KEY, ecodes.EV_REL]:
        #                        print(f"Event: code={event.code}, value={event.value}")
                                input_name = self.scan_code_map.get(device.path, {}).get("inputs", {}).get(
                                    str(event.code), f"Code {event.code}"
                                )
                                if input_name in target_input_names:
                                    print(f"Input name detected: '{input_name}' — target: {target_input_names}")
                                    return {"input": input_name, "value": event.value}

                    except BlockingIOError:
                        pass
                    except Exception as e:
                        print(f"❌ Error reading device: {e}")
                    finally:
                        try:
                            device.ungrab()
                        except:
                            pass
                except Exception as e:
                    print(f"❌ Couldn't grab device {path}: {e}")
#        print("⚠️ No matching input detected.")
        return None


if __name__ == "__main__":
    usb_reader = USBRead()
    usb_reader.get_values("Microsoft Wired Keyboard", "A")
