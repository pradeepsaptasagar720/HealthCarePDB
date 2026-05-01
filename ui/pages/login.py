from tkinter import StringVar, messagebox
from tkinter import ttk

from db.db_connection import authenticate_user
from ui.components import create_healthcare_hero, make_icon_badge


class LoginPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="App.TFrame", padding=36)
        self.app = app
        self.username = StringVar()
        self.password = StringVar()
        self.columnconfigure(0, weight=6)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=1)

        hero = create_healthcare_hero(
            self,
            "Healthcare Analytics\nWorkspace",
            "Manage healthcare records, monitor live insights, and keep patient, doctor, hospital, and billing data connected in one professional workspace.",
            (
                "Hospital-themed healthcare illustration",
                "Live SQL Server-based analysis",
                "Clean login and reporting workflow",
                "Professional patient and doctor dashboard",
            ),
        )
        hero.grid(row=0, column=0, sticky="nsew", padx=(0, 22))

        card = ttk.Frame(self, style="Card.TFrame", padding=40)
        card.grid(row=0, column=1, sticky="nsew")
        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x")
        make_icon_badge(top, "login", size=42).pack(side="left", padx=(0, 10))
        ttk.Label(top, text="Login", style="CardTitle.TLabel").pack(side="left", anchor="w")
        ttk.Label(
            card,
            text="Sign in to continue to the healthcare reporting workspace.",
            style="CardBody.TLabel",
            wraplength=380,
            justify="left",
        ).pack(anchor="w", pady=(8, 22))
        self._field(card, "Username", self.username)
        self._field(card, "Password", self.password, show="*")
        ttk.Button(card, text="→ Login", style="Primary.TButton", command=self.login).pack(fill="x", pady=(22, 10))
        ttk.Button(card, text="✚ Create Account", style="Secondary.TButton", command=lambda: self.app.show_page("RegisterPage")).pack(fill="x")

    def _field(self, parent, label, variable, show=None):
        ttk.Label(parent, text=label, style="FieldLabel.TLabel").pack(anchor="w", pady=(10, 6))
        ttk.Entry(parent, textvariable=variable, style="App.TEntry", show=show).pack(fill="x")

    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing Details", "Enter username and password.")
            return
        try:
            user = authenticate_user(username, password)
            if not user:
                messagebox.showerror("Login Failed", "Invalid credentials.")
                return
            self.password.set("")
            self.app.login(user)
        except Exception as error:
            messagebox.showerror("Database Error", str(error))
