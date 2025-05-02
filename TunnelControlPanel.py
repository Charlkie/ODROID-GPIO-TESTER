import tkinter as tk
from tkinter import messagebox
import threading
import time
from odroid_gpio import OdroidGPIO  # Import the provided OdroidGPIO class

# ====== USER CONFIGURATION ======
# Replace these placeholders with your actual GPIO pin numbers or ADC channel
VACUUM_PIN = 17          # Pin to drive the vacuum pump driver
SOLENOID_PIN = 27        # Pin to open/close the solenoid valve
TRANSDUCER_CHANNEL = "CH1"  # ADC channel key: "CH1" or "CH2"
POWER_PINS = [22, 23, 24]   # Pins that power the solenoid driver
ATMOSPHERE_PSI = 0.0     # Gauge pressure at atmosphere (psi)
# ===============================
# Initialize GPIO objects
vacuum_gpio = OdroidGPIO(VACUUM_PIN)
solenoid_gpio = OdroidGPIO(SOLENOID_PIN)
power_gpios = [OdroidGPIO(pin) for pin in POWER_PINS]

# System initialization
def init_pins():
    # Power up the solenoid driver
    for gpio in power_gpios:
        gpio.high()
    # Ensure vacuum pump and solenoid are off
    vacuum_gpio.low()
    solenoid_gpio.low()

# Read pressure in PSI
def pressure_reading():
    voltage = OdroidGPIO.adc_voltage(TRANSDUCER_CHANNEL)
    psi = OdroidGPIO.voltage_to_psi(voltage)
    return psi

# Run sequence: pump until below desired pressure, then close solenoid and stop pump
def run_sequence(desired_pressure):
    vacuum_gpio.high()  # Start vacuum pump
    # Wait until chamber pressure drops below the setpoint
    while pressure_reading() > desired_pressure:
        time.sleep(0.1)
    solenoid_gpio.high()  # Close solenoid valve
    vacuum_gpio.low()     # Stop vacuum pump
    messagebox.showinfo("Run", f"Reached {desired_pressure:.2f} psi. Sequence complete.")

# Shutdown sequence: wait until chamber returns to atmospheric pressure, then open solenoid
def shutdown_sequence():
    # Wait for chamber to return to atmosphere
    while pressure_reading() < ATMOSPHERE_PSI - 0.5:  # small tolerance
        time.sleep(0.1)
    solenoid_gpio.high()  # Open solenoid valve
    messagebox.showinfo("Shutdown", "Chamber at atmospheric pressure. Solenoid opened.")

# GUI application
class VacuumControlApp:
    def __init__(self, master):
        self.master = master
        master.title("Vacuum Pump Controller")

        # Pressure display
        self.pressure_var = tk.StringVar(value="--.- psi")
        tk.Label(master, text="Current Pressure:").grid(row=0, column=0, sticky="w")
        tk.Label(master, textvariable=self.pressure_var).grid(row=0, column=1, sticky="e")

        # Desired pressure input
        tk.Label(master, text="Desired Pressure (psi):").grid(row=1, column=0, sticky="w")
        self.desired_entry = tk.Entry(master)
        self.desired_entry.grid(row=1, column=1)
        self.desired_entry.insert(0, "10.0")  # default setpoint

        # Control buttons
        self.run_btn = tk.Button(master, text="Run", command=self.start_run)
        self.run_btn.grid(row=2, column=0, pady=10)
        self.shutdown_btn = tk.Button(master, text="Shutdown", command=self.start_shutdown)
        self.shutdown_btn.grid(row=2, column=1, pady=10)

        # Kick off periodic pressure updates
        self.update_pressure()

    def update_pressure(self):
        try:
            psi = pressure_reading()
            self.pressure_var.set(f"{psi:.2f} psi")
        except Exception as e:
            self.pressure_var.set(f"Error")
        self.master.after(500, self.update_pressure)

    def start_run(self):
        try:
            desired = float(self.desired_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for desired pressure.")
            return
        threading.Thread(target=run_sequence, args=(desired,), daemon=True).start()

    def start_shutdown(self):
        threading.Thread(target=shutdown_sequence, daemon=True).start()


if __name__ == "__main__":
    init_pins()
    root = tk.Tk()
    app = VacuumControlApp(root)
    root.mainloop()
