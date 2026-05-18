import tkinter as tk
from tkinter import ttk
import time

# -----------------------------
# SYSTEM CONSTANTS
# -----------------------------
TANK_HEIGHT = 3.0
UNDERFLOW_LEVEL = 0.5
OVERFLOW_LEVEL = 2.8
INITIAL_LEVEL = 1.5
TAP_FLOW_RATE = 0.15
MOTOR_FLOW_RATE = 0.20


# -----------------------------
# TANK MODEL
# -----------------------------
class WaterTankModel:
    def __init__(self):
        self.water_level = INITIAL_LEVEL
        self.motor_status = "OFF"
        self.buzzer_status = "OFF"
        self.system_status = "NORMAL"
        self.tap_status = "OFF"
        self.last_update = time.time()

    def update_system(self):
        now = time.time()
        dt = now - self.last_update

        motor_inflow = MOTOR_FLOW_RATE if self.motor_status == "ON" else 0
        tap_outflow = TAP_FLOW_RATE if self.tap_status == "ON" else 0

        level_change = (motor_inflow - tap_outflow) * dt
        self.water_level += level_change
        self.water_level = max(0, min(TANK_HEIGHT, self.water_level))

        if self.water_level >= OVERFLOW_LEVEL:
            self.system_status = "OVERFLOW"
            self.buzzer_status = "ON"
            self.motor_status = "OFF"
        elif self.water_level <= UNDERFLOW_LEVEL:
            self.system_status = "UNDERFLOW"
            self.buzzer_status = "ON"
            self.motor_status = "ON"
        else:
            self.system_status = "NORMAL"
            self.buzzer_status = "OFF"

        self.last_update = now
        return self.water_level, motor_inflow, tap_outflow, level_change


# -----------------------------
# GUI APPLICATION
# -----------------------------
class WaterTankHMI:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI-Based Water Tank Monitoring System")
        self.root.geometry("1000x750")

        self.tank = WaterTankModel()
        self.is_auto_refresh = True
        self.last_status = self.tank.system_status

        self.setup_gui()
        self.update_display()

    # -----------------------------
    # GUI SETUP
    # -----------------------------
    def setup_gui(self):
        header = tk.Frame(self.root, bg="#2c3e50", height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="🚰 GUI-Based Water Tank Monitoring System",
                 font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack(pady=10)

        tk.Label(header, text="Norman's Seven Stages of Action",
                 font=("Arial", 10), bg="#2c3e50", fg="white").pack()

        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_tank_panel(main)
        self.create_control_panel(main)
        self.create_log_panel()

    # -----------------------------
    # TANK PANEL
    # -----------------------------
    def create_tank_panel(self, parent):
        frame = tk.LabelFrame(parent, text="Water Tank Visualization",
                              font=("Arial", 11, "bold"))
        frame.pack(side="left", padx=10)

        self.canvas = tk.Canvas(frame, width=300, height=450, bg="white")
        self.canvas.pack(padx=10, pady=10)

        self.level_label = tk.Label(frame, text="1.50 m",
                                    font=("Arial", 12, "bold"))
        self.level_label.pack()

    # -----------------------------
    # CONTROL PANEL
    # -----------------------------
    def create_control_panel(self, parent):
        frame = tk.LabelFrame(parent, text="System Control & Status",
                              font=("Arial", 11, "bold"))
        frame.pack(side="left", padx=10)

        self.status_var = tk.StringVar()
        self.motor_var = tk.StringVar()
        self.buzzer_var = tk.StringVar()
        self.tap_var = tk.StringVar()
        self.inflow_var = tk.StringVar()
        self.outflow_var = tk.StringVar()
        self.level_change_var = tk.StringVar()

        status_frame = tk.LabelFrame(frame, text="Current Status",
                                     font=("Arial", 10, "bold"))
        status_frame.pack(fill="x", padx=5, pady=5)

        fields = [
            ("System Status:", self.status_var),
            ("Motor:", self.motor_var),
            ("Buzzer:", self.buzzer_var),
            ("Tap:", self.tap_var),
            ("Motor Inflow:", self.inflow_var),
            ("Tap Outflow:", self.outflow_var),
            ("Level Change:", self.level_change_var)
        ]

        for lbl, var in fields:
            row = tk.Frame(status_frame)
            row.pack(anchor="w", padx=10)
            tk.Label(row, text=lbl, width=15, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var).pack(side="left")

        # Motor Control
        motor_frame = tk.LabelFrame(frame, text="Motor Control",
                                    font=("Arial", 10, "bold"))
        motor_frame.pack(fill="x", padx=5, pady=10)

        tk.Button(motor_frame, text="Motor ON", bg="green", fg="white",
                  command=lambda: self.set_motor("ON")).pack(side="left", padx=5)
        tk.Button(motor_frame, text="Motor OFF", bg="red", fg="white",
                  command=lambda: self.set_motor("OFF")).pack(side="left", padx=5)

        # Tap Control
        tap_frame = tk.LabelFrame(frame, text="Tap Control",
                                  font=("Arial", 10, "bold"))
        tap_frame.pack(fill="x", padx=5, pady=10)

        tk.Button(tap_frame, text="Tap ON", bg="blue", fg="white",
                  command=lambda: self.set_tap("ON")).pack(side="left", padx=5)
        tk.Button(tap_frame, text="Tap OFF", bg="gray", fg="white",
                  command=lambda: self.set_tap("OFF")).pack(side="left", padx=5)

        self.auto_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Auto Refresh (2s)",
                       variable=self.auto_var,
                       command=self.toggle_auto).pack(pady=10)

    # -----------------------------
    # LOG PANEL
    # -----------------------------
    def create_log_panel(self):
        frame = tk.LabelFrame(self.root, text="Action Log",
                              font=("Arial", 11, "bold"))
        frame.pack(fill="x", padx=20, pady=10)

        self.log_text = tk.Text(frame, height=6)
        self.log_text.pack(fill="both", expand=True)

        self.log("System initialized")
        self.log(f"Initial water level: {INITIAL_LEVEL} m")

    # -----------------------------
    # UPDATE LOOP
    # -----------------------------
    def update_display(self):
        level, inflow, outflow, change = self.tank.update_system()

        self.level_label.config(text=f"{level:.3f} m")
        self.status_var.set(self.tank.system_status)
        self.motor_var.set(self.tank.motor_status)
        self.buzzer_var.set(self.tank.buzzer_status)
        self.tap_var.set(self.tank.tap_status)
        self.inflow_var.set(f"{inflow:.2f}")
        self.outflow_var.set(f"{outflow:.2f}")
        self.level_change_var.set(f"{change/2:.3f}/s")

        self.draw_tank()

        if self.is_auto_refresh:
            self.root.after(2000, self.update_display)

    # -----------------------------
    # DRAW TANK + TAPS
    # -----------------------------
    def draw_tank(self):
        self.canvas.delete("all")

        left, right = 80, 220
        top, bottom = 60, 360

        self.canvas.create_rectangle(left, top, right, bottom, width=3)

        water_h = (self.tank.water_level / TANK_HEIGHT) * (bottom - top)
        water_top = bottom - water_h

        color = "skyblue"
        if self.tank.system_status == "OVERFLOW":
            color = "red"
        elif self.tank.system_status == "UNDERFLOW":
            color = "orange"

        self.canvas.create_rectangle(left, water_top, right, bottom,
                                     fill=color, outline="")

        # -------- TOP TAP (INLET) --------
        x = 150
        self.canvas.create_line(x, 20, x, top, width=3)
        inlet_color = "green" if self.tank.motor_status == "ON" else "gray"
        self.canvas.create_oval(x-12, 5, x+12, 25,
                                fill=inlet_color, width=2)

        if self.tank.motor_status == "ON":
            self.canvas.create_line(x-15, 15, x+15, 15, width=3)
            for i in range(3):
                self.canvas.create_line(x-5, top+i*10,
                                        x+5, top+i*10+8,
                                        width=2, fill="blue")
        else:
            self.canvas.create_line(x, 8, x, 22, width=3)

        self.canvas.create_text(x, 40, text="INLET", font=("Arial", 9, "bold"))

        # -------- BOTTOM TAP (OUTLET) --------
        self.canvas.create_line(x, bottom, x, bottom+30, width=3)
        tap_color = "blue" if self.tank.tap_status == "ON" else "gray"
        self.canvas.create_oval(x-10, bottom+30, x+10, bottom+50,
                                fill=tap_color, width=2)

        if self.tank.tap_status == "ON":
            self.canvas.create_line(x-15, bottom+40, x+15, bottom+40, width=3)
            for i in range(3):
                self.canvas.create_line(x-10, bottom+55+i*10,
                                        x-20, bottom+65+i*10,
                                        width=2, fill="blue")
                self.canvas.create_line(x+10, bottom+55+i*10,
                                        x+20, bottom+65+i*10,
                                        width=2, fill="blue")
        else:
            self.canvas.create_line(x, bottom+35, x, bottom+45, width=3)

        self.canvas.create_text(x, bottom+80,
                                text=f"TAP: {self.tank.tap_status}",
                                font=("Arial", 10, "bold"))

    # -----------------------------
    # CONTROLS
    # -----------------------------
    def set_motor(self, state):
        if self.tank.system_status == "NORMAL":
            self.tank.motor_status = state
            self.log(f"Motor set {state}")

    def set_tap(self, state):
        if self.tank.system_status == "UNDERFLOW" and state == "ON":
            self.log("Tap blocked due to UNDERFLOW")
            return
        self.tank.tap_status = state
        self.log(f"Tap set {state}")

    def toggle_auto(self):
        self.is_auto_refresh = self.auto_var.get()
        self.log(f"Auto refresh {'ON' if self.is_auto_refresh else 'OFF'}")

    def log(self, msg):
        t = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{t}] {msg}\n")
        self.log_text.see(tk.END)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WaterTankHMI(root)
    root.mainloop()
