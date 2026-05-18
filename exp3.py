"""
=============================================================================
GOAL-DIRECTED DESIGN (GDD) - COMMUNITY WATER TANK MONITORING SYSTEM
=============================================================================

GDD RESEARCH FOUNDATION
------------------------
PRIMARY USER: Community Residents (not admins or technicians)

PERSONAS:
  1. Riya Sharma (32) — Working professional, busy mom, uses app on the go.
     Mental Model: "Just tell me if water is available or not. I don't care how."
     Goals: Know before she starts cooking/bathing if water will last.

  2. Ramesh Iyer (67) — Retired elder, low tech comfort, poor eyesight.
     Mental Model: "Simple colors and big text. Don't confuse me."
     Goals: Not be surprised by empty taps. Feel secure.

  3. Priya Nair (28) — Environmentally conscious, wants to save water.
     Mental Model: "Show me if I'm using too much. Help me be responsible."
     Goals: Track usage, reduce waste, contribute to community.

GOAL HIERARCHY (Cooper's GDD Framework):
  Final Goals    → "Water will be available when I need it."
  Experience Goals → "I feel informed and in control, not anxious."
  Life Goals     → "I am a responsible, aware community member."

KEY SCENARIOS:
  S1 - Morning Rush (7-9 AM): Riya checks before filling buckets.
       System must proactively warn if water won't last morning peak.
  S2 - Night Conservation: Ramesh wants to know if it's safe to run dishwasher.
       System uses plain language: "Plenty of water. Safe to use."
  S3 - Emergency Alert: Water critically low. System must guide, not panic.
       Instead of "CRITICAL UNDERFLOW" → "Tank is almost empty! Pump starting."

DESIGN PRINCIPLES APPLIED:
  - Plain language over technical jargon ("Tank is Full" vs "OVERFLOW DETECTED")
  - Proactive, not reactive — predict and warn before crisis
  - Resident-centric actions only (report issue, see usage forecast)
  - Color + icon + text (multi-modal for accessibility / elder users)
  - No raw numbers as primary info — translate to meaning
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import math

# ─────────────────────────────────────────────
# SYSTEM CONSTANTS
# ─────────────────────────────────────────────
TANK_HEIGHT    = 10.0
OVERFLOW_LEVEL = 9.8
CRITICAL_LOW   = 1.0
WARNING_LOW    = 3.0
COMFORTABLE    = 6.0
INITIAL_LEVEL  = 5.5

MOTOR_FLOW_RATE = 0.15   # m/s inflow when pump ON
TAP_FLOW_RATE   = 0.05   # m/s outflow (community usage)


# ─────────────────────────────────────────────
# COLOUR PALETTE  (calm, accessible)
# ─────────────────────────────────────────────
C = {
    "bg"          : "#F0F4F8",
    "panel"       : "#FFFFFF",
    "sidebar"     : "#1E2D40",
    "sidebar_txt" : "#A8C0D6",
    "accent"      : "#2D9CDB",

    "ok_green"    : "#27AE60",
    "warn_orange" : "#F39C12",
    "crit_red"    : "#E74C3C",
    "info_blue"   : "#2980B9",

    "water_ok"    : "#5DADE2",
    "water_warn"  : "#F0B429",
    "water_crit"  : "#E74C3C",
    "tank_body"   : "#D5D8DC",
    "tank_edge"   : "#ABB2B9",

    "txt_dark"    : "#1A252F",
    "txt_mid"     : "#566573",
    "txt_light"   : "#AEB6BF",
}


# ─────────────────────────────────────────────────────────
# TANK MODEL  (unchanged physics, GDD-friendly state labels)
# ─────────────────────────────────────────────────────────
class TankModel:
    def __init__(self):
        self.water_level    = INITIAL_LEVEL
        self.motor_status   = "OFF"
        self.usage_active   = True          # community tap open
        self.last_update    = time.time()
        self.manual_override = False        # Secretary override flag

    # ── Translate raw level → resident-friendly status ──────────────────
    def resident_status(self):
        lvl = self.water_level
        if lvl >= OVERFLOW_LEVEL:
            return "full",    "Tank is Full",          C["ok_green"]
        elif lvl >= COMFORTABLE:
            return "good",    "Plenty of Water",       C["ok_green"]
        elif lvl >= WARNING_LOW:
            return "moderate","Water is Running Low",  C["warn_orange"]
        elif lvl > CRITICAL_LOW:
            return "low",     "Very Little Water Left",C["crit_red"]
        else:
            return "critical","Tank Almost Empty!",    C["crit_red"]

    # ── How long until critical? (plain language) ────────────────────────
    def time_forecast(self):
        inflow  = MOTOR_FLOW_RATE if self.motor_status == "ON" else 0
        outflow = TAP_FLOW_RATE   if self.usage_active         else 0
        net     = inflow - outflow

        if net >= 0:
            if self.water_level >= COMFORTABLE:
                return "Stable — no concerns right now", C["ok_green"]
            else:
                return "Pump is refilling the tank",     C["info_blue"]
        else:
            dist_to_crit = self.water_level - CRITICAL_LOW
            if dist_to_crit <= 0:
                return "Critically low now!",            C["crit_red"]
            secs  = dist_to_crit / abs(net)
            mins  = secs / 60
            if mins < 5:
                return f"⚠ Only ~{mins:.0f} min of water left!", C["crit_red"]
            elif mins < 20:
                return f"About {mins:.0f} min before low alert",  C["warn_orange"]
            else:
                hrs = mins / 60
                if hrs >= 1:
                    return f"~{hrs:.1f} hrs of water available",  C["ok_green"]
                return f"~{mins:.0f} min of water available",     C["ok_green"]

    # ── Usage advice for Scenario S2 ─────────────────────────────────────
    def usage_advice(self):
        key, _, _ = self.resident_status()
        if key in ("full", "good"):
            return "✔  Safe to do laundry, dishes, or garden watering."
        elif key == "moderate":
            return "⚠  Limit heavy usage. Avoid garden watering."
        elif key == "low":
            return "✖  Please use water sparingly — only essentials!"
        else:
            return "✖  Emergency: Avoid all non-essential water use."

    # ── Physics update ────────────────────────────────────────────────────
    def update(self):
        now = time.time()
        dt  = now - self.last_update
        self.last_update = now

        inflow  = MOTOR_FLOW_RATE if self.motor_status == "ON" else 0
        outflow = TAP_FLOW_RATE   if self.usage_active         else 0
        self.water_level += (inflow - outflow) * dt
        self.water_level  = max(0, min(TANK_HEIGHT, self.water_level))

        # Automation: safety rules
        # Safety limits always apply even in manual override
        if self.water_level >= OVERFLOW_LEVEL:
            self.motor_status   = "OFF"   # must stop — tank full
            self.manual_override = False
        elif self.water_level <= CRITICAL_LOW and not self.manual_override:
            self.motor_status = "ON"      # auto-start if no secretary override
        elif not self.manual_override:
            pass  # auto mode: secretary hasn't intervened, leave as-is

        return inflow, outflow


# ─────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────
class GDDResidentApp:
    def __init__(self, root):
        self.root  = root
        self.root.title("Sunrise Community — Water Status")
        self.root.configure(bg=C["bg"])
        # Maximize on startup — works cross-platform
        try:
            self.root.state("zoomed")          # Windows / some Linux WMs
        except Exception:
            self.root.attributes("-zoomed", True)  # Linux fallback

        self.tank          = TankModel()
        self.alert_shown   = False
        self.event_log     = []

        # State tracking for auto-logging
        self._prev_motor   = self.tank.motor_status
        self._prev_usage   = self.tank.usage_active
        self._overflow_logged = False

        self._build_ui()
        self._loop()

    # ══════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════
    def _build_ui(self):
        # ── Sidebar ─────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=C["sidebar"], width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🏘", font=("Segoe UI Emoji", 30),
                 bg=C["sidebar"], fg="white").pack(pady=(30, 5))
        tk.Label(sidebar, text="SUNRISE\nCOMMUNITY",
                 font=("Helvetica", 12, "bold"),
                 bg=C["sidebar"], fg="white", justify="center").pack()

        tk.Label(sidebar, text="────────────────",
                 bg=C["sidebar"], fg=C["sidebar_txt"]).pack(pady=15)

        # Persona selector (GDD demonstration)
        tk.Label(sidebar, text="────────────────",
                 bg=C["sidebar"], fg=C["sidebar_txt"]).pack(pady=10)
        tk.Label(sidebar, text="Logged in as:",
                 bg=C["sidebar"], fg=C["sidebar_txt"],
                 font=("Helvetica", 9)).pack()

        self.persona_var = tk.StringVar(value="Riya Sharma (Flat 4B)")
        personas = ["Riya Sharma (Flat 4B)", "Ramesh Iyer (Flat 2A)", "Priya Nair (Flat 6C)"]
        persona_menu = ttk.Combobox(sidebar, textvariable=self.persona_var,
                                    values=personas, state="readonly", width=22)
        persona_menu.pack(padx=10, pady=5)

        # ── Main Area ────────────────────────────────────────
        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(main, bg=C["panel"], height=60)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="Water Supply — Live Status",
                 font=("Helvetica", 15, "bold"),
                 bg=C["panel"], fg=C["txt_dark"]).pack(side="left", padx=25, pady=15)
        self.time_lbl = tk.Label(topbar, text="", font=("Helvetica", 10),
                                 bg=C["panel"], fg=C["txt_mid"])
        self.time_lbl.pack(side="right", padx=25)

        # Content row
        content = tk.Frame(main, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # Left: Tank viz + status card
        left = tk.Frame(content, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True)

        self._build_status_card(left)
        self._build_tank_canvas(left)

        # Right: Info cards + resident controls
        right = tk.Frame(content, bg=C["bg"], width=310)
        right.pack(side="right", fill="y", padx=(15, 0))
        right.pack_propagate(False)

        self._build_info_cards(right)
        self._build_resident_controls(right)
        self._build_event_log(main)

    # ── Status Banner ────────────────────────────────────────
    def _build_status_card(self, parent):
        self.status_frame = tk.Frame(parent, bg=C["ok_green"],
                                     height=70, bd=0)
        self.status_frame.pack(fill="x", pady=(0, 10))
        self.status_frame.pack_propagate(False)

        self.status_icon  = tk.Label(self.status_frame, text="✔",
                                     font=("Segoe UI Emoji", 22),
                                     bg=C["ok_green"], fg="white")
        self.status_icon.pack(side="left", padx=20)

        right_lbl = tk.Frame(self.status_frame, bg=C["ok_green"])
        right_lbl.pack(side="left", fill="y", pady=10)

        self.status_title = tk.Label(right_lbl, text="Plenty of Water",
                                     font=("Helvetica", 16, "bold"),
                                     bg=C["ok_green"], fg="white")
        self.status_title.pack(anchor="w")
        self.status_sub   = tk.Label(right_lbl, text="",
                                     font=("Helvetica", 10),
                                     bg=C["ok_green"], fg="#D6EAF8")
        self.status_sub.pack(anchor="w")

    # ── Tank Canvas ──────────────────────────────────────────
    def _build_tank_canvas(self, parent):
        card = tk.Frame(parent, bg=C["panel"], bd=0,
                        highlightbackground="#E5E8E8", highlightthickness=1)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Tank Level", font=("Helvetica", 10, "bold"),
                 bg=C["panel"], fg=C["txt_mid"]).pack(anchor="w", padx=15, pady=(10, 0))

        self.canvas = tk.Canvas(card, bg=C["panel"],
                                highlightthickness=0, height=370)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=5)

    # ── Info Cards ───────────────────────────────────────────
    def _build_info_cards(self, parent):
        tk.Label(parent, text="At a Glance",
                 font=("Helvetica", 11, "bold"),
                 bg=C["bg"], fg=C["txt_dark"]).pack(anchor="w", pady=(0, 8))

        self.card_level    = self._make_card(parent, "Water in Tank",   "──",    "💧")
        self.card_pump     = self._make_card(parent, "Pump",            "──",    "⚙")
        self.card_advice   = self._make_card(parent, "Can I Use Water?","──",    "✔")

    def _make_card(self, parent, title, value, icon):
        card = tk.Frame(parent, bg=C["panel"], bd=0,
                        highlightbackground="#E5E8E8", highlightthickness=1)
        card.pack(fill="x", pady=2)

        left  = tk.Frame(card, bg=C["panel"])
        left.pack(side="left", padx=10, pady=6)

        tk.Label(left, text=icon, font=("Segoe UI Emoji", 15),
                 bg=C["panel"]).pack()

        right = tk.Frame(card, bg=C["panel"])
        right.pack(side="left", fill="both", expand=True, pady=6)

        tk.Label(right, text=title, font=("Helvetica", 8),
                 bg=C["panel"], fg=C["txt_light"]).pack(anchor="w")
        val_lbl = tk.Label(right, text=value, font=("Helvetica", 10, "bold"),
                           bg=C["panel"], fg=C["txt_dark"], wraplength=200, justify="left")
        val_lbl.pack(anchor="w")
        return val_lbl

    # ── Resident Controls (GDD: resident actions only) ────────
    def _build_resident_controls(self, parent):
        sep = tk.Frame(parent, bg=C["bg"], height=12)
        sep.pack()

        tk.Label(parent, text="My Controls",
                 font=("Helvetica", 11, "bold"),
                 bg=C["bg"], fg=C["txt_dark"]).pack(anchor="w", pady=(0, 8))

        # Conservation toggle — framed as resident responsibility
        cons_card = tk.Frame(parent, bg=C["panel"], bd=0,
                             highlightbackground="#E5E8E8", highlightthickness=1)
        cons_card.pack(fill="x", pady=2)

        inner = tk.Frame(cons_card, bg=C["panel"])
        inner.pack(fill="x", padx=12, pady=7)

        tk.Label(inner, text="Conservation Mode",
                 font=("Helvetica", 10, "bold"),
                 bg=C["panel"], fg=C["txt_dark"]).pack(anchor="w")
        tk.Label(inner, text="Pause your flat's usage to help the community",
                 font=("Helvetica", 8), bg=C["panel"], fg=C["txt_mid"],
                 wraplength=240, justify="left").pack(anchor="w", pady=(2, 8))

        self.cons_btn = tk.Button(inner,
                                  text="Enable Conservation Mode",
                                  bg=C["ok_green"], fg="white",
                                  font=("Helvetica", 10, "bold"),
                                  relief="flat", bd=0, pady=8, padx=10,
                                  cursor="hand2",
                                  command=self._toggle_conservation)
        self.cons_btn.pack(fill="x")

        # ── Secretary Motor Control ───────────────────────────
        motor_card = tk.Frame(parent, bg=C["panel"], bd=0,
                              highlightbackground="#E5E8E8", highlightthickness=1)
        motor_card.pack(fill="x", pady=2)

        motor_inner = tk.Frame(motor_card, bg=C["panel"])
        motor_inner.pack(fill="x", padx=12, pady=7)

        tk.Label(motor_inner, text="Secretary: Pump Control",
                 font=("Helvetica", 10, "bold"),
                 bg=C["panel"], fg=C["txt_dark"]).pack(anchor="w")

        self.motor_mode_lbl = tk.Label(motor_inner,
                 text="Mode: Auto  |  Pump: Standby",
                 font=("Helvetica", 8), bg=C["panel"], fg=C["txt_mid"],
                 wraplength=240, justify="left")
        self.motor_mode_lbl.pack(anchor="w", pady=(2, 8))

        self.motor_btn = tk.Button(motor_inner,
                                   text="⚙  Turn Pump ON (Override)",
                                   bg=C["ok_green"], fg="white",
                                   font=("Helvetica", 10, "bold"),
                                   relief="flat", bd=0, pady=18, padx=10,
                                   cursor="hand2",
                                   command=self._toggle_motor)
        self.motor_btn.pack(fill="x")

        # Report Issue button
        report_btn = tk.Button(parent,
                               text="📞  Report a Water Issue",
                               bg=C["panel"], fg=C["info_blue"],
                               font=("Helvetica", 10, "bold"),
                               relief="flat", bd=0, pady=10,
                               highlightbackground="#E5E8E8",
                               highlightthickness=1,
                               cursor="hand2",
                               command=self._report_issue)
        report_btn.pack(fill="x", pady=4)

    # ── Event Log ────────────────────────────────────────────
    def _build_event_log(self, parent):
        log_frame = tk.Frame(parent, bg=C["sidebar"], height=110)
        log_frame.pack(side="bottom", fill="x")
        log_frame.pack_propagate(False)

        tk.Label(log_frame, text="Recent Notifications",
                 bg=C["sidebar"], fg=C["sidebar_txt"],
                 font=("Helvetica", 9, "bold")).pack(anchor="w", padx=15, pady=(8, 2))

        self.log_box = tk.Text(log_frame, bg=C["sidebar"], fg="#7FB3D3",
                               font=("Consolas", 9), state="disabled",
                               bd=0, highlightthickness=0, height=4)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(0, 8))

    # ══════════════════════════════════════════════════════
    #  DRAWING
    # ══════════════════════════════════════════════════════
    def _draw_tank(self):
        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            return

        tank_w = min(160, cw // 2)
        tank_h = int(ch * 0.70)
        tx     = (cw - tank_w) // 2
        ty     = int(ch * 0.10)
        t_bot  = ty + tank_h

        # ── Percentage ring label ───────────────────────────
        pct = (self.tank.water_level / TANK_HEIGHT) * 100
        _, _, wcolor = self.tank.resident_status()

        # ── Support legs ───────────────────────────────────
        for dx in [0, tank_w]:
            self.canvas.create_line(tx + dx, t_bot,
                                    tx + dx + (18 if dx else -18), t_bot + 25,
                                    width=5, fill=C["tank_edge"])
        self.canvas.create_line(tx - 18, t_bot + 25,
                                tx + tank_w + 18, t_bot + 25,
                                width=3, fill=C["tank_edge"])

        # ── Tank shell ─────────────────────────────────────
        self.canvas.create_rectangle(tx, ty, tx + tank_w, t_bot,
                                     fill=C["tank_body"],
                                     outline=C["tank_edge"], width=3)

        # ── Water fill ─────────────────────────────────────
        water_h   = (self.tank.water_level / TANK_HEIGHT) * tank_h
        water_top = t_bot - water_h
        self.canvas.create_rectangle(tx + 2, water_top,
                                     tx + tank_w - 2, t_bot - 2,
                                     fill=wcolor, outline="")

        # ── Animated ripple on water surface ───────────────
        if self.tank.water_level > 0.2:
            t   = time.time()
            amp = 3
            for i in range(5):
                wx  = tx + 5 + i * (tank_w - 10) // 4
                wy  = water_top + amp * math.sin(t * 3 + i)
                self.canvas.create_oval(wx - 8, wy - 3, wx + 8, wy + 3,
                                        outline="white", width=1)

        # ── Level markers with exact heights ──────────────────
        markers = [
            (10.0,         "10 m (Max)",    C["txt_mid"],    True),
            (OVERFLOW_LEVEL,"9.8 m Overflow",C["crit_red"],  True),
            (5.0,          "5 m (Mid)",     C["info_blue"],  True),
            (CRITICAL_LOW, "1 m Underflow", C["crit_red"],   True),
        ]
        for m_lvl, label, mcolor, show_line in markers:
            my = t_bot - (m_lvl / TANK_HEIGHT) * tank_h
            if my < ty:
                my = ty
            self.canvas.create_line(tx - 5, my, tx + tank_w + 5, my,
                                    fill=mcolor, width=1, dash=(5, 3))
            self.canvas.create_text(tx + tank_w + 8, my,
                                    text=label, anchor="w",
                                    fill=mcolor, font=("Helvetica", 8, "bold"))

        # ── Current level indicator ─────────────────────────
        cur_y = t_bot - water_h
        self.canvas.create_line(tx, cur_y, tx + tank_w, cur_y,
                                fill="white", width=2)
        pct_txt = f"{pct:.0f}%"
        mid_x   = tx + tank_w // 2
        mid_y   = max(cur_y + 14, t_bot - 14)
        if water_h > 20:
            self.canvas.create_text(mid_x, mid_y, text=pct_txt,
                                    fill="white", font=("Helvetica", 13, "bold"))

        # ── Pump pipe animation ─────────────────────────────
        if self.tank.motor_status == "ON":
            cx     = tx + tank_w // 2
            pip_top = ty - 45
            self.canvas.create_line(cx, pip_top, cx, ty,
                                    width=7, fill=C["ok_green"])
            offset = int(time.time() * 12) % 20
            for off in [offset, offset + 10]:
                if off < 40:
                    self.canvas.create_oval(cx - 5, pip_top + off,
                                            cx + 5, pip_top + off + 8,
                                            fill="white", outline="")
            self.canvas.create_text(cx, pip_top - 10,
                                    text="⬇ Pump ON", fill=C["ok_green"],
                                    font=("Helvetica", 8, "bold"))

        # ── Outlet pipe ────────────────────────────────────
        out_y = t_bot - 30
        self.canvas.create_line(tx, out_y, tx - 35, out_y,
                                width=7, fill=C["tank_edge"])
        if self.tank.usage_active:
            self.canvas.create_line(tx - 35, out_y,
                                    tx - 45, out_y + 22,
                                    width=5, fill=C["water_ok"])

        # ── Dome top ───────────────────────────────────────
        self.canvas.create_arc(tx, ty - 20, tx + tank_w, ty + 20,
                               start=0, extent=180,
                               fill=C["tank_body"],
                               outline=C["tank_edge"], width=2)

    # ══════════════════════════════════════════════════════
    #  ACTIONS
    # ══════════════════════════════════════════════════════
    def _toggle_conservation(self):
        if self.tank.usage_active:
            self.tank.usage_active = False
            self.cons_btn.config(text="Disable Conservation Mode",
                                 bg=C["warn_orange"])
            self._log_event("You enabled Conservation Mode. Water usage paused.")
        else:
            self.tank.usage_active = True
            self.cons_btn.config(text="Enable Conservation Mode",
                                 bg=C["ok_green"])
            self._log_event("Conservation Mode disabled. Water usage resumed.")

    def _report_issue(self):
        persona = self.persona_var.get()
        messagebox.showinfo(
            "Issue Reported",
            f"Thank you, {persona.split('(')[0].strip()}!\n\n"
            "Your issue has been sent to the Society Secretary.\n"
            "You will receive a response within 2 hours.\n\n"
            "Reference ID: WR-2024-" + str(int(time.time()) % 9999)
        )
        self._log_event("Water issue reported to Secretary.")

    def _toggle_motor(self):
        if self.tank.water_level >= OVERFLOW_LEVEL:
            messagebox.showwarning("Cannot Start Pump",
                "Tank is already full (9.8 m).\nPump cannot be started.")
            return
        self.tank.manual_override = True
        if self.tank.motor_status == "ON":
            self.tank.motor_status = "OFF"
            self._log_event("Secretary: Pump manually turned OFF (override).")
        else:
            self.tank.motor_status = "ON"
            self._log_event("Secretary: Pump manually turned ON (override).")

    def _log_event(self, msg):
        t = time.strftime("%I:%M %p")
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, f"[{t}]  {msg}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    # ══════════════════════════════════════════════════════
    #  UPDATE LOOP
    # ══════════════════════════════════════════════════════
    def _loop(self):
        self.tank.update()

        key, label, color = self.tank.resident_status()

        # ── Auto-log all system state changes ─────────────────
        cur_motor = self.tank.motor_status
        cur_usage = self.tank.usage_active

        if cur_motor != self._prev_motor:
            if cur_motor == "ON":
                self._log_event("🟢 AUTO: Pump started automatically (low water level).")
            else:
                self._log_event("🔴 AUTO: Pump stopped automatically (tank full / overflow).")
            self._prev_motor = cur_motor

        if cur_usage != self._prev_usage:
            self._prev_usage = cur_usage  # manual toggle already logs, just sync

        if key == "full" and not self._overflow_logged:
            self._overflow_logged = True
            self._log_event("💧 SYSTEM: Tank reached full capacity (9.8 m). Pump stopped.")
        elif key != "full":
            self._overflow_logged = False

        # ── Status banner ──────────────────────────────────
        icon_map = {
            "full":     ("💧", "white"),
            "good":     ("✔",  "white"),
            "moderate": ("⚠",  "white"),
            "low":      ("⚠",  "white"),
            "critical": ("🚨", "white"),
        }
        icon, _ = icon_map.get(key, ("✔", "white"))
        self.status_frame.config(bg=color)
        self.status_icon.config(text=icon, bg=color)
        self.status_title.config(text=label, bg=color)
        self.status_sub.config(
            text=f"Current level: {self.tank.water_level:.2f} m  |  Tank capacity: 10 m",
            bg=color, fg="#D6EAF8" if key in ("full","good") else "#FFF")

        # ── At a Glance cards ──────────────────────────────
        pct = (self.tank.water_level / TANK_HEIGHT) * 100
        bars = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        self.card_level.config(
            text=f"{bars}  {pct:.0f}%  ({self.tank.water_level:.1f} m)",
            fg=color)

        pump_txt = "Running — refilling tank" if self.tank.motor_status == "ON" else "Standby"
        self.card_pump.config(
            text=pump_txt,
            fg=C["ok_green"] if self.tank.motor_status == "ON" else C["txt_light"])

        # ── Secretary motor button state ───────────────────
        is_on      = self.tank.motor_status == "ON"
        is_override = self.tank.manual_override
        mode_str   = "Mode: Manual Override" if is_override else "Mode: Auto"
        pump_state = "Running" if is_on else "Standby"
        self.motor_mode_lbl.config(text=f"{mode_str}  |  Pump: {pump_state}",
                                   fg=C["crit_red"] if is_override else C["txt_mid"])
        if is_on:
            self.motor_btn.config(text="⚙  Turn Pump OFF (Override)",
                                  bg=C["crit_red"])
        else:
            self.motor_btn.config(text="⚙  Turn Pump ON (Override)",
                                  bg=C["ok_green"])

        self.card_advice.config(text=self.tank.usage_advice(),
                                fg=C["ok_green"] if key in ("full","good") else C["crit_red"])

        # ── Clock ──────────────────────────────────────────
        self.time_lbl.config(text=time.strftime("Last updated: %I:%M:%S %p"))

        # ── Auto-notify on critical (GDD: proactive alert) ─
        if key == "critical" and not self.alert_shown:
            self.alert_shown = True
            self._log_event("⚠ ALERT: Tank critically low. Pump auto-started.")
            messagebox.showwarning(
                "Water Alert",
                "⚠  The community water tank is almost empty!\n\n"
                "The pump has been automatically started.\n"
                "Please avoid non-essential water use until\n"
                "the level recovers to a safe level.")
        elif key != "critical":
            self.alert_shown = False

        # ── Draw ───────────────────────────────────────────
        self._draw_tank()
        self.root.after(100, self._loop)


# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = GDDResidentApp(root)
    root.mainloop()