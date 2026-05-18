"""
SUNRISE COMMUNITY — Water Tank Monitoring System
Clean card-based HMI  |  Secretary password: secretary123
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time, math

TANK_HEIGHT    = 10.0
OVERFLOW_LEVEL = 9.8
CRITICAL_LOW   = 1.0
WARNING_LOW    = 3.0
COMFORTABLE    = 6.0
INITIAL_LEVEL  = 5.5
MOTOR_RATE     = 0.15
TAP_RATE       = 0.05
SECRETARY_PASS = "secretary123"
VILLA_NAMES    = [f"Villa {i}" for i in range(1, 7)]

C = {
    "app_bg"      : "#F0F4F8",
    "sidebar_bg"  : "#1B3A5C",
    "sidebar_top" : "#14304E",
    "card"        : "#FFFFFF",
    "card2"       : "#F7FAFC",
    "divider"     : "#E2E8F0",
    "ok"          : "#27AE60",
    "ok_bg"       : "#E8F8F0",
    "warn"        : "#D68910",
    "warn_bg"     : "#FEF5E7",
    "crit"        : "#C0392B",
    "crit_bg"     : "#FDEDEC",
    "blue"        : "#2471A3",
    "blue_bg"     : "#EBF5FB",
    "water"       : "#2E86C1",
    "water2"      : "#1A5276",
    "pipe"        : "#5B8DB8",
    "pipe_hi"     : "#2471A3",
    "tank_frame"  : "#2471A3",
    "tank_top"    : "#1B3A5C",
    "ground"      : "#C8A96E",
    "ground2"     : "#A07845",
    "ug_bg"       : "#D6EAF8",
    "ug_border"   : "#2471A3",
    "motor_rim"   : "#E67E22",
    "motor_bg"    : "#FEF9F0",
    "villa_roof"  : "#C0392B",
    "villa_wallok": "#E8F8F0",
    "villa_wall"  : "#EBF5FB",
    "villa_door"  : "#7D4E24",
    "villa_win"   : "#AED6F1",
    "t1"          : "#1A252F",
    "t2"          : "#566573",
    "t3"          : "#010606",
    "t_sidebar"   : "#AAB7C4",
    "s_accent"    : "#2E86C1",
    "s_gold"      : "#D4AC0D",
}


# ══════════════════════════════════════════════
#  TANK MODEL
# ══════════════════════════════════════════════
class TankModel:
    def __init__(self):
        self.water_level     = INITIAL_LEVEL
        self.motor_status    = "OFF"
        self.usage_active    = True
        self.last_update     = time.time()
        self.manual_override = False
        self.inflow          = 0.0
        self.outflow         = 0.0

    def status(self):
        l = self.water_level
        if   l >= OVERFLOW_LEVEL: return "full",     "Tank is Full",           C["blue"],  C["blue_bg"]  if "blue_bg" in C else "#EBF5FB"
        elif l >= COMFORTABLE:    return "good",     "Plenty of Water",        C["ok"],    C["ok_bg"]
        elif l >= WARNING_LOW:    return "moderate", "Water Running Low",      C["warn"],  C["warn_bg"]
        elif l >  CRITICAL_LOW:   return "low",      "Very Little Water Left", C["crit"],  C["crit_bg"]
        else:                     return "critical", "Tank Almost Empty!",     C["crit"],  C["crit_bg"]

    def advice(self):
        k = self.status()[0]
        return {
            "full":     "Safe to do laundry, dishes, or garden watering.",
            "good":     "Safe to do laundry, dishes, or garden watering.",
            "moderate": "Limit heavy usage. Avoid garden watering.",
            "low":      "Please use water sparingly — only essentials!",
            "critical": "Emergency: Avoid all non-essential water use.",
        }[k]

    def update(self):
        now = time.time()
        dt  = now - self.last_update
        self.last_update = now
        self.inflow  = MOTOR_RATE if self.motor_status == "ON" else 0.0
        self.outflow = TAP_RATE   if self.usage_active         else 0.0
        self.water_level += (self.inflow - self.outflow) * dt
        self.water_level  = max(0.0, min(TANK_HEIGHT, self.water_level))
        if self.water_level >= OVERFLOW_LEVEL:
            self.motor_status    = "OFF"
            self.manual_override = False
        elif self.water_level <= CRITICAL_LOW and not self.manual_override:
            self.motor_status = "ON"


# ══════════════════════════════════════════════
#  REPORT ISSUE DIALOG
# ══════════════════════════════════════════════
class ReportDialog(tk.Toplevel):
    def __init__(self, parent, log_cb):
        super().__init__(parent)
        self.title("Report a Water Issue")
        self.resizable(False, False)
        self.configure(bg=C["card"])
        self.grab_set()
        self.log_cb = log_cb
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = 420, 370
        self.geometry(f"{w}x{h}+{px+(pw-w)//2}+{py+(ph-h)//2}")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["blue"], height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="🚰  Report a Water Issue",
                 font=("Segoe UI", 13, "bold"),
                 bg=C["blue"], fg="white").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self, bg=C["card"], padx=24)
        body.pack(fill="both", expand=True, pady=8)

        def lbl(t):
            tk.Label(body, text=t, font=("Segoe UI", 9),
                     bg=C["card"], fg=C["t2"], anchor="w").pack(fill="x", pady=(10,2))

        self.name_var  = tk.StringVar()
        self.villa_var = tk.StringVar(value="Villa 1")

        lbl("Your Name:")
        tk.Entry(body, textvariable=self.name_var, font=("Segoe UI", 10),
                 bg=C["card2"], fg=C["t1"], relief="solid", bd=1,
                 insertbackground=C["blue"]).pack(fill="x", ipady=5)

        lbl("Villa:")
        ttk.Combobox(body, textvariable=self.villa_var, values=VILLA_NAMES,
                     state="readonly", font=("Segoe UI", 10)).pack(fill="x")

        lbl("Issue Description:")
        self.issue_txt = tk.Text(body, height=3, font=("Segoe UI", 10),
                                 bg=C["card2"], fg=C["t1"],
                                 relief="solid", bd=1, wrap="word")
        self.issue_txt.pack(fill="x")

        bf = tk.Frame(self, bg=C["card"], padx=24)
        bf.pack(fill="x", pady=12)
        tk.Button(bf, text="Submit", bg=C["ok"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  padx=24, pady=7, cursor="hand2",
                  command=self._submit).pack(side="left", padx=(0, 8))
        tk.Button(bf, text="Cancel", bg=C["card2"], fg=C["t2"],
                  font=("Segoe UI", 10), relief="flat",
                  padx=24, pady=7, cursor="hand2",
                  command=self.destroy).pack(side="left")

    def _submit(self):
        name  = self.name_var.get().strip()
        villa = self.villa_var.get()
        issue = self.issue_txt.get("1.0", tk.END).strip()
        if not name:
            messagebox.showwarning("Missing", "Please enter your name.", parent=self); return
        if not issue:
            messagebox.showwarning("Missing", "Please describe the issue.", parent=self); return
        ref = "WR-2025-" + str(int(time.time()) % 9999)
        messagebox.showinfo("Submitted ✓",
            f"Thank you, {name}!\nVilla: {villa}\nRef: {ref}\n"
            f"Forwarded to secretary.", parent=self)
        self.log_cb(f"📋 Issue by {name} ({villa}): \"{issue[:40]}\" — Ref: {ref}")
        self.destroy()


# ══════════════════════════════════════════════
#  SECRETARY LOGIN DIALOG
# ══════════════════════════════════════════════
class SecretaryLoginDialog(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Secretary Login")
        self.resizable(False, False)
        self.configure(bg=C["card"])
        self.grab_set()
        self.on_success = on_success
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = 360, 250
        self.geometry(f"{w}x{h}+{px+(pw-w)//2}+{py+(ph-h)//2}")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["s_gold"], height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="🔐  Secretary Access",
                 font=("Segoe UI", 13, "bold"),
                 bg=C["s_gold"], fg="white").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self, bg=C["card"], padx=28)
        body.pack(fill="x", pady=20)
        tk.Label(body, text="Password:", font=("Segoe UI", 9),
                 bg=C["card"], fg=C["t2"]).pack(anchor="w", pady=(0, 4))
        self.pw_var = tk.StringVar()
        e = tk.Entry(body, textvariable=self.pw_var, show="●",
                     font=("Segoe UI", 12), bg=C["card2"], fg=C["t1"],
                     relief="solid", bd=1, insertbackground=C["blue"])
        e.pack(fill="x", ipady=6)
        e.bind("<Return>", lambda _: self._login())
        e.focus()

        self.err = tk.Label(self, text="", font=("Segoe UI", 9),
                            bg=C["card"], fg=C["crit"])
        self.err.pack()

        bf = tk.Frame(self, bg=C["card"], padx=28)
        bf.pack(fill="x", pady=8)
        tk.Button(bf, text="Login", bg=C["blue"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  padx=24, pady=7, cursor="hand2",
                  command=self._login).pack(side="left", padx=(0, 8))
        tk.Button(bf, text="Cancel", bg=C["card2"], fg=C["t2"],
                  font=("Segoe UI", 10), relief="flat",
                  padx=24, pady=7, cursor="hand2",
                  command=self.destroy).pack(side="left")

    def _login(self):
        if self.pw_var.get() == SECRETARY_PASS:
            self.on_success(); self.destroy()
        else:
            self.err.config(text="⚠  Incorrect password. Try again.")
            self.pw_var.set("")


# ══════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════
class WaterMonitorApp:
    def __init__(self, root):
        self.root  = root
        self.root.title("Sunrise Community — Water Tank Monitor")
        self.root.configure(bg=C["app_bg"])
        try:    self.root.state("zoomed")
        except: self.root.attributes("-zoomed", True)

        self.tank         = TankModel()
        self.is_secretary = False
        self._prev_motor  = self.tank.motor_status
        self._overflow_lg = False
        self._alert_shown = False
        self._flow_phase  = 0
        self._motor_ang   = 0
        self._blink       = True
        self._blink_ctr   = 0

        self._build_ui()
        self._loop()

    # ══════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════
    def _build_ui(self):
        # LEFT SIDEBAR
        sb = tk.Frame(self.root, bg=C["sidebar_bg"], width=245)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        self._build_sidebar(sb)

        # MAIN AREA
        main = tk.Frame(self.root, bg=C["app_bg"])
        main.pack(side="left", fill="both", expand=True)
        self._build_main(main)

    # ── SIDEBAR ───────────────────────────────
    def _build_sidebar(self, sb):
        # Logo
        top = tk.Frame(sb, bg=C["sidebar_top"])
        top.pack(fill="x")
        tk.Label(top, text="🏗", font=("Segoe UI", 32),
                 bg=C["sidebar_top"], fg="white").pack(pady=(22, 4))
        tk.Label(top, text="SUNRISE",
                 font=("Segoe UI", 14, "bold"),
                 bg=C["sidebar_top"], fg="white").pack()
        tk.Label(top, text="Water Mgmt System",
                 font=("Segoe UI", 8),
                 bg=C["sidebar_top"], fg=C["t_sidebar"]).pack(pady=(0, 18))

        # Role badge
        self._role_badge = tk.Label(sb, text="👤  Resident View",
                                    font=("Segoe UI", 9, "bold"),
                                    bg=C["sidebar_bg"], fg=C["t_sidebar"])
        self._role_badge.pack(pady=(14, 4))
        self._sdiv(sb)

        # Live readings
        tk.Label(sb, text="LIVE READINGS",
                 font=("Segoe UI", 8, "bold"),
                 bg=C["sidebar_bg"], fg=C["t_sidebar"]).pack(anchor="w", padx=16, pady=(10, 6))

        for lbl_txt, attr in [("Water Level", "_s_level"), ("Capacity", "_s_cap"),
                               ("Motor",       "_s_motor"), ("Mode",    "_s_mode")]:
            row = tk.Frame(sb, bg=C["sidebar_bg"])
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text=lbl_txt, font=("Segoe UI", 9),
                     bg=C["sidebar_bg"], fg=C["t_sidebar"], anchor="w").pack(side="left")
            v = tk.Label(row, text="—", font=("Segoe UI", 9, "bold"),
                         bg=C["sidebar_bg"], fg="white", anchor="e")
            v.pack(side="right")
            setattr(self, attr, v)

        self._sdiv(sb)

        # Resident section
        self._res_frame = tk.Frame(sb, bg=C["sidebar_bg"])
        self._res_frame.pack(fill="x")
        self._build_resident_section(self._res_frame)

        # Secretary section (hidden until login)
        self._sec_frame = tk.Frame(sb, bg=C["sidebar_bg"])
        self._build_secretary_section(self._sec_frame)

    def _build_resident_section(self, p):
        tk.Label(p, text="RESIDENT ACTIONS",
                 font=("Segoe UI", 8, "bold"),
                 bg=C["sidebar_bg"], fg=C["t_sidebar"]
                 ).pack(anchor="w", padx=16, pady=(10, 6))
        self._sbtn(p, "⚠  Report a Water Issue",
                   C["blue"], "white", self._open_report)
        self._sbtn(p, "🔐  Secretary Login",
                   C["sidebar_top"], C["t_sidebar"], self._secretary_login)

    def _build_secretary_section(self, p):
        tk.Label(p, text="⚙  SECRETARY CONTROLS",
                 font=("Segoe UI", 8, "bold"),
                 bg=C["sidebar_bg"], fg=C["s_gold"]
                 ).pack(anchor="w", padx=16, pady=(10, 4))

        tk.Label(p, text="Conservation Mode",
                 font=("Segoe UI", 8),
                 bg=C["sidebar_bg"], fg=C["t_sidebar"]
                 ).pack(anchor="w", padx=16, pady=(4, 2))
        self._cons_btn = tk.Button(p, text="Enable Conservation Mode",
                                   bg=C["ok"], fg="white",
                                   font=("Segoe UI", 9, "bold"), relief="flat",
                                   pady=9, cursor="hand2",
                                   command=self._toggle_conservation)
        self._cons_btn.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(p, text="Motor Pump Control",
                 font=("Segoe UI", 8),
                 bg=C["sidebar_bg"], fg=C["t_sidebar"]
                 ).pack(anchor="w", padx=16, pady=(4, 2))
        self._pump_info = tk.Label(p, text="Mode: Auto | Motor: Standby",
                                   font=("Segoe UI", 7),
                                   bg=C["sidebar_bg"], fg=C["t_sidebar"])
        self._pump_info.pack(anchor="w", padx=16)
        self._motor_btn = tk.Button(p, text="Turn Pump ON (Override)",
                                    bg=C["s_accent"], fg="white",
                                    font=("Segoe UI", 9, "bold"), relief="flat",
                                    pady=9, cursor="hand2",
                                    command=self._toggle_motor)
        self._motor_btn.pack(fill="x", padx=12, pady=(2, 6))

        self._sdiv(p)
        self._sbtn(p, "↩  Logout Secretary",
                   C["crit"], "white", self._secretary_logout)

    def _sbtn(self, parent, text, bg, fg, cmd):
        tk.Button(parent, text=text, bg=bg, fg=fg,
                  font=("Segoe UI", 9, "bold"), relief="flat",
                  pady=9, cursor="hand2", command=cmd
                  ).pack(fill="x", padx=12, pady=3)

    def _sdiv(self, p):
        tk.Frame(p, bg="#243E5A", height=1).pack(fill="x", padx=14, pady=6)

    def _build_main(self, main):
        # Top bar
        topbar = tk.Frame(main, bg=C["card"], height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Frame(topbar, bg=C["blue"], width=5).pack(side="left", fill="y")
        tk.Label(topbar, text="💧  Water Supply — Live Dashboard",
                 font=("Segoe UI", 14, "bold"),
                 bg=C["card"], fg=C["t1"]).pack(side="left", padx=16, pady=14)
        self._time_lbl = tk.Label(topbar, text="",
                                   font=("Segoe UI", 9),
                                   bg=C["card"], fg=C["t3"])
        self._time_lbl.pack(side="right", padx=20)

        # Status banner
        self._banner     = tk.Frame(main, height=52)
        self._banner.pack(fill="x")
        self._banner.pack_propagate(False)
        self._ban_icon   = tk.Label(self._banner, font=("Segoe UI", 18, "bold"))
        self._ban_icon.pack(side="left", padx=16)
        btxt = tk.Frame(self._banner)
        btxt.pack(side="left", fill="y", pady=6)
        self._ban_title  = tk.Label(btxt, font=("Segoe UI", 12, "bold"))
        self._ban_title.pack(anchor="w")
        self._ban_sub    = tk.Label(btxt, font=("Segoe UI", 8))
        self._ban_sub.pack(anchor="w")
        self._ban_adv    = tk.Label(self._banner, font=("Segoe UI", 8, "italic"),
                                     wraplength=280, justify="left")
        self._ban_adv.pack(side="right", padx=20)

        # Content: canvas + right panel
        content = tk.Frame(main, bg=C["app_bg"])
        content.pack(fill="both", expand=True, padx=10, pady=8)

        self.canvas = tk.Canvas(content, bg=C["app_bg"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw())

        # Right scrollable panel
        rp_outer = tk.Frame(content, bg=C["app_bg"], width=280)
        rp_outer.pack(side="right", fill="y", padx=(8, 0))
        rp_outer.pack_propagate(False)
        self._build_right_panel(rp_outer)

        # Event log
        log_wrap = tk.Frame(main, bg=C["app_bg"])
        log_wrap.pack(fill="x", padx=10, pady=(0, 8))
        hrow = tk.Frame(log_wrap, bg=C["app_bg"])
        hrow.pack(fill="x")
        tk.Label(hrow, text="Recent Notifications",
                 font=("Segoe UI", 10, "bold"),
                 bg=C["app_bg"], fg=C["t1"]).pack(side="left")
        tk.Frame(hrow, bg=C["divider"], height=1).pack(
            side="left", fill="x", expand=True, padx=8, pady=8)
        self._log_box = tk.Text(log_wrap, height=4,
                                 font=("Courier New", 9),
                                 bg=C["card"], fg=C["t1"],
                                 relief="flat", bd=1,
                                 state="disabled", wrap="word")
        self._log_box.pack(fill="x")

    # ── RIGHT PANEL ───────────────────────────
    def _build_right_panel(self, parent):

        def card(title, color):
            """Returns a body frame inside a white card with coloured title bar."""
            outer = tk.Frame(parent, bg=C["divider"], pady=1, padx=1)
            outer.pack(fill="x", pady=(0, 8))
            inner = tk.Frame(outer, bg=C["card"])
            inner.pack(fill="x")
            hdr = tk.Frame(inner, bg=color, height=30)
            hdr.pack(fill="x"); hdr.pack_propagate(False)
            tk.Label(hdr, text=title, font=("Segoe UI", 9, "bold"),
                     bg=color, fg="white").pack(side="left", padx=12, pady=5)
            body = tk.Frame(inner, bg=C["card"], padx=12, pady=8)
            body.pack(fill="x")
            return body

        def srow(parent, label, attr):
            row = tk.Frame(parent, bg=C["card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=("Segoe UI", 9),
                     bg=C["card"], fg=C["t2"], anchor="w").pack(side="left")
            v = tk.Label(row, text="—", font=("Segoe UI", 9, "bold"),
                         bg=C["card"], fg=C["t1"], anchor="e")
            v.pack(side="right")
            setattr(self, attr, v)

        # ── AT A GLANCE ───────────────────────
        ag = card("At a Glance", C["blue"])
        # 2-column big stats
        grid = tk.Frame(ag, bg=C["card"])
        grid.pack(fill="x", pady=(0, 8))
        for i, (lbl, ba, sa) in enumerate([
                ("Level",    "_ag_lev", "_ag_lev_s"),
                ("Capacity", "_ag_cap", "_ag_cap_s")]):
            col = tk.Frame(grid, bg=C["card"])
            col.grid(row=0, column=i, padx=10, sticky="w")
            tk.Label(col, text=lbl, font=("Segoe UI", 8),
                     bg=C["card"], fg=C["t2"]).pack(anchor="w")
            b = tk.Label(col, text="—", font=("Segoe UI", 18, "bold"),
                         bg=C["card"], fg=C["t1"]); b.pack(anchor="w")
            s = tk.Label(col, text="", font=("Segoe UI", 8),
                         bg=C["card"], fg=C["t3"]); s.pack(anchor="w")
            setattr(self, ba, b); setattr(self, sa, s)

        grid2 = tk.Frame(ag, bg=C["card"])
        grid2.pack(fill="x", pady=(0, 6))
        for i, (lbl, attr) in enumerate([("Pump", "_ag_pump"), ("Mode", "_ag_mode")]):
            col2 = tk.Frame(grid2, bg=C["card"])
            col2.grid(row=0, column=i, padx=10, sticky="w")
            tk.Label(col2, text=lbl, font=("Segoe UI", 8),
                     bg=C["card"], fg=C["t2"]).pack(anchor="w")
            v = tk.Label(col2, text="—", font=("Segoe UI", 11, "bold"),
                         bg=C["card"], fg=C["t1"]); v.pack(anchor="w")
            setattr(self, attr, v)

        tk.Frame(ag, bg=C["divider"], height=1).pack(fill="x", pady=(4, 8))
        tk.Label(ag, text="Can I use water?",
                 font=("Segoe UI", 9, "bold"),
                 bg=C["card"], fg=C["t1"]).pack(anchor="w")
        self._adv_lbl = tk.Label(ag, text="", font=("Segoe UI", 9),
                                   bg=C["card"], fg=C["t2"],
                                   wraplength=240, justify="left")
        self._adv_lbl.pack(anchor="w", pady=(2, 0))

        # ── MY CONTROLS (Secretary — shown after login) ───────
        self._ctrl_outer = tk.Frame(parent, bg=C["divider"], pady=1, padx=1)
        # Not packed until login

        ctrl_inner = tk.Frame(self._ctrl_outer, bg=C["card"])
        ctrl_inner.pack(fill="x")
        ctrl_hdr = tk.Frame(ctrl_inner, bg=C["s_gold"], height=30)
        ctrl_hdr.pack(fill="x"); ctrl_hdr.pack_propagate(False)
        tk.Label(ctrl_hdr, text="My Controls",
                 font=("Segoe UI", 9, "bold"),
                 bg=C["s_gold"], fg="white").pack(side="left", padx=12, pady=5)

        ctrl_body = tk.Frame(ctrl_inner, bg=C["card"], padx=12, pady=8)
        ctrl_body.pack(fill="x")

        tk.Label(ctrl_body, text="Conservation Mode",
                 font=("Segoe UI", 9, "bold"),
                 bg=C["card"], fg=C["t1"]).pack(anchor="w")
        self._rp_cons_btn = tk.Button(ctrl_body, text="Enable Conservation Mode",
                                       bg=C["card"], fg=C["t1"],
                                       font=("Segoe UI", 9), relief="solid", bd=1,
                                       pady=7, cursor="hand2",
                                       command=self._toggle_conservation)
        self._rp_cons_btn.pack(fill="x", pady=(4, 10))

        tk.Frame(ctrl_body, bg=C["divider"], height=1).pack(fill="x", pady=4)

        tk.Label(ctrl_body, text="Secretary: Pump Control",
                 font=("Segoe UI", 9, "bold"),
                 bg=C["card"], fg=C["t1"]).pack(anchor="w", pady=(6, 2))
        self._rp_pump_info = tk.Label(ctrl_body, text="Mode: Auto | Pump: Standby",
                                       font=("Segoe UI", 8),
                                       bg=C["card"], fg=C["t3"])
        self._rp_pump_info.pack(anchor="w", pady=(0, 4))
        self._rp_motor_btn = tk.Button(ctrl_body,
                                        text="Turn Pump ON\n(Override)",
                                        bg=C["blue"], fg="white",
                                        font=("Segoe UI", 9, "bold"), relief="flat",
                                        pady=8, cursor="hand2",
                                        command=self._toggle_motor)
        self._rp_motor_btn.pack(fill="x", pady=(0, 4))

        # ── FLOW RATES ────────────────────────
        fl = card("Flow Rates", C["water2"])
        srow(fl, "Inflow (motor):",  "_fl_in")
        srow(fl, "Outflow (usage):", "_fl_out")
        srow(fl, "Net change:",      "_fl_net")

        # ── TANK DETAILS ──────────────────────
        td = card("Tank Details", "#5D6D7E")
        srow(td, "Max height:",    "_td_h")
        srow(td, "Current level:", "_td_lv")
        srow(td, "Overflow at:",   "_td_ov")
        srow(td, "Critical at:",   "_td_cr")
        self._td_h.config(text=f"{TANK_HEIGHT:.1f} m")
        self._td_ov.config(text=f"{OVERFLOW_LEVEL:.1f} m")
        self._td_cr.config(text=f"{CRITICAL_LOW:.1f} m")

        # ── REPORT ISSUE ──────────────────────
        ri_outer = tk.Frame(parent, bg=C["divider"], pady=1, padx=1)
        ri_outer.pack(fill="x", pady=(0, 8))
        ri_inner = tk.Frame(ri_outer, bg=C["card"], padx=12, pady=10)
        ri_inner.pack(fill="x")
        tk.Button(ri_inner, text="Report a Water Issue  ↗",
                  bg=C["card"], fg=C["blue"],
                  font=("Segoe UI", 9, "bold"), relief="solid", bd=1,
                  pady=7, cursor="hand2",
                  command=self._open_report).pack(fill="x")

    # ══════════════════════════════════════════
    #  DIAGRAM DRAWING
    # ══════════════════════════════════════════
    def _draw(self):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width(); H = c.winfo_height()
        if W < 50 or H < 50: return

        lvl      = self.tank.water_level
        pct      = lvl / TANK_HEIGHT
        key      = self.tank.status()[0]
        motor_on = self.tank.motor_status == "ON"
        flow_on  = self.tank.usage_active and lvl > 0.01
        ph       = self._flow_phase
        ang      = self._motor_ang

        wcol = (C["water"]  if key in ("full","good") else
                C["blue"]   if key == "moderate"       else C["crit"])

        PW = 7; BW = 4

        # Background + subtle grid
        c.create_rectangle(0, 0, W, H, fill=C["app_bg"], outline="")
        for gx in range(0, W, 50):
            c.create_line(gx, 0, gx, H, fill="#E4EBF1", width=1)
        for gy in range(0, H, 50):
            c.create_line(0, gy, W, gy, fill="#E4EBF1", width=1)

        # ── LAYOUT ─────────────────────────────
        ug_w = W*0.13; ug_h = H*0.09
        ug_x = W*0.02; gnd_y = H*0.78
        ug_y = gnd_y + H*0.022

        mr    = min(W, H)*0.038
        mtr_x = ug_x + ug_w + W*0.06
        mtr_y = ug_y + ug_h/2

        gap   = W*0.07
        bw    = W*0.15; bh = H*0.42
        bx    = mtr_x + mr + gap
        by    = H*0.04
        tw_cx = bx + bw/2

        leg_h   = H*0.11
        leg_top = by + bh
        leg_bot = leg_top + leg_h

        inlet_x = bx
        inlet_y = by + bh*0.06
        above_y = by - H*0.04

        n       = 6
        vw      = W*0.10; vh = H*0.073; vgap = H*0.009
        vx      = W - vw - W*0.008
        dist_x  = vx - W*0.045

        bot_y    = by + bh
        dhead_y  = bot_y + PW
        v_top_y  = dhead_y + H*0.012
        dist_bot = v_top_y + (n-1)*(vh+vgap) + vh/2 + 4

        # ── GROUND ─────────────────────────────
        c.create_rectangle(0, gnd_y, W*0.46, gnd_y+6,
                           fill=C["ground"], outline="")
        c.create_rectangle(0, gnd_y+6, W*0.46, gnd_y+14,
                           fill=C["ground2"], outline="")
        c.create_line(0, gnd_y, W*0.46, gnd_y,
                      fill="#B09040", width=1, dash=(6, 4))
        c.create_text(ug_x+2, gnd_y-8, text="ground level",
                      fill="#A07845", font=("Segoe UI", 7), anchor="w")

        # ── UNDERGROUND RESERVOIR ──────────────
        c.create_rectangle(ug_x, ug_y, ug_x+ug_w, ug_y+ug_h,
                           fill=C["ug_bg"], outline=C["ug_border"], width=2)
        uw = ug_h*0.70*min(1.0, pct*1.3)
        if uw > 2:
            c.create_rectangle(ug_x+3, ug_y+ug_h-uw,
                               ug_x+ug_w-3, ug_y+ug_h-3,
                               fill=C["water"], outline="")
        c.create_text(ug_x+ug_w/2, ug_y+ug_h/2,
                      text="Underground\nReservoir",
                      fill=C["t1"], font=("Segoe UI", 7, "bold"), justify="center")

        # ── MOTOR ──────────────────────────────
        if motor_on:
            for gr in (mr+9, mr+5, mr+2):
                c.create_oval(mtr_x-gr, mtr_y-gr, mtr_x+gr, mtr_y+gr,
                              fill="", outline=C["motor_rim"], width=1)
        c.create_oval(mtr_x-mr, mtr_y-mr, mtr_x+mr, mtr_y+mr,
                      fill=C["motor_bg"], outline=C["motor_rim"], width=2)
        bc = C["motor_rim"] if motor_on else C["t3"]
        for i in range(3):
            a = math.radians(ang + i*120)
            c.create_line(mtr_x, mtr_y,
                          mtr_x + mr*0.70*math.cos(a),
                          mtr_y + mr*0.70*math.sin(a),
                          fill=bc, width=3, capstyle="round")
        c.create_oval(mtr_x-4, mtr_y-4, mtr_x+4, mtr_y+4,
                      fill=C["motor_rim"], outline="")
        c.create_text(mtr_x, mtr_y+mr+12,
                      text="Motor Pump",
                      fill=C["t1"], font=("Segoe UI", 8, "bold"))
        mc = C["ok"] if motor_on else C["crit"]
        c.create_text(mtr_x, mtr_y+mr+24,
                      text="● Running" if motor_on else "○ Standby",
                      fill=mc, font=("Segoe UI", 8))

        # ── WATER TOWER ────────────────────────
        lxs = [bx + bw*f for f in (0.12, 0.34, 0.66, 0.88)]
        for lx in lxs:
            c.create_line(lx, leg_top, lx, leg_bot,
                          fill=C["tank_frame"], width=5)
        for bf in (0.30, 0.65):
            ly2 = leg_top + leg_h*bf
            c.create_line(lxs[0], ly2, lxs[-1], ly2,
                          fill=C["pipe"], width=2)
        c.create_line(lxs[0], leg_top, lxs[-1], leg_bot,
                      fill=C["pipe"], width=2)
        c.create_line(lxs[-1], leg_top, lxs[0], leg_bot,
                      fill=C["pipe"], width=2)

        # Tank drop shadow
        c.create_rectangle(bx+4, by+4, bx+bw+4, by+bh+4,
                           fill="#D4D9DF", outline="")
        # Tank body
        c.create_rectangle(bx, by, bx+bw, by+bh,
                           fill="#F0F6FC", outline=C["tank_frame"], width=2)

        # Water fill
        wfh = bh * pct
        wt  = by + bh - wfh
        if wfh > 2:
            c.create_rectangle(bx+2, wt, bx+bw-2, by+bh-2,
                               fill=wcol, outline="")
            if flow_on or motor_on:
                for wo in range(0, int(bw)-4, 12):
                    wy2 = wt + 2.5*math.sin((wo + ph*3)*0.2)
                    c.create_arc(bx+2+wo, wy2-4, bx+2+wo+12, wy2+4,
                                 start=0, extent=180,
                                 outline="blue", style="arc", width=1)

        # Zone strip (left edge)
        for zlo, zhi, zcol in [(0,1,C["crit"]),(1,3,C["blue"]),
                                (3,6,C["blue"]),(6,9.8,C["ok"]),(9.8,10,C["water2"])]:
            zy1 = by + bh - (zhi/TANK_HEIGHT)*bh
            zy2 = by + bh - (zlo/TANK_HEIGHT)*bh
            c.create_rectangle(bx-7, zy1, bx-2, zy2, fill=zcol, outline="")

        # Level lines
        for ml, mlbl in [(9.8,"9.8m"),(6.0,"6.0m"),(3.0,"3.0m"),(1.0,"1.0m")]:
            ly3 = by + bh - (ml/TANK_HEIGHT)*bh
            c.create_line(bx, ly3, bx+8, ly3,
                          fill=C["t3"], width=2, dash=(3, 3))
            c.create_text(bx-9, ly3, text=mlbl,
                          fill=C["t3"], font=("Segoe UI", 8), anchor="e")

        # Dome
        c.create_arc(bx, by-bh*0.05, bx+bw, by+bh*0.05,
                     start=0, extent=180,
                     fill=C["tank_top"], outline=C["tank_frame"], width=2)
        # Railing
        rl = by - bh*0.022
        c.create_line(bx-3, rl, bx+bw+3, rl,
                      fill=C["tank_frame"], width=3)
        for rx in range(int(bx), int(bx+bw)+1, 12):
            c.create_line(rx, rl, rx, by, fill=C["tank_frame"], width=1)

        # Text inside tank
        ty  = max(wt+16, by+16)
        tc  = "white" if wfh > 22 else C["t1"]
       

        # ── PIPES ──────────────────────────────

        # P1: Underground → Motor
        c.create_rectangle(ug_x+ug_w-1, mtr_y-PW//2,
                           mtr_x-mr+1, mtr_y+PW//2,
                           fill=C["pipe"], outline="")
        if motor_on:
            self._anim_h(c, ug_x+ug_w, mtr_y, mtr_x-mr, mtr_y, ph)

        # P2: Motor → up → elbow above tank → down into top-left
        mt_y = mtr_y - mr
        # a) vertical up
        c.create_rectangle(mtr_x-PW//2, mt_y, mtr_x+PW//2, above_y,
                           fill=C["pipe"], outline="")
        # b) horizontal elbow
        ex0 = min(mtr_x, inlet_x); ex1 = max(mtr_x, inlet_x)
        c.create_rectangle(ex0-PW//2, above_y-PW//2,
                           ex1+PW//2, above_y+PW//2,
                           fill=C["pipe"], outline="")
        # c) vertical down into tank
        c.create_rectangle(inlet_x-PW//2, above_y,
                           inlet_x+PW//2, inlet_y,
                           fill=C["pipe"], outline="")

        # Supply label
        c.create_text((mtr_x+inlet_x)/2, above_y-11,
                      text="Motor Supply",
                      fill=C["pipe_hi"] if motor_on else C["t3"],
                      font=("Segoe UI", 7, "bold"))

        # Inlet nozzle (top-left of tank)
        nc = C["water"] if motor_on else C["pipe"]
        c.create_rectangle(inlet_x-2, inlet_y-6, inlet_x+12, inlet_y+6,
                           fill=nc, outline=C["tank_frame"], width=1)
        if motor_on and self._blink:
            c.create_polygon([inlet_x+12, inlet_y,
                               inlet_x+2, inlet_y-5,
                               inlet_x+2, inlet_y+5],
                              fill=C["ok"], outline="")

        if motor_on:
            self._anim_v(c, mtr_x, mt_y, mtr_x, above_y, ph, up=True)
            self._anim_h(c, mtr_x, above_y, inlet_x, above_y, ph, rev=True)
            self._anim_v(c, inlet_x, above_y, inlet_x, inlet_y, ph, up=False)

        # P3: Tank bottom → header → dist pipe
        c.create_rectangle(tw_cx-PW//2, bot_y,
                           dist_x+PW//2, bot_y+PW,
                           fill=C["pipe"], outline="")
        c.create_text((tw_cx+dist_x)/2, bot_y-8,
                      text="Supply header",
                      fill=C["t3"], font=("Segoe UI", 7))
        if flow_on:
            self._anim_h(c, tw_cx, bot_y+PW//2, dist_x, bot_y+PW//2, ph)

        # P4: Vertical distribution pipe
        c.create_rectangle(dist_x-PW//2, dhead_y, dist_x+PW//2, dist_bot,
                           fill=C["pipe"], outline="")
        c.create_text(dist_x-28, (dhead_y+dist_bot)/2,
                      text="Main\nDist.\nPipe",
                      fill=C["t3"], font=("Segoe UI", 7), justify="center")
        if flow_on:
            self._anim_v(c, dist_x, dhead_y, dist_x, dist_bot, ph)

        # Flow labels
        
        # ── VILLAS ─────────────────────────────
        for vi, vname in enumerate(VILLA_NAMES):
            vy  = v_top_y + vi*(vh+vgap)
            vcx = vx + vw/2
            rh  = vh*0.35; wh_v = vh*0.65
            wy  = vy + rh
            my  = wy + wh_v*0.32

            # Branch pipe
            c.create_line(dist_x, my, vx, my,
                          fill=C["pipe"], width=BW, capstyle="butt")
            c.create_oval(dist_x-BW//2-1, my-BW//2-1,
                          dist_x+BW//2+1, my+BW//2+1,
                          fill=C["pipe_hi"], outline="")
            if flow_on:
                self._anim_h(c, dist_x+2, my, vx-2, my, ph)

            wfill = C["villa_wallok"] if flow_on else C["villa_wall"]
            wout  = C["ok"] if flow_on else C["crit"]

            # Shadow
            c.create_rectangle(vx+3, wy+3, vx+vw+3, vy+vh+3,
                               fill="#D4D9DF", outline="")
            # Wall
            c.create_rectangle(vx, wy, vx+vw, vy+vh,
                               fill=wfill, outline=C["t3"], width=1)
            # Roof
            c.create_polygon([vx-2, wy, vcx, vy, vx+vw+2, wy],
                              fill=C["villa_roof"], outline="#922B21", width=1)
            # Door
            dw=vw*0.22; dh=wh_v*0.40
            dx=vcx-dw/2; dy=vy+vh-dh
            c.create_rectangle(dx, dy, dx+dw, vy+vh,
                               fill=C["villa_door"], outline="#3E2010", width=1)
            # Windows
            ww=vw*0.18; wh_w=wh_v*0.24
            wwy=wy+wh_v*0.12
            for wxo in (vw*0.07, vw*0.74):
                c.create_rectangle(vx+wxo, wwy, vx+wxo+ww, wwy+wh_w,
                                   fill=C["villa_win"] if flow_on else "#D5D8DC",
                                   outline=C["t3"], width=1)
            # Pipe entry dot
            c.create_oval(vx-3, my-3, vx+3, my+3,
                          fill=C["water"] if flow_on else C["pipe"],
                          outline=C["pipe_hi"], width=1)
            # Labels
            c.create_text(vcx, wy+wh_v*0.22, text=vname,
                          font=("Segoe UI", 7, "bold"), fill=C["t1"])
            c.create_text(vcx, vy+vh+8,
                          text="● Active" if flow_on else "○ No flow",
                          font=("Segoe UI", 6), fill=wout)

    # ── ANIMATION HELPERS ─────────────────────
    def _anim_h(self, c, x1, y, x2, y2, ph, rev=False):
        L = abs(x2-x1)
        if L < 2: return
        S, G = 10, 5; step = S+G
        nx1, nx2 = (x1, x2) if x2 >= x1 else (x2, x1)
        off = step-(ph*2)%step if rev else (ph*2)%step
        t = off
        while t < L:
            c.create_line(nx1+t, y, min(nx2, nx1+t+S), y,
                          fill=C["water"], width=3, capstyle="round")
            t += step

    def _anim_v(self, c, x, y1, x2, y2, ph, up=False):
        L = abs(y2-y1)
        if L < 2: return
        S, G = 10, 5; step = S+G
        ny1, ny2 = (y1, y2) if y2 >= y1 else (y2, y1)
        off = step-(ph*2)%step if up else (ph*2)%step
        t = off
        while t < L:
            c.create_line(x, ny1+t, x, min(ny2, ny1+t+S),
                          fill=C["water"], width=3, capstyle="round")
            t += step

    # ── ROLE MANAGEMENT ───────────────────────
    def _secretary_login(self):
        SecretaryLoginDialog(self.root, self._on_sec_success)

    def _on_sec_success(self):
        self.is_secretary = True
        self._role_badge.config(text="🔑  Secretary Mode", fg=C["s_gold"])
        self._res_frame.pack_forget()
        self._sec_frame.pack(fill="x")
        self._ctrl_outer.pack(fill="x", pady=(0, 8))
        self._log("🔑 Secretary logged in.")

    def _secretary_logout(self):
        self.is_secretary = False
        self._role_badge.config(text="👤  Resident View", fg=C["t_sidebar"])
        self._sec_frame.pack_forget()
        self._res_frame.pack(fill="x")
        self._ctrl_outer.pack_forget()
        self._log("🔓 Secretary logged out.")

    # ── CONTROLS ──────────────────────────────
    def _toggle_conservation(self):
        if self.tank.usage_active:
            self.tank.usage_active = False
            for b in (self._cons_btn, self._rp_cons_btn):
                b.config(text="Disable Conservation Mode", bg=C["warn"])
            self._rp_cons_btn.config(fg="white")
            self._log("🌿 Conservation Mode enabled.")
        else:
            self.tank.usage_active = True
            self._cons_btn.config(text="Enable Conservation Mode", bg=C["ok"])
            self._rp_cons_btn.config(text="Enable Conservation Mode",
                                     bg=C["card"], fg=C["t1"])
            self._log("▶ Conservation Mode disabled.")

    def _toggle_motor(self):
        if self.tank.water_level >= OVERFLOW_LEVEL:
            messagebox.showwarning("Cannot Start",
                                   "Tank is full. Motor cannot be started.")
            return
        self.tank.manual_override = True
        if self.tank.motor_status == "ON":
            self.tank.motor_status = "OFF"
            self._log("🔧 Secretary: Motor turned OFF (manual override).")
        else:
            self.tank.motor_status = "ON"
            self._log("🔧 Secretary: Motor turned ON (manual override).")

    def _open_report(self):
        ReportDialog(self.root, self._log)

    # ── LOGGING ───────────────────────────────
    def _log(self, msg):
        t = time.strftime("%I:%M %p")
        self._log_box.config(state="normal")
        self._log_box.insert(tk.END, f"[{t}] {msg}\n")
        self._log_box.see(tk.END)
        self._log_box.config(state="disabled")

    # ══════════════════════════════════════════
    #  MAIN LOOP
    # ══════════════════════════════════════════
    def _loop(self):
        self.tank.update()
        key, label, color, bg_col = self.tank.status()
        lvl  = self.tank.water_level
        pct  = lvl / TANK_HEIGHT * 100
        mon  = self.tank.motor_status == "ON"
        mode = "Manual" if self.tank.manual_override else "Auto"

        # Animations
        if mon:
            self._motor_ang  = (self._motor_ang + 14) % 360
        if self.tank.usage_active or mon:
            self._flow_phase = (self._flow_phase + 1) % 60
        self._blink_ctr = (self._blink_ctr + 1) % 8
        self._blink     = self._blink_ctr < 5

        # Auto-log motor state changes
        if self.tank.motor_status != self._prev_motor:
            self._log("🔄 AUTO: Motor started (≤1.0 m)."
                      if self.tank.motor_status == "ON"
                      else "⏹ AUTO: Motor stopped (≥9.8 m).")
            self._prev_motor = self.tank.motor_status

        if key == "full" and not self._overflow_lg:
            self._overflow_lg = True
            self._log("💧 SYSTEM: Tank reached 9.8 m. Motor auto-stopped.")
        elif key != "full":
            self._overflow_lg = False

        if key == "critical" and not self._alert_shown:
            self._alert_shown = True
            self._log("🚨 ALERT: Tank critically low. Motor auto-started.")
            messagebox.showwarning("Water Alert",
                "Community tank is almost empty!\n"
                "Motor has been automatically started.\n"
                "Please avoid all non-essential water use.")
        elif key != "critical":
            self._alert_shown = False

        # ── Banner ────────────────────────────
        icons = {"full":"💧","good":"✓","moderate":"⚠","low":"▼","critical":"🚨"}
        self._banner.config(bg=bg_col)
        self._ban_icon.config(text=icons.get(key,"?"), bg=bg_col, fg=color)
        self._ban_title.config(text=label, bg=bg_col, fg=color)
        # btxt container doesn't get direct config — just set its children
        for w in self._ban_title.master.winfo_children():
            w.config(bg=bg_col)
        self._ban_title.master.config(bg=bg_col)
        self._ban_sub.config(
            text=f"Level: {lvl:.2f} m  ·  Capacity: {pct:.0f}%  ·  Motor: {'ON' if mon else 'OFF'}",
            bg=bg_col, fg=C["t2"])
        self._ban_adv.config(text=self.tank.advice(), bg=bg_col, fg=C["t2"])

        # ── Sidebar ───────────────────────────
        self._s_level.config(text=f"{lvl:.2f} m")
        self._s_cap.config(text=f"{pct:.0f}%",
                           fg=C["ok"] if pct > 30 else C["crit"])
        self._s_motor.config(text="Running" if mon else "Standby",
                             fg=C["ok"] if mon else C["crit"])
        self._s_mode.config(text=mode)

        # ── At a Glance ───────────────────────
        self._ag_lev.config(text=f"{lvl:.2f} m", fg=color)
        self._ag_lev_s.config(text=f"of {TANK_HEIGHT:.0f} m max")
        self._ag_cap.config(text=f"{pct:.0f}%", fg=color)
        self._ag_cap_s.config(text="capacity")
        self._ag_pump.config(text="Running" if mon else "Standby",
                             fg=C["ok"] if mon else C["crit"])
        self._ag_mode.config(text=mode, fg=C["t1"])
        self._adv_lbl.config(text=self.tank.advice())

        # ── Flow rates ────────────────────────
        net = self.tank.inflow - self.tank.outflow
        self._fl_in.config(text=f"{self.tank.inflow:.2f} m/s",
                           fg=C["ok"] if self.tank.inflow > 0 else C["t3"])
        self._fl_out.config(text=f"{self.tank.outflow:.2f} m/s",
                            fg=C["warn"] if self.tank.outflow > 0 else C["t3"])
        self._fl_net.config(text=f"{net:+.2f} m/s",
                            fg=C["ok"] if net > 0 else C["crit"] if net < 0 else C["t3"])

        # ── Tank details ──────────────────────
        self._td_lv.config(text=f"{lvl:.2f} m", fg=color)

        # ── Secretary controls ────────────────
        if self.is_secretary:
            btxt = f"Turn Pump {'OFF' if mon else 'ON'} (Override)"
            btxt2 = f"Turn Pump {'OFF' if mon else 'ON'}\n(Override)"
            bc = C["crit"] if mon else C["blue"]
            self._motor_btn.config(text=btxt, bg=bc)
            self._rp_motor_btn.config(text=btxt2, bg=bc)
            info = f"Mode: {mode} | Pump: {'Running' if mon else 'Standby'}"
            self._pump_info.config(text=info)
            self._rp_pump_info.config(text=info)

        self._time_lbl.config(text=time.strftime("Updated: %I:%M:%S %p"))
        self._draw()
        self.root.after(120, self._loop)


if __name__ == "__main__":
    root = tk.Tk()
    WaterMonitorApp(root)
    root.mainloop()
