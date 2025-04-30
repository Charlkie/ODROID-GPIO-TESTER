import os
import threading
import time

class OdroidGPIO:
    SYSFS_GPIO_PATH = "/sys/class/gpio"
    ADC_PATHS = {
        "CH1": "/sys/bus/platform/drivers/rockchip-saradc/fe720000.saradc/iio:device0/in_voltage3_raw",  # Pin #37
        "CH2": "/sys/bus/platform/drivers/rockchip-saradc/fe720000.saradc/iio:device0/in_voltage2_raw",  # Pin #40
    }

    def __init__(self, pin):
        self.pin = str(pin)
        self.export_pin()
        self.set_direction("out")

    def export_pin(self):
        if not os.path.exists(f"{self.SYSFS_GPIO_PATH}/gpio{self.pin}"):
            with open(f"{self.SYSFS_GPIO_PATH}/export", 'w') as f:
                f.write(self.pin)

    def unexport_pin(self):
        if os.path.exists(f"{self.SYSFS_GPIO_PATH}/gpio{self.pin}"):
            with open(f"{self.SYSFS_GPIO_PATH}/unexport", 'w') as f:
                f.write(self.pin)

    def set_direction(self, direction):
        assert direction in ("in", "out")
        with open(f"{self.SYSFS_GPIO_PATH}/gpio{self.pin}/direction", 'w') as f:
            f.write(direction)

    def write(self, value):
        assert value in (0, 1)
        with open(f"{self.SYSFS_GPIO_PATH}/gpio{self.pin}/value", 'w') as f:
            f.write(str(value))

    def high(self):
        self.write(1)

    def low(self):
        self.write(0)

    def start_square_wave(self, period_ms, duty_percent):
        on_time = (period_ms * duty_percent / 100.0) / 1000.0
        off_time = (period_ms * (100 - duty_percent) / 100.0) / 1000.0

        def wave_loop():
            while True:
                self.high()
                time.sleep(on_time)
                self.low()
                time.sleep(off_time)

        t = threading.Thread(target=wave_loop, daemon=True)
        t.start()

    @staticmethod
    def read_adc_raw(channel):
        """
        Reads the raw ADC integer value.
        """
        path = OdroidGPIO.ADC_PATHS.get(channel)
        if not path or not os.path.exists(path):
            raise ValueError(f"ADC channel '{channel}' is not available.")
        with open(path, 'r') as f:
            return int(f.read().strip())

    @staticmethod
    def adc_voltage(channel, reference_voltage=1.8, resolution_bits=10):
        """
        Converts raw ADC value to voltage.

        ODROID-M1S has a 10-bit ADC (0–1023) and 1.8V reference.
        """
        raw = OdroidGPIO.read_adc_raw(channel)
        max_val = (2 ** resolution_bits) - 1
        return (raw / max_val) * reference_voltage

    @staticmethod
    def voltage_to_psi(voltage, v_min=0.5, v_max=4.5, psi_min=0, psi_max=150):
        """
        Converts voltage to PSI for a typical 0.5–4.5V analog pressure sensor.
        Clamps output to sensor range.
        """
        if voltage < v_min:
            return psi_min
        if voltage > v_max:
            return psi_max
        return ((voltage - v_min) / (v_max - v_min)) * (psi_max - psi_min) + psi_min

