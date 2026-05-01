from collections import defaultdict
from datetime import datetime
import tkinter as tk
from tkinter import ttk

from db.db_connection import fetch_bill_by_group, fetch_detailed_records, fetch_group_counts, fetch_overview_metrics
from ui.components import NavigationSidebar, ScrollableFrame


THEME = {
    "bg": "#08121f",
    "panel": "#102033",
    "panel_hover": "#17314d",
    "panel_alt": "#132842",
    "border": "#295071",
    "title": "#f1f7ff",
    "text": "#cfe3f8",
    "muted": "#8db0cf",
    "blue": "#39a7ff",
    "cyan": "#4cc9f0",
    "teal": "#1dd3b0",
    "orange": "#ff9640",
    "pink": "#ff5f87",
    "purple": "#8c6ff7",
    "yellow": "#f3d45a",
}

CHART_COLORS = [
    THEME["blue"],
    THEME["teal"],
    THEME["orange"],
    THEME["pink"],
    THEME["purple"],
    THEME["yellow"],
    THEME["cyan"],
    "#7cc36f",
]


class HoverTip:
    def __init__(self, widget, text, bg=THEME["panel_hover"]):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.tip = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")

    def show(self, _event=None):
        if self.tip or not self.text:
            return
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + 18
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            bg=self.bg,
            fg=THEME["title"],
            font=("Segoe UI", 9),
            justify="left",
            wraplength=240,
            relief="solid",
            bd=1,
            padx=10,
            pady=6,
        )
        label.pack()

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class HoverPanel(tk.Frame):
    def __init__(self, parent, title, accent, tooltip_text, **kwargs):
        super().__init__(parent, bg=THEME["panel"], highlightbackground=THEME["border"], highlightthickness=1, **kwargs)
        self.default_bg = THEME["panel"]
        self.accent = accent
        self._header = tk.Frame(self, bg=self.default_bg)
        self._header.pack(fill="x", padx=16, pady=(12, 6))
        dot = tk.Canvas(self._header, width=14, height=14, bg=self.default_bg, highlightthickness=0)
        dot.pack(side="left")
        dot.create_oval(2, 2, 12, 12, fill=accent, outline="")
        self.title_label = tk.Label(
            self._header,
            text=title,
            bg=self.default_bg,
            fg=accent,
            font=("Segoe UI Semibold", 12),
        )
        self.title_label.pack(side="left", padx=(8, 0))
        self.info_icon = tk.Canvas(self._header, width=18, height=18, bg=self.default_bg, highlightthickness=0, cursor="hand2")
        self.info_icon.pack(side="right")
        self.info_icon.create_oval(2, 2, 16, 16, fill="#1a3956", outline=accent)
        self.info_icon.create_text(9, 9, text="i", fill=THEME["title"], font=("Segoe UI Semibold", 9))
        self.content = tk.Frame(self, bg=self.default_bg)
        self.content.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        HoverTip(self.info_icon, tooltip_text)


class AnalysisPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="App.TFrame", padding=24)
        self.app = app
        self.records = []

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar_host = ttk.Frame(self, style="App.TFrame")
        self.sidebar_host.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        self.scroll = ScrollableFrame(self, bg_color=THEME["bg"])
        self.scroll.grid(row=0, column=1, sticky="nsew")
        self.scroll.h_scrollbar.grid_remove()
        self.scroll.canvas.bind("<Configure>", self._fit_to_width, add="+")

    def refresh(self):
        for widget in self.sidebar_host.winfo_children():
            widget.destroy()
        NavigationSidebar(self.sidebar_host, self.app, "AnalysisPage").pack(fill="y", expand=True)

        body = self.scroll.content
        for widget in body.winfo_children():
            widget.destroy()

        body.configure(style="App.TFrame")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        board = tk.Frame(body, bg=THEME["bg"])
        board.grid(row=0, column=0, sticky="nsew")
        for col in range(6):
            board.grid_columnconfigure(col, weight=1, uniform="dashboard")

        try:
            metrics = fetch_overview_metrics()
            diseases = fetch_group_counts("disease")
            conditions = fetch_group_counts("medical_condition")
            specialists = fetch_group_counts("specialist")
            doctors = fetch_group_counts("doctor")
            billing = fetch_bill_by_group("disease")
        except Exception as error:
            tk.Label(
                board,
                text=f"Database Error: {error}",
                bg=THEME["bg"],
                fg="#ffb4b4",
                font=("Segoe UI Semibold", 14),
                justify="left",
                wraplength=1000,
            ).grid(row=0, column=0, sticky="w")
            return

        self._build_header(board)
        self._build_summary_tiles(board, metrics)
        self._build_ring_panel(board, 3, 0, 2, "Disease Distribution", diseases, "Shows the top disease categories from your live healthcare records.")
        self._build_ring_panel(board, 3, 2, 2, "Condition Mix", conditions, "Shows medical condition categories and their current proportion.")
        self._build_bar_panel(board, 3, 4, 2, "Doctor Workload", doctors, "Shows how many records are linked to each doctor.")
        self._build_ring_panel(board, 4, 0, 3, "Specialist Coverage", specialists, "Shows specialist participation across all records.")
        self._build_funnel_panel(board, 4, 3, 3, billing)
        self._build_trend_panel(board, 5, 0, 3)
        self._build_center_panel(board, 5, 3, 3, metrics)

    def _fit_to_width(self, event):
        self.scroll.canvas.itemconfigure(self.scroll.window, width=max(event.width, 1200))

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=THEME["bg"])
        header.grid(row=0, column=0, columnspan=12, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        badge = tk.Canvas(header, width=62, height=62, bg=THEME["bg"], highlightthickness=0)
        badge.grid(row=0, column=0, padx=(6, 14), sticky="w")
        badge.create_oval(2, 2, 60, 60, fill="#0f2940", outline=THEME["border"])
        badge.create_rectangle(27, 15, 35, 47, fill=THEME["blue"], outline="")
        badge.create_rectangle(15, 27, 47, 35, fill=THEME["blue"], outline="")

        title_wrap = tk.Frame(header, bg=THEME["bg"])
        title_wrap.grid(row=0, column=1, sticky="w")
        tk.Label(
            title_wrap,
            text="HOSPITAL ANALYSIS DASHBOARD",
            bg=THEME["bg"],
            fg=THEME["title"],
            font=("Segoe UI Semibold", 27),
        ).pack(anchor="w")
        tk.Label(
            title_wrap,
            text="Live healthcare intelligence with better chart spacing, clearer cards, and full hospital data visibility.",
            bg=THEME["bg"],
            fg=THEME["muted"],
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            header,
            text=datetime.now().strftime("%Y-%m-%d    %H:%M:%S"),
            bg=THEME["bg"],
            fg=THEME["muted"],
            font=("Segoe UI", 11),
        ).grid(row=0, column=2, sticky="ne", padx=(12, 6))

    def _build_summary_tiles(self, parent, metrics):
        tiles = [
            ("Patients", metrics["total_patients"], "Patient volume", THEME["blue"]),
            ("Doctors", metrics["total_doctors"], "Doctor network", THEME["teal"]),
            ("Hospitals", metrics["total_hospitals"], "Hospital count", THEME["orange"]),
            ("Records", metrics["total_records"], "Clinical entries", THEME["purple"]),
            ("Diseases", metrics["total_diseases"], "Disease categories", THEME["pink"]),
            ("Avg Bill", f"Rs {metrics['average_bill']:,.0f}", "Per-entry average", THEME["yellow"]),
        ]
        for index, (label, value, sub, accent) in enumerate(tiles):
            panel = HoverPanel(parent, label, accent, f"{label}: {sub}. This card updates from the SQL Server data.")
            panel.grid(row=1 + (index // 3), column=(index % 3) * 2, columnspan=2, sticky="nsew", padx=6, pady=6)
            tk.Label(panel.content, text=str(value), bg=panel.default_bg, fg=THEME["title"], font=("Segoe UI Semibold", 20)).pack(anchor="w", pady=(4, 4))
            tk.Label(panel.content, text=sub, bg=panel.default_bg, fg=THEME["muted"], font=("Segoe UI", 9)).pack(anchor="w")

    def _build_ring_panel(self, parent, row, column, span, title, rows, tooltip):
        panel = HoverPanel(parent, title, THEME["blue"], tooltip)
        panel.grid(row=row, column=column, columnspan=span, sticky="nsew", padx=6, pady=6)
        panel.grid_propagate(False)
        panel.configure(height=260)

        holder = tk.Frame(panel.content, bg=panel.default_bg)
        holder.pack(fill="both", expand=True)

        chart = tk.Canvas(holder, width=200, height=170, bg=panel.default_bg, highlightthickness=0)
        chart.pack(side="top", pady=(4, 6))
        self._draw_donut(chart, rows)

        legend = tk.Frame(holder, bg=panel.default_bg)
        legend.pack(fill="x", pady=(2, 0))
        for column_index in range(2):
            legend.grid_columnconfigure(column_index, weight=1)
        for index, row_data in enumerate(rows[:5]):
            line = tk.Frame(legend, bg=panel.default_bg)
            line.grid(row=index // 2, column=index % 2, sticky="w", padx=(0, 10), pady=3)
            dot = tk.Canvas(line, width=12, height=12, bg=panel.default_bg, highlightthickness=0)
            dot.pack(side="left")
            fill = CHART_COLORS[index % len(CHART_COLORS)]
            dot.create_oval(2, 2, 10, 10, fill=fill, outline="")
            HoverTip(dot, f"{row_data['label']}: {row_data['total']} records")
            label = row_data["label"]
            if len(label) > 11:
                label = label[:9] + ".."
            label_widget = tk.Label(line, text=f"{label} ({row_data['total']})", bg=panel.default_bg, fg=THEME["text"], font=("Segoe UI", 9), anchor="w")
            label_widget.pack(side="left", padx=(6, 0))
            HoverTip(label_widget, f"{row_data['label']}: {row_data['total']} records")

    def _build_bar_panel(self, parent, row, column, span, title, rows, tooltip):
        panel = HoverPanel(parent, title, THEME["teal"], tooltip)
        panel.grid(row=row, column=column, columnspan=span, sticky="nsew", padx=6, pady=6)
        panel.configure(height=260)
        tk.Label(
            panel.content,
            text="Use the small info icon for details. Horizontal scroll keeps doctor names readable.",
            bg=panel.default_bg,
            fg=THEME["muted"],
            font=("Segoe UI", 9),
            justify="left",
            wraplength=360,
        ).pack(anchor="w", pady=(0, 4))

        holder = tk.Frame(panel.content, bg=panel.default_bg)
        holder.pack(fill="both", expand=True)
        chart = tk.Canvas(holder, height=170, bg=panel.default_bg, highlightthickness=0)
        scroll = ttk.Scrollbar(holder, orient="horizontal", command=chart.xview)
        chart.configure(xscrollcommand=scroll.set)
        chart.pack(fill="both", expand=True)
        scroll.pack(fill="x", pady=(4, 0))
        self._draw_vertical_bars(chart, rows)

    def _build_trend_panel(self, parent, row, column, span):
        panel = HoverPanel(parent, "Monthly Admission Trend", THEME["blue"], "Shows monthly admissions and billing movement from your current records.")
        panel.grid(row=row, column=column, columnspan=span, rowspan=1, sticky="nsew", padx=6, pady=6)
        panel.configure(height=340)
        chart = tk.Canvas(panel.content, height=260, bg=panel.default_bg, highlightthickness=0)
        chart.pack(fill="both", expand=True)
        self._draw_line_trend(chart)

    def _build_center_panel(self, parent, row, column, span, metrics):
        panel = HoverPanel(parent, "Healthcare Operations Pulse", THEME["orange"], "Highlights the core healthcare totals and combined billing value.")
        panel.grid(row=row, column=column, columnspan=span, rowspan=1, sticky="nsew", padx=6, pady=6)
        panel.configure(height=340)
        canvas = tk.Canvas(panel.content, height=260, bg=panel.default_bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.bind(
            "<Configure>",
            lambda _event: self._draw_center_score(
                canvas,
                metrics["total_bill"],
                metrics["total_records"],
                metrics["total_doctors"],
                metrics["total_hospitals"],
            ),
        )
        self._draw_center_score(canvas, metrics["total_bill"], metrics["total_records"], metrics["total_doctors"], metrics["total_hospitals"])

    def _build_funnel_panel(self, parent, row, column, span, rows):
        panel = HoverPanel(parent, "Billing Funnel by Disease", THEME["pink"], "Compares disease categories by total billing contribution.")
        panel.grid(row=row, column=column, columnspan=span, rowspan=1, sticky="nsew", padx=6, pady=6)
        panel.configure(height=340)
        chart = tk.Canvas(panel.content, height=260, bg=panel.default_bg, highlightthickness=0)
        chart.pack(fill="both", expand=True)
        self._draw_funnel(chart, rows)

    def _draw_donut(self, canvas, rows):
        canvas.delete("all")
        if not rows:
            return
        total = sum(row["total"] for row in rows) or 1
        x1, y1, x2, y2 = 20, 15, 150, 145
        start = 90
        non_zero = [row for row in rows if float(row["total"]) > 0]
        raw_extents = [(float(row["total"]) / total) * 360 for row in non_zero]
        min_extent = 5
        adjusted = [max(min_extent, extent) for extent in raw_extents]
        scale = 360 / sum(adjusted) if adjusted else 1
        adjusted = [extent * scale for extent in adjusted]

        for index, row in enumerate(non_zero):
            extent = -adjusted[index]
            arc = canvas.create_arc(x1, y1, x2, y2, start=start, extent=extent, fill=CHART_COLORS[index % len(CHART_COLORS)], outline=THEME["panel"], width=1)
            canvas.tag_bind(arc, "<Enter>", lambda _e, r=row: self._show_canvas_tip(canvas, f"{r['label']}: {r['total']} records"))
            canvas.tag_bind(arc, "<Leave>", lambda _e: self._hide_canvas_tip())
            start += extent
        canvas.create_oval(55, 50, 115, 110, fill=THEME["panel"], outline=THEME["panel"])
        canvas.create_text(85, 70, text=str(total), fill=THEME["title"], font=("Segoe UI Semibold", 11))
        canvas.create_text(85, 90, text="records", fill=THEME["muted"], font=("Segoe UI", 9))

    def _draw_vertical_bars(self, canvas, rows):
        canvas.delete("all")
        if not rows:
            return
        visible_width = max(canvas.winfo_width(), 420)
        bar_width = 34
        gap = 12
        left = 28
        base_y = 135
        chart_width = max(visible_width, left + len(rows) * (bar_width + gap) + 40)
        canvas.configure(scrollregion=(0, 0, chart_width, 170))
        max_value = max(float(row["total"]) for row in rows) or 1
        canvas.create_line(20, base_y, chart_width - 16, base_y, fill="#355879", width=2)
        for index, row in enumerate(rows):
            x1 = left + index * (bar_width + gap)
            x2 = x1 + bar_width
            height = (float(row["total"]) / max_value) * 90
            y1 = base_y - height
            color = CHART_COLORS[index % len(CHART_COLORS)]
            bar = canvas.create_rectangle(x1, y1, x2, base_y, fill=color, outline="")
            canvas.tag_bind(bar, "<Enter>", lambda _e, r=row: self._show_canvas_tip(canvas, f"{r['label']}: {int(r['total'])} records"))
            canvas.tag_bind(bar, "<Leave>", lambda _e: self._hide_canvas_tip())
            canvas.create_text((x1 + x2) / 2, y1 - 8, text=str(int(row["total"])), fill=THEME["title"], font=("Segoe UI", 8))
            label = str(row["label"])
            if len(label) > 10:
                label = label[:8] + ".."
            canvas.create_text((x1 + x2) / 2, base_y + 18, text=label, fill=THEME["muted"], font=("Segoe UI", 8), width=78)

    def _draw_line_trend(self, canvas):
        canvas.delete("all")
        width = max(canvas.winfo_width(), 540)
        height = 250
        left, top, right, bottom = 52, 24, width - 72, 210
        canvas.create_rectangle(0, 0, width, height, fill=THEME["panel"], outline="")
        canvas.create_oval(60, 170, width - 20, 320, fill="#0c2440", outline="")

        monthly = defaultdict(lambda: {"count": 0, "bill": 0.0})
        for row in fetch_detailed_records():
            date_obj = self._parse_date(row.get("admitted_date"))
            if not date_obj:
                continue
            month_key = date_obj.strftime("%Y-%m")
            monthly[month_key]["count"] += 1
            monthly[month_key]["bill"] += float(row.get("bill_amount") or 0)

        sorted_months = sorted(monthly.items())[-6:]
        items = [
            (
                datetime.strptime(month_key, "%Y-%m").strftime("%b"),
                {
                    "count": values["count"],
                    "bill": max(values["bill"], 1.0),
                },
            )
            for month_key, values in sorted_months
        ]
        if not items:
            return

        for step in range(5):
            y = top + step * ((bottom - top) / 4)
            canvas.create_line(left, y, right, y, fill="#254563")

        max_count = max(item[1]["count"] for item in items) or 1
        max_bill = max(item[1]["bill"] for item in items) or 1
        gap = (right - left) / max(1, len(items) - 1)
        count_pts = []
        bill_pts = []
        for index, (label, data) in enumerate(items):
            x = left + index * gap
            y1 = bottom - (data["count"] / max_count) * (bottom - top - 10)
            y2 = bottom - (data["bill"] / max_bill) * (bottom - top - 10)
            count_pts.extend([x, y1])
            bill_pts.extend([x, y2])
            canvas.create_text(x, bottom + 18, text=label, fill=THEME["muted"], font=("Segoe UI", 9))
        canvas.create_line(count_pts, fill=THEME["blue"], width=3, smooth=True)
        canvas.create_line(bill_pts, fill=THEME["pink"], width=3, smooth=True)
        for i in range(0, len(count_pts), 2):
            x, y = count_pts[i], count_pts[i + 1]
            dot = canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=THEME["blue"], outline="#cbe7ff", width=2)
            item = items[i // 2]
            canvas.tag_bind(dot, "<Enter>", lambda _e, it=item: self._show_canvas_tip(canvas, f"{it[0]} admissions: {it[1]['count']}"))
            canvas.tag_bind(dot, "<Leave>", lambda _e: self._hide_canvas_tip())
        for i in range(0, len(bill_pts), 2):
            x, y = bill_pts[i], bill_pts[i + 1]
            dot = canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=THEME["pink"], outline="#ffd3dd", width=2)
            item = items[i // 2]
            canvas.tag_bind(dot, "<Enter>", lambda _e, it=item: self._show_canvas_tip(canvas, f"{it[0]} billing: Rs {it[1]['bill']:,.0f}"))
            canvas.tag_bind(dot, "<Leave>", lambda _e: self._hide_canvas_tip())
        canvas.create_text(left + 10, 10, text="Admissions", fill=THEME["blue"], font=("Segoe UI Semibold", 10), anchor="w")
        canvas.create_text(left + 120, 10, text="Billing", fill=THEME["pink"], font=("Segoe UI Semibold", 10), anchor="w")

    def _draw_center_score(self, canvas, total_bill, records, doctors, hospitals):
        canvas.delete("all")
        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 250)
        canvas.create_rectangle(0, 0, width, height, fill=THEME["panel"], outline="")
        canvas.create_oval(-20, height - 80, width + 20, height + 100, fill="#123353", outline="")
        canvas.create_oval(40,
                           height - 55, width - 40, height + 28, fill="#1b4063", outline="")
        canvas.create_arc(50, 26, width - 50, height - 10, start=200, extent=140, style="arc", outline="#4a7fb0", width=2)
        dots = [("Records", records, THEME["teal"]), ("Doctors", doctors, THEME["orange"]), ("Hospitals", hospitals, THEME["purple"])]
        start_x = 48
        for index, (label, value, color) in enumerate(dots):
            x = start_x + index * 108
            canvas.create_oval(x, 22, x + 18, 40, fill=color, outline="")
            canvas.create_text(x + 28, 30, text=label, fill=THEME["muted"], font=("Segoe UI Semibold", 10), anchor="w")
            canvas.create_text(x + 28, 48, text=str(value), fill=THEME["title"], font=("Segoe UI Semibold", 12), anchor="w")
        canvas.create_text(width / 2, height / 2 + 10, text=f"Rs {total_bill:,.0f}", fill=THEME["blue"], font=("Segoe UI Light", 28))
        canvas.create_text(width / 2, height / 2 + 38, text="Total Billing Value", fill=THEME["muted"], font=("Segoe UI", 11))

    def _draw_funnel(self, canvas, rows):
        canvas.delete("all")
        width = max(canvas.winfo_width(), 220)
        if not rows:
            return
        filtered = [row for row in rows if float(row["total"]) > 0][:7]
        top_width = max(110, width - 34)
        center_x = width / 2
        start_y = 22
        seg_h = 26
        legend_y = start_y + len(filtered) * seg_h + 14
        required_height = legend_y + len(filtered) * 16 + 24
        canvas.configure(height=max(260, required_height), scrollregion=(0, 0, width, max(260, required_height)))
        for index, row in enumerate(filtered):
            ratio = 1 - (index / (len(filtered) + 1))
            next_ratio = 1 - ((index + 1) / (len(filtered) + 1))
            w1 = top_width * ratio
            w2 = top_width * next_ratio
            y1 = start_y + index * seg_h
            y2 = y1 + seg_h - 3
            points = [center_x - w1 / 2, y1, center_x + w1 / 2, y1, center_x + w2 / 2, y2, center_x - w2 / 2, y2]
            poly = canvas.create_polygon(points, fill=CHART_COLORS[index % len(CHART_COLORS)], outline=THEME["panel"])
            canvas.tag_bind(poly, "<Enter>", lambda _e, r=row: self._show_canvas_tip(canvas, f"{r['label']}: Rs {r['total']:,.0f}"))
            canvas.tag_bind(poly, "<Leave>", lambda _e: self._hide_canvas_tip())
        for index, row in enumerate(filtered):
            color = CHART_COLORS[index % len(CHART_COLORS)]
            lx = 18
            ly = legend_y + index * 16
            canvas.create_oval(lx, ly, lx + 10, ly + 10, fill=color, outline="")
            label = row["label"]
            if len(label) > 14:
                label = label[:12] + ".."
            canvas.create_text(lx + 16, ly + 5, text=label, fill=THEME["text"], font=("Segoe UI", 8), anchor="w")

    def _show_canvas_tip(self, canvas, text):
        if hasattr(self, "_canvas_tip") and self._canvas_tip:
            self._canvas_tip.destroy()
            self._canvas_tip = None
        tip = tk.Toplevel(canvas)
        tip.wm_overrideredirect(True)
        x = canvas.winfo_pointerx() + 14
        y = canvas.winfo_pointery() + 14
        tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            tip,
            text=text,
            bg=THEME["panel_hover"],
            fg=THEME["title"],
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            padx=8,
            pady=4,
        ).pack()
        self._canvas_tip = tip

    def _hide_canvas_tip(self):
        if hasattr(self, "_canvas_tip") and self._canvas_tip:
            self._canvas_tip.destroy()
            self._canvas_tip = None

    def _parse_date(self, value):
        text = str(value).strip()
        if not text or text.lower() == "none":
            return None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(text[:19], fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text[:19])
        except ValueError:
            return None
