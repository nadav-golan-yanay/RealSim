import pigpio
import time

class SignalGenerator:
    def __init__(self, pin):
        self.pi = pigpio.pi()  # Initialize pigpio library
        self.pin = pin
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

        print("Signal Generator init")

    def generate_ppm(self, channel_values, frame_length=22500):
        """
        Generate a PPM signal for RC receivers.
        :param channel_values: List of pulse widths (e.g., [1500, 1500, 1000, 2000])
        :param frame_length: Total frame length in microseconds (default 22.5ms)
        """
        sync_pulse = 300
        total_pulse_width = sync_pulse

        for pulse in channel_values:
            self.pi.gpio_write(self.pin, 1)
            self.pi.gpio_trigger(self.pin, pulse)
            total_pulse_width += pulse

            self.pi.gpio_write(self.pin, 0)
            self.pi.gpio_trigger(self.pin, sync_pulse)
            total_pulse_width += sync_pulse

        if total_pulse_width < frame_length:
            self.pi.gpio_write(self.pin, 0)
            self.pi.gpio_trigger(self.pin, frame_length - total_pulse_width)

    def generate_crossfire(self, data):
        """
        Generate a simple Crossfire signal (CRSF Protocol).
        :param data: List of channel values [roll, pitch, yaw, throttle]
        """
        crossfire_frame = [0xC8, len(data) + 2]

        for channel in data:
            crossfire_frame.append(channel >> 8)
            crossfire_frame.append(channel & 0xFF)

        checksum = 0
        for byte in crossfire_frame:
            checksum ^= byte
        crossfire_frame.append(checksum)

        for byte in crossfire_frame:
            self._send_byte(byte)

    def _send_byte(self, byte):
        """Send individual bytes using the desired protocol timing."""
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            self.pi.gpio_write(self.pin, bit)
            time.sleep(0.0001)

    def cleanup(self):
        """Safely stop pigpio"""
        self.pi.stop()
