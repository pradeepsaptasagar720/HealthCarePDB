import tkinter as tk
from tkinter import StringVar, ttk

from db.db_connection import fetch_detailed_records
from ui.components import NavigationSidebar, ScrollableFrame


PAGE = {
    "bg": "#08121f",
    "panel": "#102033",
    "border": "#295071",
    "title": "#f1f7ff",
    "text": "#cfe3f8",
    "muted": "#8db0cf",
    "accent": "#8c6ff7",
}


class ViewDataInfoPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="App.TFrame", padding=24)
        self.app = app
        self.search_var = StringVar()
        self.filter_var = StringVar(value="All")
        self.records = []
        self.filtered_records = []
        self.tree = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar_host = ttk.Frame(self, style="App.TFrame")
        self.sidebar_host.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        self.scroll = ScrollableFrame(self, bg_color=PAGE["bg"])
        self.scroll.grid(row=0, column=1, sticky="nsew")

    def refresh(self):
        for widget in self.sidebar_host.winfo_children():
            widget.destroy()
        NavigationSidebar(self.sidebar_host, self.app, "ViewDataInfoPage").pack(fill="y", expand=True)

        body = self.scroll.content
        for widget in body.winfo_children():
            widget.destroy()
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        board = tk.Frame(body, bg=PAGE["bg"])
        board.grid(row=0, column=0, sticky="nsew")
        board.columnconfigure(0, weight=1)
        board.rowconfigure(1, weight=1)

        try:
            self.records = fetch_detailed_records()
        except Exception as error:
            tk.Label(
                board,
                text=f"Database Error: {error}",
                bg=PAGE["bg"],
                fg="#ffb4b4",
                font=("Segoe UI Semibold", 14),
                justify="left",
                wraplength=1000,
            ).grid(row=0, column=0, sticky="w")
            return

        self.filtered_records = list(self.records)

        self._build_header(board)
        self._build_table_card(board)

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=PAGE["bg"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        badge = tk.Canvas(header, width=58, height=58, bg=PAGE["bg"], highlightthickness=0)
        badge.grid(row=0, column=0, padx=(6, 14), sticky="w")
        badge.create_oval(2, 2, 56, 56, fill="#1c2d48", outline=PAGE["border"])
        badge.create_rectangle(16, 18, 42, 22, fill=PAGE["accent"], outline="")
        badge.create_rectangle(16, 28, 42, 32, fill=PAGE["accent"], outline="")
        badge.create_rectangle(16, 38, 42, 42, fill=PAGE["accent"], outline="")

        text_wrap = tk.Frame(header, bg=PAGE["bg"])
        text_wrap.grid(row=0, column=1, sticky="w")
        tk.Label(
            text_wrap,
            text="VIEW DATA INFO",
            bg=PAGE["bg"],
            fg=PAGE["title"],
            font=("Segoe UI Semibold", 26),
        ).pack(anchor="w")
        tk.Label(
            text_wrap,
            text="Dedicated full-table page for hospital, doctor, patient, disease, room, condition, and billing records.",
            bg=PAGE["bg"],
            fg=PAGE["muted"],
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(4, 0))

    def _build_table_card(self, parent):
        card = tk.Frame(parent, bg=PAGE["panel"], highlightbackground=PAGE["border"], highlightthickness=1)
        card.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(2, weight=1)
        title = tk.Frame(card, bg=PAGE["panel"])
        title.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))
        tk.Label(
            title,
            text="Detailed Healthcare Records",
            bg=PAGE["panel"],
            fg=PAGE["accent"],
            font=("Segoe UI Semibold", 14),
        ).pack(anchor="w")

        controls = tk.Frame(card, bg=PAGE["panel"])
        controls.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        controls.columnconfigure(3, weight=1)

        disease_values = ["All"] + sorted({str(row["disease"]) for row in self.records if str(row["disease"]).strip()})
        tk.Label(controls, text="Disease", bg=PAGE["panel"], fg=PAGE["muted"], font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Combobox(controls, textvariable=self.filter_var, values=disease_values, state="readonly", width=18).grid(row=0, column=1, sticky="ew", padx=(0, 12))
        tk.Label(controls, text="Search", bg=PAGE["panel"], fg=PAGE["muted"], font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", padx=(0, 6))
        ttk.Entry(controls, textvariable=self.search_var, width=28).grid(row=0, column=3, sticky="ew", padx=(0, 12))
        ttk.Button(controls, text="Apply", style="Primary.TButton", command=self.apply_filters).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(controls, text="Reset", style="Secondary.TButton", command=self.reset_filters).grid(row=0, column=5, padx=(0, 8))
        ttk.Button(controls, text="Refresh", style="Secondary.TButton", command=self.refresh).grid(row=0, column=6)

        table_wrap = tk.Frame(card, bg=PAGE["panel"])
        table_wrap.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 14))
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("ViewData.Treeview", background="#0c1828", fieldbackground="#0c1828", foreground=PAGE["text"], rowheight=30, borderwidth=0)
        style.map("ViewData.Treeview", background=[("selected", "#214f79")])
        style.configure("ViewData.Treeview.Heading", background="#183657", foreground="#d8ecff", font=("Segoe UI Semibold", 9))

        columns = (
            "hospital_id",
            "hospital_name",
            "hospital_city",
            "doctor",
            "doctor_id",
            "specialist",
            "patient_id",
            "patient_name",
            "disease",
            "floor",
            "medical_condition",
            "admitted_date",
            "room_number",
            "discharge_date",
            "bill_amount",
        )
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", style="ViewData.Treeview")
        widths = {
            "hospital_id": 90,
            "hospital_name": 160,
            "hospital_city": 120,
            "doctor": 150,
            "doctor_id": 90,
            "specialist": 120,
            "patient_id": 90,
            "patient_name": 150,
            "disease": 130,
            "floor": 80,
            "medical_condition": 140,
            "admitted_date": 110,
            "room_number": 90,
            "discharge_date": 110,
            "bill_amount": 110,
        }
        for key in columns:
            self.tree.heading(key, text=key.replace("_", " ").title())
            self.tree.column(key, width=widths[key], anchor="center", stretch=False)

        y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self._populate_tree(self.filtered_records)

    def _populate_tree(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["hospital_id"],
                    row["hospital_name"],
                    row["hospital_city"],
                    row["doctor"],
                    row["doctor_id"],
                    row["specialist"],
                    row["patient_id"],
                    row["patient_name"],
                    row["disease"],
                    row["floor"],
                    row["medical_condition"],
                    row["admitted_date"],
                    row["room_number"],
                    row["discharge_date"],
                    f"Rs {row['bill_amount']:,.0f}",
                ),
            )

    def apply_filters(self):
        disease_filter = self.filter_var.get().strip().lower()
        search = self.search_var.get().strip().lower()
        results = list(self.records)

        if disease_filter and disease_filter != "all":
            results = [row for row in results if str(row["disease"]).strip().lower() == disease_filter]

        if search:
            results = [
                row
                for row in results
                if search in " ".join(
                    [
                        str(row["hospital_id"]),
                        str(row["hospital_name"]),
                        str(row["hospital_city"]),
                        str(row["doctor"]),
                        str(row["doctor_id"]),
                        str(row["specialist"]),
                        str(row["patient_id"]),
                        str(row["patient_name"]),
                        str(row["disease"]),
                        str(row["floor"]),
                        str(row["medical_condition"]),
                        str(row["admitted_date"]),
                        str(row["room_number"]),
                        str(row["discharge_date"]),
                        str(row["bill_amount"]),
                    ]
                ).lower()
            ]

        self.filtered_records = results
        self._populate_tree(results)

    def reset_filters(self):
        self.filter_var.set("All")
        self.search_var.set("")
        self.filtered_records = list(self.records)
        self._populate_tree(self.filtered_records)
