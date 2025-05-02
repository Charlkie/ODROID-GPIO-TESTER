import sys
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random

try:
    from odroid_gpio import OdroidGPIO
    REAL_GPIO = True
except ImportError:
    REAL_GPIO = False
    class OdroidGPIO:
        """
        Fake GPIO/ADC for macOS testing. Generates dummy values and noops.
        """
        def __init__(self, pin):
            self.pin = pin
        def high(self): pass
        def low(self): pass
        def write(self, value): pass
        def start_square_wave(self, period_ms, duty_percent): pass
        @staticmethod
        def adc_voltage(channel):
            # Return a random PSI value between 0 and 150 for testing
            return random.uniform(0, 150)
        @staticmethod
        def voltage_to_psi(voltage, v_min=0.5, v_max=4.5, psi_min=0, psi_max=150):
            return voltage  # treat voltage as psi for simplicity

# ====== USER CONFIGURATION ======
VACUUM_PIN = 17          # Pin to drive the vacuum pump driver
SOLENOID_PIN = 27        # Pin to open/close the solenoid valve
TRANSDUCER_CHANNEL = "CH1"  # ADC channel key: "CH1" or "CH2"
POWER_PINS = [22, 23, 24]   # Pins that power the solenoid driver
ATMOSPHERE_PSI = 0.0     # Gauge pressure at atmosphere (psi)

# Initialize GPIO objects
vacuum_gpio = OdroidGPIO(VACUUM_PIN)
solenoid_gpio = OdroidGPIO(SOLENOID_PIN)
power_gpios = [OdroidGPIO(pin) for pin in POWER_PINS]

# System initialization
def init_pins():
    for gpio in power_gpios:
        gpio.high()
    vacuum_gpio.low()
    solenoid_gpio.low()

# Read pressure in PSI
def pressure_reading():
    psi = OdroidGPIO.adc_voltage(TRANSDUCER_CHANNEL)
    return psi

# Run sequence
def run_sequence(desired_pressure):
    vacuum_gpio.high()
    while pressure_reading() > desired_pressure:
        time.sleep(0.1)
    solenoid_gpio.high()
    vacuum_gpio.low()
    messagebox.showinfo("Run", f"Reached {desired_pressure:.2f} psi. Sequence complete.")

# Shutdown sequence
def shutdown_sequence():
    while pressure_reading() < ATMOSPHERE_PSI - 0.5:
        time.sleep(0.1)
    solenoid_gpio.high()
    messagebox.showinfo("Shutdown", "Chamber at atmospheric pressure. Solenoid opened.")

# GUI application
class VacuumControlApp:
    def __init__(self, master):
        self.master = master
        master.title("Vacuum Pump Controller")

        self.pressure_var = tk.StringVar(value="--.- psi")
        tk.Label(master, text="Current Pressure:").grid(row=0, column=0, sticky="w")
        tk.Label(master, textvariable=self.pressure_var).grid(row=0, column=1, sticky="e")

        tk.Label(master, text="Desired Pressure (psi):").grid(row=1, column=0, sticky="w")
        self.desired_entry = tk.Entry(master)
        self.desired_entry.grid(row=1, column=1)
        self.desired_entry.insert(0, "10.0")

        self.run_btn = tk.Button(master, text="Run", command=self.start_run)
        self.run_btn.grid(row=2, column=0, pady=10)
        self.shutdown_btn = tk.Button(master, text="Shutdown", command=self.start_shutdown)
        self.shutdown_btn.grid(row=2, column=1, pady=10)

        self.update_pressure()

    def update_pressure(self):
        try:
            psi = pressure_reading()
            self.pressure_var.set(f"{psi:.2f} psi")
        except Exception:
            self.pressure_var.set("Error")
        self.master.after(500, self.update_pressure)

    def start_run(self):
        try:
            desired = float(self.desired_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid number for desired pressure.")
            return
        threading.Thread(target=run_sequence, args=(desired,), daemon=True).start()

    def start_shutdown(self):
        threading.Thread(target=shutdown_sequence, daemon=True).start()

if __name__ == "__main__":
    init_pins()
    if not REAL_GPIO:
        print("Running in simulation mode (fake GPIO/ADC)")
    root = tk.Tk()
    app = VacuumControlApp(root)
    root.mainloop()
