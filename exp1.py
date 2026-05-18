import tkinter as tk
from tkinter import ttk, messagebox
import time

# -----------------------------
# SYSTEM CONSTANTS
# -----------------------------
TANK_HEIGHT = 3.0
UNDERFLOW_LEVEL = 0.5
OVERFLOW_LEVEL = 2.8
INITIAL_LEVEL = 1.5
TAP_FLOW_RATE = 0.05  # DECREASED: Flow rate when tap is ON (was 0.15)
MOTOR_FLOW_RATE = 0.08 # DECREASED: Flow rate when motor is ON (was 0.25)


# -----------------------------
# TANK MODEL
# -----------------------------
class WaterTankModel:
    def __init__(self):
        self.water_level = INITIAL_LEVEL
        self.motor_status = "OFF"  # Start with motor OFF
        self.buzzer_status = "OFF"
        self.system_status = "NORMAL"
        self.tap_status = "OFF"  # Tap status
        self.last_update = time.time()

    def update_system(self):
        current_time = time.time()
        dt = current_time - self.last_update
        
        # TAP LOGIC: Water only decreases when tap is ON
        tap_outflow = 0
        if self.tap_status == "ON":
            tap_outflow = TAP_FLOW_RATE
        
        # MOTOR LOGIC: Motor fills tank only when ON
        motor_inflow = 0
        if self.motor_status == "ON":
            motor_inflow = MOTOR_FLOW_RATE  # Fixed motor inflow rate
        
        # Calculate level change
        # Water level increases when motor is ON
        # Water level decreases when tap is ON
        # When both are OFF, water level remains CONSTANT
        level_change = (motor_inflow - tap_outflow) * dt
        self.water_level += level_change
        
        # IMPORTANT: Water level should NOT go above overflow level
        # Even if calculation says it should, cap it at OVERFLOW_LEVEL
        if self.water_level > OVERFLOW_LEVEL:
            self.water_level = OVERFLOW_LEVEL
            
        self.water_level = max(0, min(TANK_HEIGHT, self.water_level))
        
        # Check safety conditions
        if self.water_level >= OVERFLOW_LEVEL:
            self.system_status = "OVERFLOW"
            self.buzzer_status = "ON"
            self.motor_status = "OFF"  # Auto turn OFF motor
        elif self.water_level <= UNDERFLOW_LEVEL:
            self.system_status = "UNDERFLOW"
            self.buzzer_status = "ON"
            self.motor_status = "ON"  # Auto turn ON motor
        else:
            self.system_status = "NORMAL"
            self.buzzer_status = "OFF"

        self.last_update = current_time
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
        self.last_status = self.tank.system_status
        self.last_level = self.tank.water_level
        self.last_motor_status = self.tank.motor_status
        self.last_tap_status = self.tank.tap_status
        self.last_constant_log_time = 0  # Track last time "constant water level" was logged
        self.last_status_change_time = 0  # Track last status change log
        self.last_auto_action_time = 0    # Track last automatic action log

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

        

        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_tank_panel(main)
        self.create_control_panel(main)
        self.create_log_panel()

    # -----------------------------
    # TANK VISUALIZATION
    # -----------------------------
    def create_tank_panel(self, parent):
        frame = tk.LabelFrame(parent, text="Water Tank Visualization", font=("Arial", 11, "bold"))
        frame.pack(side="left", padx=10)

        self.canvas = tk.Canvas(frame, width=300, height=450, bg="white")
        self.canvas.pack(padx=10, pady=10)

        self.level_label = tk.Label(frame, text="1.50 m", font=("Arial", 12, "bold"))
        self.level_label.pack()

    # -----------------------------
    # CONTROL PANEL
    # -----------------------------
    def create_control_panel(self, parent):
        frame = tk.LabelFrame(parent, text="System Control & Status", font=("Arial", 11, "bold"))
        frame.pack(side="left", padx=10)

        self.status_var = tk.StringVar()
        self.motor_var = tk.StringVar()
        self.buzzer_var = tk.StringVar()
        self.inflow_var = tk.StringVar()
        self.tap_flow_var = tk.StringVar()
        self.tap_var = tk.StringVar()
        self.level_change_var = tk.StringVar()

        # System Status Section
        status_frame = tk.LabelFrame(frame, text="Current Status", font=("Arial", 10, "bold"))
        status_frame.pack(fill="x", padx=5, pady=5)
        
        for label, var in [
            ("System Status:", self.status_var),
            ("Motor:", self.motor_var),
            ("Buzzer:", self.buzzer_var),
            ("Tap:", self.tap_var),
            ("Motor Inflow:", self.inflow_var),
            ("Tap Outflow:", self.tap_flow_var),
            ("Level Change:", self.level_change_var)
        ]:
            row = tk.Frame(status_frame)
            row.pack(anchor="w", pady=2, padx=10)
            tk.Label(row, text=label, width=15, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var, width=15).pack(side="left")

        # Motor Control Section
        motor_frame = tk.LabelFrame(frame, text="Motor Control", font=("Arial", 10, "bold"))
        motor_frame.pack(fill="x", padx=5, pady=10)
        
        motor_btn_frame = tk.Frame(motor_frame)
        motor_btn_frame.pack(pady=10)
        
        self.motor_on_btn = tk.Button(motor_btn_frame, text="Motor ON",
                  command=lambda: self.set_motor("ON"),
                  bg="green", fg="white", width=10)
        self.motor_on_btn.pack(side="left", padx=5)
        
        self.motor_off_btn = tk.Button(motor_btn_frame, text="Motor OFF",
                  command=lambda: self.set_motor("OFF"),
                  bg="red", fg="white", width=10)
        self.motor_off_btn.pack(side="left", padx=5)
        
        # Motor description - UPDATED with new flow rate
        tk.Label(motor_frame, text=f"Motor: Fills the tank (+{MOTOR_FLOW_RATE:.2f}/s)", font=("Arial", 9), fg="gray").pack(pady=(0, 5))

        # Tap Control Section
        tap_frame = tk.LabelFrame(frame, text="Tap Control", font=("Arial", 10, "bold"))
        tap_frame.pack(fill="x", padx=5, pady=10)
        
        tap_btn_frame = tk.Frame(tap_frame)
        tap_btn_frame.pack(pady=10)
        
        self.tap_on_btn = tk.Button(tap_btn_frame, text="Tap ON",
                  command=lambda: self.set_tap("ON"),
                  bg="blue", fg="white", width=10)
        self.tap_on_btn.pack(side="left", padx=5)
        
        self.tap_off_btn = tk.Button(tap_btn_frame, text="Tap OFF",
                  command=lambda: self.set_tap("OFF"),
                  bg="gray", fg="white", width=10)
        self.tap_off_btn.pack(side="left", padx=5)
        
        # Tap description - UPDATED with new flow rate
        tk.Label(tap_frame, text=f"Tap: Drains the tank (-{TAP_FLOW_RATE:.2f}/s)", font=("Arial", 9), fg="gray").pack(pady=(0, 5))

    # -----------------------------
    # LOG PANEL
    # -----------------------------
    def create_log_panel(self):
        frame = tk.LabelFrame(self.root, text="Action Log", font=("Arial", 11, "bold"))
        frame.pack(fill="x", padx=20, pady=10)

        self.log_text = tk.Text(frame, height=6, bg="#f8f9fa")
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log("System initialized")
        self.log(f"Initial water level: {INITIAL_LEVEL} m")
        self.log(f"Motor flow rate: +{MOTOR_FLOW_RATE:.2f} m/s")
        self.log(f"Tap flow rate: -{TAP_FLOW_RATE:.2f} m/s")
        self.log("NOTE: Water level remains constant when both motor and tap are OFF")

    # -----------------------------
    # CORE UPDATE LOOP
    # -----------------------------
    def update_display(self):
        level, motor_inflow, tap_outflow, level_change = self.tank.update_system()
        
        # Update display variables - show overflow status in text only
        self.level_label.config(text=f"{level:.3f} m")
        
        # Show overflow status in text only
        if self.tank.system_status in ["OVERFLOW", "UNDERFLOW"]:
            self.status_var.set(f"⚠️ {self.tank.system_status}")
        else:
            self.status_var.set(self.tank.system_status)
            
        self.motor_var.set(self.tank.motor_status)
        self.buzzer_var.set(self.tank.buzzer_status)
        self.tap_var.set(self.tank.tap_status)
        self.inflow_var.set(f"{motor_inflow:.3f}")
        self.tap_flow_var.set(f"{tap_outflow:.3f}")
        
        # Show level change with + or - sign
        if level_change > 0:
            self.level_change_var.set(f"+{level_change:.3f}/s")
        elif level_change < 0:
            self.level_change_var.set(f"{level_change:.3f}/s")
        else:
            self.level_change_var.set(f"{level_change:.3f}/s")

        self.draw_tank()
        
        # Update button states based on system status
        self.update_button_states()

        # Check for status changes and log them only when status actually changes
        if self.tank.system_status != self.last_status:
            current_time = time.time()
            # Only log if enough time has passed since last status change (to avoid duplicates)
            if current_time - self.last_status_change_time > 1.0:
                self.log(f"System status changed to: {self.tank.system_status}")
                self.last_status_change_time = current_time
            self.last_status = self.tank.system_status

        # Check for automatic actions and log them (but only once)
        current_time = time.time()
        if self.tank.system_status == "OVERFLOW" and self.last_motor_status == "ON":
            # Motor was automatically turned OFF due to overflow
            if current_time - self.last_auto_action_time > 1.0:
                self.log("AUTOMATIC: Motor turned OFF due to overflow")
                self.last_auto_action_time = current_time
        elif self.tank.system_status == "UNDERFLOW" and self.last_motor_status == "OFF":
            # Motor was automatically turned ON due to underflow
            if current_time - self.last_auto_action_time > 1.0:
                self.log("AUTOMATIC: Motor turned ON due to underflow")
                self.last_auto_action_time = current_time

        # Update last known motor status
        if self.tank.motor_status != self.last_motor_status:
            self.last_motor_status = self.tank.motor_status

        # Log when water level remains constant (but only occasionally to avoid spam)
        if motor_inflow == 0 and tap_outflow == 0:
            if abs(level_change) < 0.0001:  # Almost zero change
                current_time = time.time()
                # Only log constant status once every 10 seconds to avoid spam
                if current_time - self.last_constant_log_time > 10.0:
                    self.log("Water level constant (Motor OFF, Tap OFF)")
                    self.last_constant_log_time = current_time

        # Update every 100ms for smooth display
        self.root.after(100, self.update_display)

    def update_button_states(self):
        # Enable/disable buttons based on system status
        if self.tank.system_status == "OVERFLOW":
            self.motor_on_btn.config(state="disabled")
            self.motor_off_btn.config(state="normal")
            self.tap_on_btn.config(state="normal")  # Allow tap to drain
            self.tap_off_btn.config(state="normal")
        elif self.tank.system_status == "UNDERFLOW":
            self.motor_on_btn.config(state="normal")
            self.motor_off_btn.config(state="disabled")
            self.tap_on_btn.config(state="disabled")  # Prevent tap when underflow
            self.tap_off_btn.config(state="normal")
        else:
            self.motor_on_btn.config(state="normal")
            self.motor_off_btn.config(state="normal")
            self.tap_on_btn.config(state="normal")
            self.tap_off_btn.config(state="normal")

    def draw_tank(self):
        self.canvas.delete("all")
        
        # Draw tank
        tank_left = 80
        tank_right = 220
        tank_top = 50
        tank_bottom = 350
        self.canvas.create_rectangle(tank_left, tank_top, tank_right, tank_bottom, width=3)
        
        # Calculate water height - IMPORTANT: Water should NOT go above overflow line
        # The water level is capped at OVERFLOW_LEVEL in the model, so it won't exceed 2.8m
        height = (self.tank.water_level / TANK_HEIGHT) * (tank_bottom - tank_top)
        water_top = tank_bottom - height
        
        # Water is always sky blue
        water_color = "skyblue"
            
        # Draw water - it will stop at the overflow line (2.8m)
        self.canvas.create_rectangle(tank_left, water_top, tank_right, tank_bottom, 
                                     fill=water_color, outline="")
        
        # Draw warning message if in overflow or underflow
        if self.tank.system_status in ["OVERFLOW", "UNDERFLOW"]:
            # Draw warning symbol
            warning_x = 150
            warning_y = 100
            self.canvas.create_polygon(
                warning_x, warning_y-20,
                warning_x-15, warning_y+10,
                warning_x+15, warning_y+10,
                fill="yellow", outline="black", width=2
            )
            # Draw exclamation mark
            self.canvas.create_text(warning_x, warning_y, text="!", font=("Arial", 16, "bold"))
            
            # Draw alert text
            alert_text = "OVERFLOW!" if self.tank.system_status == "OVERFLOW" else "UNDERFLOW!"
            self.canvas.create_text(150, 140, text=alert_text, font=("Arial", 12, "bold"), fill="red")
        
        # Draw tap
        self.draw_tap()
        
        # Draw motor inflow pipe if motor is ON
        if self.tank.motor_status == "ON":
            # Draw inflow pipe on top
            pipe_x = 150
            self.canvas.create_line(pipe_x, 20, pipe_x, tank_top, width=3, fill="green")
            self.canvas.create_oval(pipe_x-8, 15, pipe_x+8, 25, fill="green")
            # Draw water droplets flowing in
            for i in range(3):
                offset = i * 5
                self.canvas.create_line(pipe_x-5, tank_top+offset, pipe_x+5, tank_top+offset+10, 
                                       width=2, fill="blue")
        
        # Draw labels
        self.canvas.create_text(150, 30, text="WATER TANK", font=("Arial", 12, "bold"))
        
        # Draw level indicators with overflow/underflow lines
        # 0 m line
        self.canvas.create_line(tank_left-10, tank_bottom, tank_left, tank_bottom, width=2)
        self.canvas.create_text(tank_left-15, tank_bottom, text="0 m", anchor="e")
        
        # Underflow line - RED
        underflow_y = tank_bottom - (UNDERFLOW_LEVEL/TANK_HEIGHT) * (tank_bottom - tank_top)
        self.canvas.create_line(tank_left-10, underflow_y, tank_left, underflow_y, 
                               width=2, dash=(5, 2), fill="red")
        self.canvas.create_text(tank_left-15, underflow_y, text=f"{UNDERFLOW_LEVEL}m", 
                               anchor="e", fill="red")
        
        # 1 m line
        one_m_y = tank_bottom - (1.0/TANK_HEIGHT) * (tank_bottom - tank_top)
        self.canvas.create_line(tank_left-10, one_m_y, tank_left, one_m_y, width=1)
        self.canvas.create_text(tank_left-15, one_m_y, text="1 m", anchor="e")
        
        # 2 m line
        two_m_y = tank_bottom - (2.0/TANK_HEIGHT) * (tank_bottom - tank_top)
        self.canvas.create_line(tank_left-10, two_m_y, tank_left, two_m_y, width=1)
        self.canvas.create_text(tank_left-15, two_m_y, text="2 m", anchor="e")
        
        # Overflow line - RED (water stops here)
        overflow_y = tank_bottom - (OVERFLOW_LEVEL/TANK_HEIGHT) * (tank_bottom - tank_top)
        self.canvas.create_line(tank_left-10, overflow_y, tank_left, overflow_y, 
                               width=2, dash=(5, 2), fill="red")
        self.canvas.create_text(tank_left-15, overflow_y, text=f"{OVERFLOW_LEVEL}m", 
                               anchor="e", fill="red")
        
        # 3 m line (top) - but water won't reach this because it stops at 2.8m
        self.canvas.create_line(tank_left-10, tank_top, tank_left, tank_top, width=2)
        self.canvas.create_text(tank_left-15, tank_top, text="3 m", anchor="e")

    def draw_tap(self):
        # Draw tap at the bottom of the tank
        tap_x = 150  # Center of tank
        
        # Draw tap pipe
        self.canvas.create_line(tap_x, 350, tap_x, 380, width=3, fill="gray")
        
        # Draw tap body
        tap_color = "blue" if self.tank.tap_status == "ON" else "gray"
        self.canvas.create_oval(tap_x-10, 380, tap_x+10, 400, fill=tap_color, outline="black", width=2)
        
        # Draw tap handle
        if self.tank.tap_status == "ON":
            # Handle in horizontal position (open)
            self.canvas.create_line(tap_x-15, 390, tap_x+15, 390, width=3)
        else:
            # Handle in vertical position (closed)
            self.canvas.create_line(tap_x, 385, tap_x, 395, width=3)
        
        # Draw water flow if tap is ON
        if self.tank.tap_status == "ON":
            for i in range(3):
                y_start = 400 + (i * 10)
                y_end = 420 + (i * 10)
                self.canvas.create_line(tap_x-5, y_start, tap_x-15, y_end, width=2, fill="blue")
                self.canvas.create_line(tap_x+5, y_start, tap_x+15, y_end, width=2, fill="blue")
        
        # Draw tap label
        self.canvas.create_text(tap_x, 420, text=f"TAP: {self.tank.tap_status}", 
                               font=("Arial", 10, "bold"), fill=tap_color)

    # -----------------------------
    # CONTROLS
    # -----------------------------
    def set_motor(self, state):
        # Only allow motor control when not in automatic safety mode
        if self.tank.system_status == "NORMAL":
            self.tank.motor_status = state
            # Check if this is actually a change to avoid duplicate logs
            if self.last_motor_status != state:
                self.log(f"User set motor {state}")
                self.last_motor_status = state
        else:
            # Inform user that motor is in automatic mode (but only once)
            if self.last_motor_status != self.tank.motor_status:
                status_msg = "OVERFLOW" if self.tank.system_status == "OVERFLOW" else "UNDERFLOW"
                self.log(f"Cannot manually change motor: System in {status_msg} mode")

    def set_tap(self, state):
        if self.tank.system_status == "UNDERFLOW" and state == "ON":
            # Only log this message if it's different from last state
            if self.last_tap_status != "ON":
                self.log("Cannot turn tap ON during UNDERFLOW condition")
            return
            
        # Only log if there's an actual change
        if self.last_tap_status != state:
            self.tank.tap_status = state
            self.log(f"User set tap {state}")
            self.last_tap_status = state
            # Update display immediately to show tap status change
            self.draw_tap()
        else:
            self.tank.tap_status = state

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