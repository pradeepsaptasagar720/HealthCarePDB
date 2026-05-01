from tkinter import StringVar, messagebox
from tkinter import ttk

from db.db_connection import register_user
from ui.components import create_healthcare_hero, make_icon_badge


class RegisterPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="App.TFrame", padding=36)
        self.app = app
        self.username = StringVar()
        self.password = StringVar()
        self.confirm_password = StringVar()
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=1)

        hero = create_healthcare_hero(
            self,
            "Create Your\nHealthcare Account",
            "Register a new account while keeping your existing SQL Server healthcare workflow and reporting pipeline unchanged.",
            (
                "Hospital-inspired healthcare background",
                "Works with the same user table",
                "Protects the current login flow",
                "Designed for a cleaner onboarding experience",
            ),
        )
        hero.grid(row=0, column=0, sticky="nsew", padx=(0, 22))

        form = ttk.Frame(self, style="Card.TFrame", padding=36)
        form.grid(row=0, column=1, sticky="nsew")
        top = ttk.Frame(form, style="Card.TFrame")
        top.pack(fill="x")
        make_icon_badge(top, "register", size=42).pack(side="left", padx=(0, 10))
        ttk.Label(top, text="Register", style="CardTitle.TLabel").pack(side="left", anchor="w")
        ttk.Label(
            form,
            text="Enter your details below to create a new account.",
            style="CardBody.TLabel",
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(8, 20))
        self._field(form, "Username", self.username)
        self._field(form, "Password", self.password, show="*")
        self._field(form, "Confirm Password", self.confirm_password, show="*")
        ttk.Button(form, text="✚ Submit Registration", style="Primary.TButton", command=self.register).pack(fill="x", pady=(22, 10))
        ttk.Button(form, text="← Back To Login", style="Secondary.TButton", command=lambda: self.app.show_page("LoginPage")).pack(fill="x")

    def _field(self, parent, label, variable, show=None):
        ttk.Label(parent, text=label, style="FieldLabel.TLabel").pack(anchor="w", pady=(10, 6))
        ttk.Entry(parent, textvariable=variable, style="App.TEntry", show=show).pack(fill="x")

    def register(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        confirm = self.confirm_password.get().strip()
        if not username or not password or not confirm:
            messagebox.showwarning("Missing Details", "Fill all fields.")
            return
        if password != confirm:
            messagebox.showerror("Password Error", "Passwords do not match.")
            return
        try:
            success, message = register_user(username, password)
            if success:
                messagebox.showinfo("Success", message)
                self.username.set("")
                self.password.set("")
                self.confirm_password.set("")
                self.app.show_page("LoginPage")
            else:
                messagebox.showerror("Register Failed", message)
        except Exception as error:
            messagebox.showerror("Database Error", str(error))
