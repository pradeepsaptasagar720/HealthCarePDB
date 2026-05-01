import tkinter as tk
from tkinter import ttk


COLORS = {
    "bg": "#F4F8FB",
    "surface": "#FFFFFF",
    "surface_alt": "#EAF3FF",
    "primary": "#0B6E99",
    "primary_dark": "#084C6D",
    "text": "#1E293B",
    "muted": "#64748B",
    "border": "#DCE7F3",
    "success": "#16A34A",
    "warning": "#F59E0B",
    "danger": "#DC2626",
    "teal": "#14B8A6",
    "slate": "#334155",
}


def configure_styles(root):
    root.configure(bg=COLORS["bg"])
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("App.TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["surface"], relief="flat", borderwidth=1)
    style.configure("SoftCard.TFrame", background=COLORS["surface_alt"], relief="flat", borderwidth=0)
    style.configure("Accent.TFrame", background=COLORS["primary"])

    style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI Semibold", 26))
    style.configure("Subtitle.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 11))
    style.configure("CardTitle.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=("Segoe UI Semibold", 17))
    style.configure("CardBody.TLabel", background=COLORS["surface"], foreground=COLORS["muted"], font=("Segoe UI", 11))
    style.configure("FieldLabel.TLabel", background=COLORS["surface"], foreground=COLORS["slate"], font=("Segoe UI Semibold", 10))
    style.configure("HeroTitle.TLabel", background=COLORS["primary"], foreground="white", font=("Segoe UI Semibold", 28))
    style.configure("HeroLead.TLabel", background=COLORS["primary"], foreground="#E6F5FB", font=("Segoe UI", 12))
    style.configure("HeroPoint.TLabel", background=COLORS["primary"], foreground="#D7EDF7", font=("Segoe UI", 11))

    style.configure("Primary.TButton", background=COLORS["primary"], foreground="white", font=("Segoe UI Semibold", 10), padding=12, borderwidth=0)
    style.map("Primary.TButton", background=[("active", COLORS["primary_dark"])])

    style.configure("Secondary.TButton", background=COLORS["surface_alt"], foreground=COLORS["text"], font=("Segoe UI Semibold", 10), padding=12, borderwidth=0)
    style.map("Secondary.TButton", background=[("active", "#D8E8FF")])

    style.configure("Nav.TButton", background=COLORS["surface_alt"], foreground=COLORS["text"], font=("Segoe UI Semibold", 10), padding=10, borderwidth=0)
    style.map("Nav.TButton", background=[("active", "#D8E8FF")])

    style.configure("App.TEntry", fieldbackground="white", bordercolor=COLORS["border"], lightcolor=COLORS["border"], darkcolor=COLORS["border"], padding=10)

    style.configure("Treeview", font=("Segoe UI", 10), rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10), background=COLORS["surface_alt"], foreground=COLORS["text"])


class NavigationSidebar(ttk.Frame):
    def __init__(self, parent, app, active_page):
        super().__init__(parent, style="Card.TFrame", padding=20)
        self.app = app

        brand = ttk.Frame(self, style="Card.TFrame")
        brand.pack(fill="x", pady=(0, 16))
        make_icon_badge(brand, "brand", size=48).pack(side="left", padx=(0, 10))
        brand_text = ttk.Frame(brand, style="Card.TFrame")
        brand_text.pack(side="left", fill="x", expand=True)
        ttk.Label(brand_text, text="CareVista", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(brand_text, text="Healthcare BI", style="CardBody.TLabel").pack(anchor="w", pady=(2, 0))
        ttk.Label(
            self,
            text="Healthcare desktop workspace for records, reporting, and live operational analysis.",
            style="CardBody.TLabel",
            wraplength=190,
            justify="left",
        ).pack(anchor="w", pady=(4, 20))

        self._btn("Dashboard", "HomePage", active_page)
        self._btn("Analysis", "AnalysisPage", active_page)
        self._btn("Data Entry", "FormPage", active_page)
        self._btn("View Data Info", "ViewDataInfoPage", active_page)
        self._btn("About", "AboutPage", active_page)

        ttk.Separator(self).pack(fill="x", pady=20)
        user_name = app.current_user.get("username", "User") if isinstance(app.current_user, dict) else "User"
        ttk.Label(self, text=user_name, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(self, text="SQL Server user", style="CardBody.TLabel").pack(anchor="w", pady=(4, 18))
        ttk.Button(self, text="Logout", style="Secondary.TButton", command=app.logout).pack(fill="x")

    def _btn(self, text, page, active):
        style = "Primary.TButton" if page == active else "Nav.TButton"
        ttk.Button(self, text=text, style=style, command=lambda: self.app.open_page(page)).pack(fill="x", pady=5)


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, bg_color=None):
        super().__init__(parent)
        canvas_bg = bg_color or COLORS["bg"]

        self.canvas = tk.Canvas(self, bg=canvas_bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.content = ttk.Frame(self.canvas, style="App.TFrame")
        self.scrollable_frame = self.content
        self.window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        self.content.bind("<Enter>", self._bind_mousewheel)
        self.content.bind("<Leave>", self._unbind_mousewheel)

    def _on_content_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        requested = max(self.content.winfo_reqwidth(), event.width)
        self.canvas.itemconfigure(self.window, width=requested)

    def _bind_mousewheel(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _unbind_mousewheel(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")


def create_healthcare_hero(parent, title, body, points):
    hero = tk.Frame(parent, bg=COLORS["primary"], bd=0, highlightthickness=0)
    hero.grid_propagate(False)
    hero.columnconfigure(0, weight=1)

    bg = tk.Canvas(hero, bg=COLORS["primary"], highlightthickness=0, bd=0)
    bg.place(relx=0, rely=0, relwidth=1, relheight=1)

    def redraw(_event=None):
        width = max(bg.winfo_width(), 420)
        height = max(bg.winfo_height(), 520)
        bg.delete("all")
        bg.create_rectangle(0, 0, width, height, fill=COLORS["primary"], outline="")
        bg.create_oval(width - 220, -40, width + 80, 220, fill="#167BA8", outline="")
        bg.create_oval(-80, height - 180, 220, height + 80, fill="#0A5C7E", outline="")
        bg.create_rectangle(48, height - 185, width - 70, height - 85, fill="#D8EFF7", outline="")
        bg.create_rectangle(70, height - 265, width - 110, height - 185, fill="#EFF8FC", outline="")
        bg.create_rectangle(width - 175, height - 245, width - 110, height - 85, fill="#C7E7F2", outline="")
        bg.create_rectangle(98, height - 238, 148, height - 85, fill="#B8E1F0", outline="")
        bg.create_rectangle(70, height - 215, width - 175, height - 200, fill="#DCEFFA", outline="")
        bg.create_rectangle((width / 2) - 16, height - 245, (width / 2) + 16, height - 170, fill="#2DD4BF", outline="")
        bg.create_rectangle((width / 2) - 48, height - 215, (width / 2) + 48, height - 201, fill="#2DD4BF", outline="")
        for row in range(2):
            for col in range(5):
                x1 = 180 + col * 54
                y1 = height - 245 + row * 34
                bg.create_rectangle(x1, y1, x1 + 28, y1 + 18, fill="#A7D8EC", outline="")
        bg.create_rectangle(width - 210, height - 155, width - 190, height - 85, fill="#95D5E4", outline="")
        bg.create_rectangle(width - 170, height - 155, width - 150, height - 85, fill="#95D5E4", outline="")
        bg.create_rectangle(width - 130, height - 155, width - 110, height - 85, fill="#95D5E4", outline="")

    bg.bind("<Configure>", redraw)

    content = ttk.Frame(hero, style="Accent.TFrame", padding=44)
    content.place(relx=0, rely=0, relwidth=1, relheight=1)

    ttk.Label(content, text=title, style="HeroTitle.TLabel", wraplength=430, justify="left").pack(anchor="w", pady=(8, 18))
    ttk.Label(content, text=body, style="HeroLead.TLabel", wraplength=430, justify="left").pack(anchor="w", pady=(0, 20))
    for line in points:
        ttk.Label(content, text=f"- {line}", style="HeroPoint.TLabel", wraplength=430, justify="left").pack(anchor="w", pady=7)

    return hero


def make_icon_badge(parent, kind="brand", size=44):
    canvas = tk.Canvas(parent, width=size, height=size, bg=COLORS["surface"], highlightthickness=0, bd=0)
    canvas.create_oval(2, 2, size - 2, size - 2, fill="#E6F5FB", outline="")

    cx = size / 2
    cy = size / 2
    accent = COLORS["primary"]

    if kind in ("brand", "health", "login", "register"):
        canvas.create_rectangle(cx - 4, cy - 12, cx + 4, cy + 12, fill=accent, outline="")
        canvas.create_rectangle(cx - 12, cy - 4, cx + 12, cy + 4, fill=accent, outline="")
    elif kind == "home":
        canvas.create_polygon(cx, cy - 12, cx - 12, cy - 1, cx - 12, cy + 12, cx + 12, cy + 12, cx + 12, cy - 1, fill=accent, outline="")
        canvas.create_rectangle(cx - 4, cy + 2, cx + 4, cy + 12, fill="#E6F5FB", outline="")
    elif kind == "form":
        canvas.create_rectangle(cx - 12, cy - 12, cx + 12, cy + 12, fill=accent, outline="")
        for offset in (-6, 0, 6):
            canvas.create_line(cx - 7, cy + offset, cx + 7, cy + offset, fill="white", width=2)
        canvas.create_rectangle(cx - 9, cy - 9, cx - 4, cy - 4, fill="#E6F5FB", outline="")
    elif kind == "analysis":
        canvas.create_rectangle(cx - 11, cy + 3, cx - 5, cy + 12, fill=accent, outline="")
        canvas.create_rectangle(cx - 2, cy - 4, cx + 4, cy + 12, fill=accent, outline="")
        canvas.create_rectangle(cx + 7, cy - 10, cx + 13, cy + 12, fill=accent, outline="")
    elif kind == "about":
        canvas.create_oval(cx - 11, cy - 11, cx + 11, cy + 11, fill=accent, outline="")
        canvas.create_text(cx, cy - 1, text="i", fill="white", font=("Segoe UI Semibold", max(10, int(size / 2.6))))
    elif kind == "doctor":
        canvas.create_oval(cx - 10, cy - 12, cx + 10, cy + 8, fill=accent, outline="")
        canvas.create_rectangle(cx - 4, cy + 8, cx + 4, cy + 14, fill=accent, outline="")
    elif kind == "hospital":
        canvas.create_rectangle(cx - 11, cy - 12, cx + 11, cy + 12, fill=accent, outline="")
        canvas.create_rectangle(cx - 3, cy - 8, cx + 3, cy + 8, fill="white", outline="")
        canvas.create_rectangle(cx - 8, cy - 3, cx + 8, cy + 3, fill="white", outline="")
    elif kind == "patient":
        canvas.create_oval(cx - 10, cy - 13, cx + 10, cy + 7, fill=accent, outline="")
        canvas.create_arc(cx - 14, cy - 2, cx + 14, cy + 16, start=0, extent=180, style="chord", fill=accent, outline="")
    elif kind == "view_data":
        canvas.create_rectangle(cx - 12, cy - 10, cx + 12, cy - 6, fill=accent, outline="")
        canvas.create_rectangle(cx - 12, cy - 2, cx + 12, cy + 2, fill=accent, outline="")
        canvas.create_rectangle(cx - 12, cy + 6, cx + 12, cy + 10, fill=accent, outline="")
    return canvas


def make_page_header(parent, title, subtitle, icon_kind="health"):
    wrap = ttk.Frame(parent, style="App.TFrame")
    wrap.columnconfigure(1, weight=1)
    make_icon_badge(wrap, icon_kind, size=56).grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))
    ttk.Label(wrap, text=title, style="Title.TLabel").grid(row=0, column=1, sticky="w")
    ttk.Label(wrap, text=subtitle, style="Subtitle.TLabel", wraplength=860, justify="left").grid(row=1, column=1, sticky="w", pady=(6, 0))
    return wrap


def make_section_badge(parent, title, body, icon_kind="health"):
    card = ttk.Frame(parent, style="Card.TFrame", padding=20)
    card.columnconfigure(1, weight=1)
    make_icon_badge(card, icon_kind, size=52).grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 14))
    ttk.Label(card, text=title, style="CardTitle.TLabel").grid(row=0, column=1, sticky="w")
    ttk.Label(card, text=body, style="CardBody.TLabel", wraplength=720, justify="left").grid(row=1, column=1, sticky="w", pady=(8, 0))
    return card


def make_metric_card(parent, title, value, body):
    card = ttk.Frame(parent, style="Card.TFrame", padding=20)
    accent = tk.Frame(card, bg=COLORS["primary"], width=5)
    accent.pack(side="left", fill="y", padx=(0, 12))

    content = ttk.Frame(card, style="Card.TFrame")
    content.pack(fill="both", expand=True)
    ttk.Label(content, text=title, style="CardBody.TLabel").pack(anchor="w")
    ttk.Label(content, text=value, font=("Segoe UI Semibold", 22), foreground=COLORS["primary"], background=COLORS["surface"]).pack(anchor="w", pady=(6, 5))
    ttk.Label(content, text=body, style="CardBody.TLabel").pack(anchor="w")
    return card


def estimate_chart_height(row_count):
    return max(230, min(700, 90 + row_count * 34))


def _truncate_label(label, limit=24):
    text = str(label)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def draw_bar_chart(canvas, rows, colors=None, currency=False):
    canvas.delete("all")
    width = max(canvas.winfo_width(), int(canvas.cget("width") or 640), 640)
    height = int(canvas.cget("height") or 300)
    canvas.configure(scrollregion=(0, 0, width, height))

    if not rows:
        canvas.create_text(width / 2, height / 2, text="No data available.", fill=COLORS["muted"], font=("Segoe UI", 11))
        return

    palette = colors or [COLORS["primary"], COLORS["teal"], COLORS["success"], "#6366F1", COLORS["warning"]]
    max_value = max(float(row["total"]) for row in rows) or 1
    left = 170
    right = width - 28
    top = 22
    row_gap = 30
    bar_height = 18

    for index, row in enumerate(rows):
        y = top + index * row_gap
        x0 = left
        x1 = left + ((float(row["total"]) / max_value) * max(160, right - left))
        color = palette[index % len(palette)]

        canvas.create_text(18, y + 9, text=_truncate_label(row["label"]), anchor="w", fill=COLORS["text"], font=("Segoe UI", 9))
        canvas.create_rectangle(x0, y, x1, y + bar_height, fill=color, outline="")
        value_text = f"Rs {float(row['total']):,.0f}" if currency else f"{int(row['total'])}"
        canvas.create_text(min(right, x1 + 10), y + 9, text=value_text, anchor="w", fill=COLORS["muted"], font=("Segoe UI", 9))


def draw_scrollable_vertical_chart(canvas, rows, colors=None, currency=False):
    canvas.delete("all")
    if not rows:
        canvas.configure(scrollregion=(0, 0, 640, 260))
        canvas.create_text(320, 130, text="No data available.", fill=COLORS["muted"], font=("Segoe UI", 11))
        return

    palette = colors or [COLORS["primary"], COLORS["teal"], COLORS["success"], "#6366F1", COLORS["warning"]]
    visible_width = max(canvas.winfo_width(), 640)
    count = len(rows)
    bar_width = 54
    gap = 20
    left = 34
    base_y = 225
    chart_width = max(visible_width, left + count * (bar_width + gap) + 40)
    max_value = max(float(row["total"]) for row in rows) or 1

    canvas.configure(scrollregion=(0, 0, chart_width, 270))
    canvas.create_line(26, base_y, chart_width - 18, base_y, fill=COLORS["border"], width=2)

    for index, row in enumerate(rows):
        x1 = left + index * (bar_width + gap)
        x2 = x1 + bar_width
        height = (float(row["total"]) / max_value) * 138
        y1 = base_y - height
        color = palette[index % len(palette)]
        canvas.create_rectangle(x1, y1, x2, base_y, fill=color, outline="")
        value_text = f"Rs {float(row['total']):,.0f}" if currency else f"{int(row['total'])}"
        canvas.create_text((x1 + x2) / 2, y1 - 10, text=value_text, fill=COLORS["text"], font=("Segoe UI", 9))
        canvas.create_text((x1 + x2) / 2, base_y + 22, text=_truncate_label(row["label"], 14), width=80, fill=COLORS["muted"], font=("Segoe UI", 9))
