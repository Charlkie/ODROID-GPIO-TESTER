import tkinter as tk
from tkinter import ttk, messagebox
from odroid_gpio import OdroidGPIO

class HardwareInterface:
    # Keep track of pin objects to reuse them
    _pin_objects = {}

    @staticmethod
    def _parse_export_number(pin_label):
        # Extracts the number from a label like "#113(19)"
        return int(pin_label.split('(')[0][1:])

    @classmethod
    def _get_pin(cls, label):
        pin_number = cls._parse_export_number(label)
        if pin_number not in cls._pin_objects:
            cls._pin_objects[pin_number] = OdroidGPIO(pin_number)
        return cls._pin_objects[pin_number]

    @classmethod
    def set_pins_high(cls, labels):
        for label in labels:
            pin = cls._get_pin(label)
            pin.high()

    @classmethod
    def set_pins_low(cls, labels):
        for label in labels:
            pin = cls._get_pin(label)
            pin.low()

    @classmethod
    def output_square_wave(cls, labels, period_ms, duty_cycle):
        for label in labels:
            pin = cls._get_pin(label)
            pin.start_square_wave(period_ms, duty_cycle)

    @staticmethod
    def read_adc(channel):
        raw = OdroidGPIO.read_adc_raw(channel)
        voltage = OdroidGPIO.adc_voltage(channel)
        psi = OdroidGPIO.voltage_to_psi(voltage)
        return raw, voltage, psi




class GPIOTesterApp:
    # GPIO export numbers sorted, with physical header pins in brackets
    PIN_LABELS = [
        "#11(28)", "#12(27)", "#13(33)", "#14(7)",
        "#16(11)", "#17(13)", "#18(15)", "#67(10)",
        "#68(8)",  "#69(35)", "#70(36)", "#73(26)",
        "#74(32)", "#77(16)", "#78(18)", "#79(31)",
        "#80(29)", "#97(24)", "#109(5)", "#110(3)",
        "#113(19)", "#114(21)", "#115(23)"
    ]

    def __init__(self, master):
        self.master = master
        master.title("ODROID GPIO Tester")
        master.geometry("600x500")

        # Pin selection listbox
        pin_frame = ttk.LabelFrame(master, text="Select GPIO Pins")
        pin_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.pin_list = tk.Listbox(pin_frame, selectmode=tk.MULTIPLE)
        for label in self.PIN_LABELS:
            self.pin_list.insert(tk.END, label)
        self.pin_list.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        # Default background
        self.default_bg = self.pin_list.cget('bg')

        # Control buttons
        control_frame = ttk.LabelFrame(master, text="Pin Control")
        control_frame.pack(fill="x", padx=10, pady=5)

        self.high_button = tk.Button(control_frame, text="Set HIGH", command=self.set_high)
        self.high_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.low_button = tk.Button(control_frame, text="Set LOW", command=self.set_low)
        self.low_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Square wave controls
        wave_frame = ttk.LabelFrame(master, text="Square Wave Output")
        wave_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(wave_frame, text="Period (ms):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.period_entry = ttk.Entry(wave_frame, width=10)
        self.period_entry.insert(0, "1000")
        self.period_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(wave_frame, text="Duty Cycle (%):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.duty_entry = ttk.Entry(wave_frame, width=10)
        self.duty_entry.insert(0, "50")
        self.duty_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(wave_frame, text="Start Wave", command=self.start_wave).grid(row=0, column=4, padx=10)

        # ADC reader
        adc_frame = ttk.LabelFrame(master, text="ADC Reader")
        adc_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(adc_frame, text="Channel:").pack(side=tk.LEFT, padx=5)
        self.adc_channel = ttk.Combobox(adc_frame, values=["CH1(#37)","CH2(#40)"], width=8)
        self.adc_channel.current(0)
        self.adc_channel.pack(side=tk.LEFT)
        ttk.Button(adc_frame, text="Read ADC", command=self.read_adc).pack(side=tk.LEFT, padx=5)

        self.adc_value_label = ttk.Label(adc_frame, text="Value: --")
        self.adc_value_label.pack(side=tk.LEFT, padx=10)

    def get_selected_indices(self):
        return list(self.pin_list.curselection())

    def set_high(self):
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showwarning("No Pins", "Please select at least one GPIO pin.")
            return
        pins = [self.PIN_LABELS[i] for i in indices]
        HardwareInterface.set_pins_high(pins)
        for i in indices:
            # apply green background
            self.pin_list.itemconfig(i, bg='lightgreen')
            # clear selection highlight
            self.pin_list.selection_clear(i)

    def set_low(self):
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showwarning("No Pins", "Please select at least one GPIO pin.")
            return
        pins = [self.PIN_LABELS[i] for i in indices]
        HardwareInterface.set_pins_low(pins)
        for i in indices:
            # reset to default background
            self.pin_list.itemconfig(i, bg=self.default_bg)
            # clear selection highlight
            self.pin_list.selection_clear(i)

    def start_wave(self):
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showwarning("No Pins", "Please select pins first.")
            return
        try:
            period = float(self.period_entry.get())
            duty = float(self.duty_entry.get())
            if not (0 < duty <= 100): raise ValueError
            pins = [self.PIN_LABELS[i] for i in indices]
            HardwareInterface.output_square_wave(pins, period, duty)
            # clear highlights and selection
            for i in indices:
                self.pin_list.itemconfig(i, bg=self.default_bg)
                self.pin_list.selection_clear(i)
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter valid period>0 and 0<duty<=100.")

    def read_adc(self):
        channel = self.adc_channel.get()[:3]
        try:
            raw, voltage, psi = HardwareInterface.read_adc(channel)
            self.adc_value_label.config(
                text=f"Raw: {raw} | Voltage: {voltage:.3f} V | PSI: {psi:.1f}"
            )
        except Exception as e:
            messagebox.showerror("ADC Read Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = GPIOTesterApp(root)
    root.mainloop()
