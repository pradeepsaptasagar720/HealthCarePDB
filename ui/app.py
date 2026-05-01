import tkinter as tk
from tkinter import ttk
import ctypes

from ui.components import configure_styles
from ui.pages.about import AboutPage
from ui.pages.analysis import AnalysisPage
from ui.pages.form import FormPage
from ui.pages.home import HomePage
from ui.pages.login import LoginPage
from ui.pages.register import RegisterPage
from ui.pages.view_data_info import ViewDataInfoPage


# ✅ FIX BLUR (DPI Awareness)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows DPI fix
except:
    pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Better scaling
        try:
            self.tk.call("tk", "scaling", 1.3)
        except Exception:
            pass

        self.title("Healthcare System")
        self.geometry("1280x820")
        self.minsize(1120, 720)

        configure_styles(self)

        self.current_user = None
        self.frames = {}

        container = ttk.Frame(self, style="App.TFrame")
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        for page_cls in (LoginPage, RegisterPage, HomePage, FormPage, AboutPage, AnalysisPage, ViewDataInfoPage):
            frame = page_cls(container, self)
            self.frames[page_cls.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_page("LoginPage")

    def show_page(self, page_name):
        frame = self.frames[page_name]

        if hasattr(frame, "refresh"):
            frame.refresh()

        frame.tkraise()

    def open_page(self, page_name):
        if self.current_user is None and page_name not in ["LoginPage", "RegisterPage"]:
            self.show_page("LoginPage")
            return

        self.show_page(page_name)

    def login(self, user):
        self.current_user = user
        self.show_page("HomePage")

    def logout(self):
        self.current_user = None
        self.show_page("LoginPage")
