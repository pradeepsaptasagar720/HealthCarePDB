from tkinter import ttk

from ui.components import NavigationSidebar, make_page_header, make_section_badge


class AboutPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="App.TFrame", padding=24)
        self.app = app
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.sidebar_host = ttk.Frame(self, style="App.TFrame")
        self.sidebar_host.grid(row=0, column=0, sticky="nsw", padx=(0, 20))
        self.content = ttk.Frame(self, style="App.TFrame")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)

    def refresh(self):
        for widget in self.sidebar_host.winfo_children():
            widget.destroy()
        NavigationSidebar(self.sidebar_host, self.app, "AboutPage").pack(fill="y", expand=True)
        for widget in self.content.winfo_children():
            widget.destroy()
        header = make_page_header(
            self.content,
            "About This Project",
            "This Healthcare Data Analysis System is designed to transform raw hospital data into meaningful insights for smarter decision-making. It integrates Python (Tkinter) with SQL Server to provide a centralized platform for data entry, monitoring, and real-time analytics.",
            icon_kind="about",
        )
        header.grid(row=0, column=0, sticky="ew")

        details = [
            (
                "Existing Working Flow Maintained",
                "The system preserves the original SQL Server integration, ensuring reliable data storage and consistency. All new records entered through the application are securely stored and instantly available for analysis without disrupting the existing workflow.",
            ),
            (
                "Modern & Professional User Interface",
                "The application features a structured and user-friendly interface with dedicated modules for Login, Dashboard, Data Entry, Analysis, and Reporting. Clean navigation and responsive layouts enhance usability and improve the overall user experience.",
            ),
            (
                "Real-Time Data Analysis",
                "The analysis module dynamically reads data directly from the database, ensuring up-to-date insights. Newly added patient records, diseases, and billing details are immediately reflected in charts and dashboards.",
            ),
            (
                "Key Highlights",
                "Centralized healthcare data management\nInteractive dashboards with multiple visualizations\nReal-time analytics from SQL Server\nEfficient patient and hospital record tracking\nScalable design for future enhancements",
            ),
        ]
        icon_map = ["hospital", "health", "analysis", "brand"]
        for index, (title, body) in enumerate(details, start=1):
            card = make_section_badge(self.content, title, body, icon_kind=icon_map[index - 1])
            card.grid(row=index, column=0, sticky="ew", pady=(18 if index == 1 else 8, 8))
