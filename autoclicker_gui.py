import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from pynput import keyboard
import subprocess
import sys

# ---------- SETĂRI ----------
HOTKEY = "z"  # tasta globală pentru toggle
DEFAULT_CPS = 10  # click-uri pe secundă inițial
MIN_CPS = 1
MAX_CPS = 500  # Limita maximă crescută la 500 click-uri/secundă
# ---------------------------


class ModernButton(tk.Canvas):
    """Buton personalizat modern cu hover effect"""
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, height=45, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.is_active = False
        
        # Culori
        self.bg_normal = "#2563eb"  # Albastru
        self.bg_hover = "#1d4ed8"   # Albastru mai închis
        self.bg_active = "#dc2626"  # Roșu când este activ
        self.bg_active_hover = "#b91c1c"
        self.text_color = "#ffffff"
        
        self.rect = self.create_rectangle(0, 0, 400, 45, fill=self.bg_normal, outline="", tags="button")
        self.text_item = self.create_text(200, 22, text=text, fill=self.text_color, 
                                         font=("Segoe UI", 11, "bold"), tags="button")
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
    def _on_enter(self, e):
        color = self.bg_active_hover if self.is_active else self.bg_hover
        self.itemconfig(self.rect, fill=color)
        
    def _on_leave(self, e):
        color = self.bg_active if self.is_active else self.bg_normal
        self.itemconfig(self.rect, fill=color)
        
    def _on_click(self, e):
        if self.command:
            self.command()
    
    def set_active(self, active):
        self.is_active = active
        color = self.bg_active if active else self.bg_normal
        self.itemconfig(self.rect, fill=color)
        self.itemconfig(self.text_item, text="⏸ OPREȘTE (Z)" if active else "▶ PORNEȘTE (Z)")


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Pro")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e293b")
        
        # Încearcă să centreze fereastra
        self.root.update_idletasks()
        width = 480
        height = 620
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.clicking_event = threading.Event()
        self.stop_app = False
        self.click_count = 0
        self.start_time = 0

        # ---- UI Modernă ----
        main = tk.Frame(root, bg="#1e293b", padx=25, pady=20)
        main.pack(fill="both", expand=True)

        # Header
        header = tk.Label(main, text="⚡ AutoClicker Pro", font=("Segoe UI", 20, "bold"),
                         bg="#1e293b", fg="#60a5fa")
        header.pack(pady=(0, 5))
        
        # Status indicator
        status_frame = tk.Frame(main, bg="#0f172a", highlightbackground="#334155", 
                               highlightthickness=1)
        status_frame.pack(fill="x", pady=(0, 20))
        
        self.status_dot = tk.Label(status_frame, text="⬤", font=("Segoe UI", 16),
                                   bg="#0f172a", fg="#64748b")
        self.status_dot.pack(side="left", padx=15, pady=8)
        
        self.status_var = tk.StringVar(value="Inactiv")
        self.status_lbl = tk.Label(status_frame, textvariable=self.status_var,
                                   font=("Segoe UI", 13, "bold"), bg="#0f172a", fg="#cbd5e1")
        self.status_lbl.pack(side="left", pady=8)

        # Stats panel
        stats_frame = tk.Frame(main, bg="#1e293b")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Click counter
        click_panel = tk.Frame(stats_frame, bg="#0f172a", highlightbackground="#334155",
                              highlightthickness=1)
        click_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(click_panel, text="Click-uri totale", font=("Segoe UI", 9),
                bg="#0f172a", fg="#94a3b8").pack(pady=(10, 2))
        self.click_count_var = tk.StringVar(value="0")
        tk.Label(click_panel, textvariable=self.click_count_var, 
                font=("Segoe UI", 18, "bold"), bg="#0f172a", fg="#60a5fa").pack(pady=(0, 10))
        
        # Time counter
        time_panel = tk.Frame(stats_frame, bg="#0f172a", highlightbackground="#334155",
                             highlightthickness=1)
        time_panel.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        tk.Label(time_panel, text="Timp activ", font=("Segoe UI", 9),
                bg="#0f172a", fg="#94a3b8").pack(pady=(10, 2))
        self.time_var = tk.StringVar(value="0s")
        tk.Label(time_panel, textvariable=self.time_var,
                font=("Segoe UI", 18, "bold"), bg="#0f172a", fg="#60a5fa").pack(pady=(0, 10))

        # Speed control
        speed_frame = tk.Frame(main, bg="#0f172a", highlightbackground="#334155",
                              highlightthickness=1)
        speed_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(speed_frame, text="Viteză Click-uri", font=("Segoe UI", 11, "bold"),
                bg="#0f172a", fg="#cbd5e1").pack(pady=(15, 5))
        
        speed_control = tk.Frame(speed_frame, bg="#0f172a")
        speed_control.pack(fill="x", padx=20, pady=(0, 10))
        
        self.cps_var = tk.IntVar(value=DEFAULT_CPS)
        self.cps_value_lbl = tk.Label(speed_control, text=f"{DEFAULT_CPS}", 
                                     font=("Segoe UI", 24, "bold"),
                                     bg="#0f172a", fg="#60a5fa")
        self.cps_value_lbl.pack()
        
        tk.Label(speed_control, text="click-uri / secundă", font=("Segoe UI", 9),
                bg="#0f172a", fg="#94a3b8").pack()
        
        # Slider cu butoane +/-
        slider_controls = tk.Frame(speed_frame, bg="#0f172a")
        slider_controls.pack(fill="x", padx=20, pady=(5, 15))
        
        # Buton minus
        minus_btn = tk.Button(slider_controls, text="−", command=self._decrease_cps,
                             bg="#475569", fg="#ffffff", font=("Segoe UI", 18, "bold"),
                             relief="flat", width=3, cursor="hand2", bd=0,
                             activebackground="#64748b", highlightthickness=0)
        minus_btn.pack(side="left", padx=(0, 8))
        
        self.cps_scale = tk.Scale(slider_controls, from_=MIN_CPS, to=MAX_CPS,
                                 orient="horizontal", command=self._on_scale,
                                 bg="#334155", fg="#60a5fa", troughcolor="#1e293b",
                                 highlightthickness=0, sliderlength=50, width=25,
                                 activebackground="#3b82f6", showvalue=False, bd=0)
        self.cps_scale.set(DEFAULT_CPS)
        self.cps_scale.pack(side="left", fill="x", expand=True, padx=3)
        
        # Buton plus
        plus_btn = tk.Button(slider_controls, text="+", command=self._increase_cps,
                            bg="#475569", fg="#ffffff", font=("Segoe UI", 18, "bold"),
                            relief="flat", width=3, cursor="hand2", bd=0,
                            activebackground="#64748b", highlightthickness=0)
        plus_btn.pack(side="left", padx=(8, 0))

        # Buton modern toggle
        self.toggle_btn = ModernButton(main, "▶ PORNEȘTE (Z)", self.toggle_clicking, width=400)
        self.toggle_btn.pack(pady=(0, 15))
        
        # Reset button
        reset_btn = tk.Button(main, text="🔄 Reset Statistici", command=self.reset_stats,
                             bg="#334155", fg="#cbd5e1", font=("Segoe UI", 9),
                             relief="flat", padx=15, pady=8, cursor="hand2",
                             activebackground="#475569")
        reset_btn.pack()

        # Footer
        tk.Label(main, text="Apasă Z pentru a porni/opri", 
                font=("Segoe UI", 9), bg="#1e293b", fg="#64748b").pack(pady=(15, 0))

        # ---- Thread de click ----
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()
        
        # Thread pentru timer
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()

        # ---- Global hotkey ----
        if HOTKEY:
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
        else:
            self.listener = None

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # Convertim cps -> delay
    def _delay(self):
        cps = max(MIN_CPS, min(MAX_CPS, int(round(self.cps_scale.get()))))
        return 1.0 / cps

    def _on_scale(self, _):
        self.cps_value_lbl.config(text=f"{int(round(self.cps_scale.get()))}")
    
    def _increase_cps(self):
        current = self.cps_scale.get()
        new_value = min(MAX_CPS, current + 10)
        self.cps_scale.set(new_value)
        self._on_scale(None)
    
    def _decrease_cps(self):
        current = self.cps_scale.get()
        new_value = max(MIN_CPS, current - 10)
        self.cps_scale.set(new_value)
        self._on_scale(None)
    
    def reset_stats(self):
        self.click_count = 0
        self.click_count_var.set("0")
        self.time_var.set("0s")

    def toggle_clicking(self):
        if self.clicking_event.is_set():
            self.clicking_event.clear()
            self.status_var.set("Inactiv")
            self.status_dot.config(fg="#64748b")
            self.toggle_btn.set_active(False)
            print("🔴 AutoClicker OPRIT")
        else:
            self.clicking_event.set()
            self.start_time = time.time()
            self.status_var.set("Activ - Click-uri automate")
            self.status_dot.config(fg="#22c55e")
            self.toggle_btn.set_active(True)
            print("🟢 AutoClicker PORNIT")
    
    def _timer_loop(self):
        """Thread pentru actualizarea timer-ului"""
        while not self.stop_app:
            if self.clicking_event.is_set():
                elapsed = int(time.time() - self.start_time)
                if elapsed < 60:
                    time_str = f"{elapsed}s"
                elif elapsed < 3600:
                    time_str = f"{elapsed//60}m {elapsed%60}s"
                else:
                    time_str = f"{elapsed//3600}h {(elapsed%3600)//60}m"
                self.root.after(0, lambda: self.time_var.set(time_str))
            time.sleep(1)

    def _click_loop(self):
        print("✅ Click thread pornit")
        update_counter = 0
        while not self.stop_app:
            if self.clicking_event.is_set():
                try:
                    pyautogui.click()
                    self.click_count += 1

                    update_counter += 1
                    if update_counter >= 10:
                        self.root.after(
                            0,
                            lambda c=self.click_count: self.click_count_var.set(f"{c:,}")
                        )
                        update_counter = 0
                except Exception as e:
                    print(f"❌ Eroare la click: {e}")
                    self.status_var.set(f"Eroare: {e}")
                    self.status_dot.config(fg="#ef4444")
                    self.clicking_event.clear()
                    self.toggle_btn.set_active(False)
                time.sleep(self._delay())
            else:
                time.sleep(0.05)
        print("⛔ Click thread oprit")

    def _on_key_press(self, key):
        try:
            if isinstance(key, keyboard.KeyCode) and key.char == HOTKEY:
                print(f"⌨️ Tastă apăsată: {HOTKEY}")
                # Toggle pe threadul UI
                self.root.after(0, self.toggle_clicking)
        except Exception as e:
            print(f"⚠️ Eroare la procesarea tastei: {e}")

    def _on_close(self):
        self.stop_app = True
        self.clicking_event.clear()
        try:
            self.listener.stop()
        except Exception:
            pass
        self.root.destroy()


def main():
    # Previne fail-uri pe ecrane mici și elimină delay-urile
    try:
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0  # Elimină delay-ul implicit de 0.1s între acțiuni
    except Exception:
        pass

    # Creăm fereastra principală
    root = tk.Tk()

    try:
        print("✅ Creez aplicația...")
        app = AutoClickerApp(root)
        print("✅ App creat, pornesc mainloop...")
        root.mainloop()
        print("✅ Mainloop terminat")
    except Exception as e:
        print(f"❌ Eroare la pornirea app: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
