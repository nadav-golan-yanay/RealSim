#Vrtual Envrioment:
#source .venv/bin/activate

import os
import time
from src.Display import Display  # Import the new display class
from src.signal_generator import SignalGenerator  # Import the new display class
print("Imports complete.")
from src.USB_Read import USBRead

# Display Setup
display = Display()
print("Display initialized.")

sigGen = SignalGenerator(18)
print("Signal Generator initialized.")

USB = USBRead()
print("USB initialized.")

display.show_message("RealSim Starting...")


if __name__ == "__main__":
    try:
        display.show_message("RealSim Running!")
        print("RealSim is running...")
        USB.list_usb_devices()
        display.show_message(f"USB Devices:\n{USB.list_usb_devices()}", duration=3)
        counter = 0  # Counter to reduce print frequency
        while True:
            if counter % 10 == 0:  # Print less frequently for SSH stability
                print("RealSim is running...")

            result = USB.get_filtered_input("Microsoft Wired Keyboard 400", ["A", "B", "Enter"])
            if result:
                print(f"🎯 Got input: {result}")
                display.show_message(f"Got input: {result}", duration=1)

            counter += 1
#            time.sleep(0.5)  # Reduce CPU load by lowering the loop frequency

    except KeyboardInterrupt:
        print("Shutting down RealSim...")
        display.show_message("Shutting Down...")

    except Exception as e:
        print(f"Unexpected Error: {e}")
        display.show_message("Error Detected", duration=3)

    finally:
        display.clear_display()
        print("Cleanup complete. Goodbye!")
