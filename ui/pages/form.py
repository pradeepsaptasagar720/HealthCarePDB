import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from db.db_connection import insert_healthcare_record
from ui.components import NavigationSidebar, ScrollableFrame, make_page_header


class FormPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="App.TFrame", padding=24)
        self.app = app
        self.entries = {}
        self.placeholders = {
            "hospital_id": "Example: 101",
            "hospital_name": "Example: Apollo Hospital",
            "hospital_city": "Example: Hyderabad",
            "doctor": "Example: Dr. Ruchita",
            "doctor_id": "Example: 5001",
            "specialist": "Example: Cardiology",
            "patient_id": "Example: 20045",
            "patient_name": "Example: Pradeep",
            "disease": "Example: Diabetes",
            "floor": "Example: 2",
            "medical_condition": "Example: Stable",
            "admitted_date": "Example: 2026-04-22",
            "room_number": "Example: 215",
            "discharge_date": "Example: 2026-04-28",
            "bill_amount": "Example: 27500",
        }
        self.field_specs = [
            ("hospital_id", "Hospital ID"),
            ("hospital_name", "Hospital Name"),
            ("hospital_city", "Hospital City"),
            ("doctor", "Doctor"),
            ("doctor_id", "Doctor ID"),
            ("specialist", "Specialist"),
            ("patient_id", "Patient ID"),
            ("patient_name", "Patient Name"),
            ("disease", "Disease"),
            ("floor", "Floor"),
            ("medical_condition", "Medical Condition"),
            ("admitted_date", "Admitted Date (YYYY-MM-DD)"),
            ("room_number", "Room Number"),
            ("discharge_date", "Discharge Date (YYYY-MM-DD)"),
            ("bill_amount", "Bill Amount"),
        ]
        self.field_widgets = []
        self.current_columns = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar_host = ttk.Frame(self, style="App.TFrame")
        self.sidebar_host.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        self.scroll = ScrollableFrame(self)
        self.scroll.grid(row=0, column=1, sticky="nsew")

        self._build_form()

    def refresh(self):
        for widget in self.sidebar_host.winfo_children():
            widget.destroy()
        NavigationSidebar(self.sidebar_host, self.app, "FormPage").pack(fill="y", expand=True)

    def _build_form(self):
        body = self.scroll.content
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        header = make_page_header(
            body,
            "Healthcare Data Entry",
            "Two-column form layout for hospital, doctor, patient, and billing details, with action buttons placed below the fields in the usual form position.",
            icon_kind="form",
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        self.fields_frame = ttk.Frame(body, style="App.TFrame")
        self.fields_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        for key, label in self.field_specs:
            wrapper = ttk.Frame(self.fields_frame, style="Card.TFrame", padding=16)
            wrapper.columnconfigure(0, weight=1)
            ttk.Label(wrapper, text=label, style="CardBody.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
            entry = ttk.Entry(wrapper, style="App.TEntry")
            entry.grid(row=1, column=0, sticky="ew")
            self.entries[key] = entry
            self._set_placeholder(entry, self.placeholders[key])
            entry.bind("<FocusIn>", lambda event, e=entry, p=self.placeholders[key]: self._clear_placeholder(event, e, p))
            entry.bind("<FocusOut>", lambda event, e=entry, p=self.placeholders[key]: self._restore_placeholder(event, e, p))
            self.field_widgets.append(wrapper)

        self.action_bar = ttk.Frame(body, style="Card.TFrame", padding=14)
        self.action_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 24))
        self.action_bar.columnconfigure(0, weight=1)
        self.action_bar.columnconfigure(1, weight=1)
        self.action_bar.columnconfigure(2, weight=1)
        ttk.Button(self.action_bar, text="✚ Submit Record", style="Primary.TButton", command=self.submit).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(self.action_bar, text="⌫ Clear Form", style="Secondary.TButton", command=self.clear_form).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(self.action_bar, text="← Back", style="Secondary.TButton", command=lambda: self.app.show_page("HomePage")).grid(row=0, column=2, sticky="ew", padx=(8, 0))

        self.scroll.canvas.bind("<Configure>", self._handle_resize, add="+")
        self.after(100, self._relayout_fields)

    def _handle_resize(self, _event=None):
        self._relayout_fields()

    def _relayout_fields(self):
        width = self.scroll.canvas.winfo_width()
        columns = 1 if width < 760 else 2
        if columns == self.current_columns:
            return
        self.current_columns = columns

        for index in range(2):
            self.fields_frame.columnconfigure(index, weight=0)
        for index in range(columns):
            self.fields_frame.columnconfigure(index, weight=1)

        for widget in self.field_widgets:
            widget.grid_forget()

        for index, widget in enumerate(self.field_widgets):
            row = index // columns
            column = index % columns
            widget.grid(row=row, column=column, sticky="ew", padx=8, pady=8)

    def clear_form(self):
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            self._set_placeholder(entry, self.placeholders[key])

    def _set_placeholder(self, entry, placeholder):
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.configure(foreground="#8fa1b6")

    def _clear_placeholder(self, _event, entry, placeholder):
        if entry.get() == placeholder and str(entry.cget("foreground")) in ("#8fa1b6", "gray", "grey"):
            entry.delete(0, tk.END)
            entry.configure(foreground="#1E293B")

    def _restore_placeholder(self, _event, entry, placeholder):
        if not entry.get().strip():
            self._set_placeholder(entry, placeholder)

    def _get_entry_value(self, key):
        entry = self.entries[key]
        value = entry.get().strip()
        if value == self.placeholders[key]:
            return ""
        return value

    def submit(self):
        try:
            record = {
                "hospital_id": int(self._get_entry_value("hospital_id")),
                "hospital_name": self._get_entry_value("hospital_name"),
                "hospital_city": self._get_entry_value("hospital_city"),
                "doctor": self._get_entry_value("doctor"),
                "doctor_id": int(self._get_entry_value("doctor_id")),
                "specialist": self._get_entry_value("specialist"),
                "patient_id": int(self._get_entry_value("patient_id")),
                "patient_name": self._get_entry_value("patient_name"),
                "disease": self._get_entry_value("disease"),
                "floor": int(self._get_entry_value("floor")),
                "medical_condition": self._get_entry_value("medical_condition"),
                "admitted_date": self._get_entry_value("admitted_date"),
                "room_number": int(self._get_entry_value("room_number")),
                "discharge_date": self._get_entry_value("discharge_date"),
                "bill_amount": float(self._get_entry_value("bill_amount")),
            }
            if any(value == "" for value in record.values() if isinstance(value, str)):
                raise ValueError("All fields are required.")
            insert_healthcare_record(record)
            messagebox.showinfo("Success", "Data inserted successfully.")
            self.clear_form()
        except Exception as error:
            messagebox.showerror("Insert Error", str(error))
