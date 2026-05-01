import tkinter as tk
from tkinter import ttk

from db.db_connection import fetch_overview_metrics
from ui.components import NavigationSidebar


DASH = {
    "bg": "#f3f8fd",
    "hero_start": "#0c5e93",
    "hero_end": "#19a7a1",
    "panel": "#ffffff",
    "panel_alt": "#edf7ff",
    "border": "#d5e5f3",
    "title": "#12304a",
    "text": "#52657c",
    "blue": "#1c8ef5",
    "teal": "#16b8a6",
    "orange": "#ff9a3d",
    "pink": "#ff5e8a",
    "purple": "#7a67f8",
    "yellow": "#f0c94d",
}


class HomePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="App.TFrame", padding=24)
        self.app = app
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar_host = ttk.Frame(self, style="App.TFrame")
        self.sidebar_host.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        self.content = tk.Frame(self, bg=DASH["bg"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)

    def refresh(self):
        for widget in self.sidebar_host.winfo_children():
            widget.destroy()
        NavigationSidebar(self.sidebar_host, self.app, "HomePage").pack(fill="y", expand=True)

        for widget in self.content.winfo_children():
            widget.destroy()

        user = self.app.current_user["username"] if self.app.current_user else "User"

        try:
            metrics = fetch_overview_metrics()
            self._build_dashboard(user, metrics)
        except Exception as error:
            error_card = tk.Frame(self.content, bg=DASH["panel"], highlightbackground=DASH["border"], highlightthickness=1)
            error_card.grid(row=0, column=0, sticky="ew")
            tk.Label(
                error_card,
                text="Dashboard Unavailable",
                bg=DASH["panel"],
                fg=DASH["title"],
                font=("Segoe UI Semibold", 20),
            ).pack(anchor="w", padx=24, pady=(20, 8))
            tk.Label(
                error_card,
                text=str(error),
                bg=DASH["panel"],
                fg=DASH["text"],
                font=("Segoe UI", 11),
                wraplength=900,
                justify="left",
            ).pack(anchor="w", padx=24, pady=(0, 20))

    def _build_dashboard(self, user, metrics):
        hero = tk.Canvas(self.content, height=220, bg=DASH["hero_start"], highlightthickness=0)
        hero.grid(row=0, column=0, sticky="ew")
        hero.bind("<Configure>", lambda event: self._draw_hero(hero, event.width, event.height, user, metrics))

        layout = tk.Frame(self.content, bg=DASH["bg"])
        layout.grid(row=1, column=0, sticky="nsew", pady=(18, 0))
        layout.grid_columnconfigure(0, weight=5)
        layout.grid_columnconfigure(1, weight=3)

        left = tk.Frame(layout, bg=DASH["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = tk.Frame(layout, bg=DASH["bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        for col in range(2):
            left.grid_columnconfigure(col, weight=1)
            right.grid_columnconfigure(col, weight=1)

        cards = [
            ("Total Records", str(metrics["total_records"]), "All healthcare entries currently stored.", DASH["blue"]),
            ("Patients", str(metrics["total_patients"]), "Distinct patient records available.", DASH["teal"]),
            ("Hospitals", str(metrics["total_hospitals"]), "Active healthcare facilities tracked.", DASH["orange"]),
            ("Doctors", str(metrics["total_doctors"]), "Doctors connected to current entries.", DASH["pink"]),
            ("Diseases", str(metrics["total_diseases"]), "Unique diseases reflected live.", DASH["purple"]),
            ("Specialists", str(metrics["total_specialists"]), "Specialist categories in the system.", DASH["yellow"]),
        ]
        for index, (title, value, body, accent) in enumerate(cards):
            card = self._make_stat_card(left, title, value, body, accent)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=8, pady=8)

        bill_card = self._make_bill_card(right, metrics)
        bill_card.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        actions = self._make_action_card(right)
        actions.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        insights = [
            ("Average Bill", f"Rs {metrics['average_bill']:,.0f}", DASH["blue"]),
            ("Patient Reach", str(metrics["total_patients"]), DASH["teal"]),
            ("Disease Watch", str(metrics["total_diseases"]), DASH["pink"]),
            ("Network Scale", str(metrics["total_hospitals"] + metrics["total_doctors"]), DASH["purple"]),
        ]
        for index, (label, value, accent) in enumerate(insights):
            tile = self._make_small_tile(right, label, value, accent)
            tile.grid(row=2 + index // 2, column=index % 2, sticky="nsew", padx=8, pady=8)

    def _draw_hero(self, canvas, width, height, user, metrics):
        canvas.delete("all")
        width = max(width, 920)
        canvas.create_rectangle(0, 0, width, height, fill=DASH["hero_start"], outline="")
        canvas.create_polygon(0, 0, width * 0.62, 0, width * 0.42, height, 0, height, fill=DASH["hero_end"], outline="")
        canvas.create_oval(width - 260, -80, width + 40, 180, fill="#0f7691", outline="")
        canvas.create_oval(width - 360, 70, width - 70, 300, fill="#0d5a8d", outline="")
        canvas.create_rectangle(width - 230, 78, width - 70, 175, fill="#d8eef9", outline="")
        canvas.create_rectangle(width - 205, 48, width - 95, 78, fill="#edf8ff", outline="")
        canvas.create_rectangle(width - 150, 96, width - 130, 160, fill="#22c0b7", outline="")
        canvas.create_rectangle(width - 180, 120, width - 100, 138, fill="#22c0b7", outline="")

        canvas.create_text(34, 42, text=f"Welcome back, {user}", anchor="w", fill="#e7fbff", font=("Segoe UI", 15))
        canvas.create_text(34, 82, text="Healthcare Operations Dashboard", anchor="w", fill="white", font=("Segoe UI Semibold", 28))
        canvas.create_text(
            34,
            122,
            text="Monitor records, hospitals, doctors, diseases, specialists, and billing with a cleaner operational view.",
            anchor="w",
            fill="#d9f6ff",
            width=500,
            font=("Segoe UI", 11),
        )
        canvas.create_text(width - 250, 34, text="Live SQL Server Status", anchor="w", fill="#d8f3ff", font=("Segoe UI Semibold", 11))
        canvas.create_text(width - 250, 58, text=f"{metrics['total_records']} records synchronized", anchor="w", fill="white", font=("Segoe UI", 18))
        canvas.create_text(width - 250, 84, text=f"Rs {metrics['total_bill']:,.0f} total billing tracked", anchor="w", fill="#d8f3ff", font=("Segoe UI", 11))

    def _make_stat_card(self, parent, title, value, body, accent):
        card = tk.Frame(parent, bg=DASH["panel"], highlightbackground=DASH["border"], highlightthickness=1)
        tk.Frame(card, bg=accent, height=6).pack(fill="x")
        inner = tk.Frame(card, bg=DASH["panel"])
        inner.pack(fill="both", expand=True, padx=18, pady=16)
        dot = tk.Canvas(inner, width=16, height=16, bg=DASH["panel"], highlightthickness=0)
        dot.pack(anchor="w")
        dot.create_oval(2, 2, 14, 14, fill=accent, outline="")
        tk.Label(inner, text=title, bg=DASH["panel"], fg=DASH["title"], font=("Segoe UI Semibold", 13)).pack(anchor="w", pady=(8, 2))
        tk.Label(inner, text=value, bg=DASH["panel"], fg=accent, font=("Segoe UI Semibold", 26)).pack(anchor="w")
        tk.Label(inner, text=body, bg=DASH["panel"], fg=DASH["text"], font=("Segoe UI", 10), wraplength=280, justify="left").pack(anchor="w", pady=(6, 0))
        return card

    def _make_bill_card(self, parent, metrics):
        card = tk.Canvas(parent, height=180, bg=DASH["panel"], highlightthickness=1, highlightbackground=DASH["border"])
        card.bind("<Configure>", lambda event: self._draw_bill_card(card, event.width, event.height, metrics))
        return card

    def _draw_bill_card(self, canvas, width, height, metrics):
        canvas.delete("all")
        width = max(width, 320)
        canvas.create_rectangle(0, 0, width, height, fill=DASH["panel"], outline="")
        canvas.create_oval(width - 170, -40, width + 20, 120, fill="#e6f4ff", outline="")
        canvas.create_oval(width - 220, 70, width - 20, 210, fill="#eefaf7", outline="")
        canvas.create_text(22, 26, text="Financial Snapshot", anchor="w", fill=DASH["title"], font=("Segoe UI Semibold", 15))
        canvas.create_text(22, 58, text=f"Rs {metrics['total_bill']:,.0f}", anchor="w", fill=DASH["blue"], font=("Segoe UI Semibold", 30))
        canvas.create_text(22, 85, text="Combined billing across all healthcare records", anchor="w", fill=DASH["text"], font=("Segoe UI", 10))
        canvas.create_text(22, 118, text=f"Average bill: Rs {metrics['average_bill']:,.0f}", anchor="w", fill=DASH["teal"], font=("Segoe UI Semibold", 11))
        canvas.create_text(22, 142, text=f"Specialists tracked: {metrics['total_specialists']}", anchor="w", fill=DASH["orange"], font=("Segoe UI Semibold", 11))

    def _make_action_card(self, parent):
        card = tk.Frame(parent, bg=DASH["panel_alt"], highlightbackground=DASH["border"], highlightthickness=1)
        tk.Label(card, text="Quick Actions", bg=DASH["panel_alt"], fg=DASH["title"], font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=18, pady=(16, 8))
        tk.Label(
            card,
            text="Refresh the dashboard, jump to data entry, or open live analysis without disturbing the current SQL Server workflow.",
            bg=DASH["panel_alt"],
            fg=DASH["text"],
            font=("Segoe UI", 10),
            wraplength=360,
            justify="left",
        ).pack(anchor="w", padx=18)
        buttons = tk.Frame(card, bg=DASH["panel_alt"])
        buttons.pack(fill="x", padx=18, pady=16)
        ttk.Button(buttons, text="Refresh Dashboard", style="Primary.TButton", command=self.refresh).pack(side="left", padx=(0, 10))
        ttk.Button(buttons, text="Open Analysis", style="Secondary.TButton", command=lambda: self.app.open_page("AnalysisPage")).pack(side="left", padx=(0, 10))
        ttk.Button(buttons, text="Add Record", style="Secondary.TButton", command=lambda: self.app.open_page("FormPage")).pack(side="left")
        return card

    def _make_small_tile(self, parent, label, value, accent):
        tile = tk.Frame(parent, bg=DASH["panel"], highlightbackground=DASH["border"], highlightthickness=1)
        tk.Frame(tile, bg=accent, height=4).pack(fill="x")
        body = tk.Frame(tile, bg=DASH["panel"])
        body.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(body, text=label, bg=DASH["panel"], fg=DASH["text"], font=("Segoe UI Semibold", 10)).pack(anchor="w")
        tk.Label(body, text=value, bg=DASH["panel"], fg=accent, font=("Segoe UI Semibold", 22)).pack(anchor="w", pady=(6, 0))
        return tile
