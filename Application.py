import tkinter as tk
from tkinter import ttk, messagebox

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from main import (
    DEVICES,
    get_device_problems,
    get_follow_up_questions,
    infer_follow_up_group,
)

BG = "#F5F5F3"        
CARD = "#FFFFFF"
TEXT = "#222222"
MUTED = "#6B7280"
ACCENT = "#2F6F6B"    
ACCENT_HOVER = "#255A57"
BORDER = "#DADAD6"

FONT = "Arial"


class TroubleshooterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Computer Troubleshooting Expert System")
        self.geometry("560x580")
        self.minsize(520, 540)
        self.configure(bg=BG)

        self._setup_styles()

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True, padx=36, pady=28)

        self.show_devices()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Card.TButton",
            font=(FONT, 11),
            background=CARD,
            foreground=TEXT,
            bordercolor=BORDER,
            lightcolor=CARD,
            darkcolor=CARD,
            padding=(12, 10),
            relief="flat",
        )
        style.map(
            "Card.TButton",
            background=[("active", "#EEF3F2")],
            bordercolor=[("active", ACCENT)],
        )

        style.configure(
            "Accent.TButton",
            font=(FONT, 11, "bold"),
            background=ACCENT,
            foreground="#FFFFFF",
            bordercolor=ACCENT,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            padding=(16, 10),
            relief="flat",
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT_HOVER)],
        )

        style.configure(
            "Link.TButton",
            font=(FONT, 10),
            background=BG,
            foreground=MUTED,
            bordercolor=BG,
            lightcolor=BG,
            darkcolor=BG,
            padding=(4, 4),
            relief="flat",
        )
        style.map("Link.TButton", foreground=[("active", ACCENT)],
                  background=[("active", BG)])

        style.configure(
            "TRadiobutton",
            background=CARD,
            foreground=TEXT,
            font=(FONT, 10),
        )
        style.map("TRadiobutton", background=[("active", CARD)])

    def clear(self):
        for child in self.container.winfo_children():
            child.destroy()

    def heading(self, title, subtitle=None):
        tk.Label(
            self.container, text=title, font=(FONT, 20, "bold"),
            bg=BG, fg=TEXT, anchor="w",
        ).pack(fill="x")
        if subtitle:
            tk.Label(
                self.container, text=subtitle, font=(FONT, 11),
                bg=BG, fg=MUTED, anchor="w", justify="left",
                wraplength=480,
            ).pack(fill="x", pady=(4, 0))
        tk.Frame(self.container, bg=BORDER, height=1).pack(
            fill="x", pady=(16, 16)
        )

    def show_devices(self):
        self.clear()
        self.heading(
            "Computer Troubleshooting",
            "Select the device you want to troubleshoot.",
        )

        for key, name in DEVICES.items():
            ttk.Button(
                self.container,
                text=name,
                style="Card.TButton",
                command=lambda k=key: self.show_problems(k),
            ).pack(fill="x", pady=5)

    def show_problems(self, device_key):
        problems = get_device_problems(device_key)
        device_name = DEVICES[device_key]

        if not problems:
            messagebox.showinfo(
                "No problems found",
                "No problems are listed for this device in the knowledge base.",
            )
            return

        self.clear()
        self.heading(
            device_name,
            "Choose the problem that best matches what you are experiencing.",
        )

        list_frame = tk.Frame(
            self.container, bg=CARD,
            highlightthickness=1, highlightbackground=BORDER,
        )
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        listbox = tk.Listbox(
            list_frame,
            font=(FONT, 11),
            bg=CARD,
            fg=TEXT,
            selectbackground=ACCENT,
            selectforeground="#FFFFFF",
            activestyle="none",
            highlightthickness=0,
            borderwidth=0,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        for item in problems:
            listbox.insert("end", "  " + item.get("problem", "Unknown problem"))

        def proceed(_event=None):
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning(
                    "Select a problem", "Please choose a problem first."
                )
                return
            self.show_questions(device_name, problems[selection[0]])

        listbox.bind("<Double-Button-1>", proceed)

        buttons = tk.Frame(self.container, bg=BG)
        buttons.pack(fill="x", pady=(16, 0))
        ttk.Button(
            buttons, text="← Back", style="Link.TButton",
            command=self.show_devices,
        ).pack(side="left")
        ttk.Button(
            buttons, text="Continue", style="Accent.TButton", command=proceed,
        ).pack(side="right")

    def show_questions(self, device_name, item):
        questions = get_follow_up_questions(item)

        # No follow-ups for this record: go straight to the result.
        if not questions:
            self.show_result(device_name, item, [])
            return

        self.clear()
        group = item.get("follow_up_group") or infer_follow_up_group(item)
        subtitle = item.get("problem", "")
        if group:
            subtitle += f"  ·  {group}"
        self.heading("A few quick checks", subtitle)

        card = tk.Frame(
            self.container, bg=CARD,
            highlightthickness=1, highlightbackground=BORDER,
        )
        card.pack(fill="both", expand=True)

        variables = []
        for question in questions:
            row = tk.Frame(card, bg=CARD)
            row.pack(fill="x", padx=16, pady=(12, 0))

            tk.Label(
                row, text=question, font=(FONT, 10), bg=CARD, fg=TEXT,
                anchor="w", justify="left", wraplength=440,
            ).pack(fill="x")

            var = tk.StringVar(value="")
            variables.append(var)

            choices = tk.Frame(row, bg=CARD)
            choices.pack(anchor="w", pady=(4, 0))
            ttk.Radiobutton(
                choices, text="Yes", value="yes", variable=var,
            ).pack(side="left", padx=(0, 16))
            ttk.Radiobutton(
                choices, text="No", value="no", variable=var,
            ).pack(side="left")

        def submit():
            if any(v.get() == "" for v in variables):
                messagebox.showwarning(
                    "Unanswered questions",
                    "Please answer every question (Yes or No).",
                )
                return
            answers = [
                (q, v.get() == "yes") for q, v in zip(questions, variables)
            ]
            self.show_result(device_name, item, answers)

        buttons = tk.Frame(self.container, bg=BG)
        buttons.pack(fill="x", pady=(16, 0))
        device_key = next(
            (k for k, n in DEVICES.items() if n == device_name), None
        )
        ttk.Button(
            buttons, text="← Back", style="Link.TButton",
            command=lambda: self.show_problems(device_key),
        ).pack(side="left")
        ttk.Button(
            buttons, text="See result", style="Accent.TButton", command=submit,
        ).pack(side="right")


    def show_result(self, device_name, item, answers):
        self.clear()
        self.heading("Troubleshooting Result")

        card = tk.Frame(
            self.container, bg=CARD,
            highlightthickness=1, highlightbackground=BORDER,
        )
        card.pack(fill="both", expand=True)

        fields = [
            ("Device category", device_name),
            ("Exact problem", item.get("problem", "Not available")),
            ("Possible cause", item.get("possible_cause", "Not available")),
            ("Recommended solution", item.get("solution", "Not available")),
            ("Severity", item.get("severity", "Not specified")),
        ]

        for label, value in fields:
            block = tk.Frame(card, bg=CARD)
            block.pack(fill="x", padx=18, pady=(12, 0))
            tk.Label(
                block, text=label.upper(), font=(FONT, 8, "bold"),
                bg=CARD, fg=MUTED, anchor="w",
            ).pack(fill="x")
            is_solution = label == "Recommended solution"
            tk.Label(
                block, text=value,
                font=(FONT, 13 if is_solution else 11,
                      "bold" if is_solution else "normal"),
                bg=CARD, fg=ACCENT if is_solution else TEXT,
                anchor="w", justify="left", wraplength=460,
            ).pack(fill="x", pady=(2, 0))

        if answers:
            tk.Frame(card, bg=BORDER, height=1).pack(
                fill="x", padx=18, pady=(16, 0)
            )
            tk.Label(
                card, text="YOUR ANSWERS", font=(FONT, 8, "bold"),
                bg=CARD, fg=MUTED, anchor="w",
            ).pack(fill="x", padx=18, pady=(10, 0))
            for question, answer in answers:
                tk.Label(
                    card,
                    text=f"{'Yes' if answer else 'No'}  —  {question}",
                    font=(FONT, 9), bg=CARD, fg=MUTED, anchor="w",
                    justify="left", wraplength=460,
                ).pack(fill="x", padx=18, pady=(2, 0))

        buttons = tk.Frame(self.container, bg=BG)
        buttons.pack(fill="x", pady=(16, 0))
        ttk.Button(
            buttons, text="Quit", style="Link.TButton", command=self.destroy,
        ).pack(side="left")
        ttk.Button(
            buttons, text="Start over", style="Accent.TButton",
            command=self.show_devices,
        ).pack(side="right")


if __name__ == "__main__":
    TroubleshooterApp().mainloop()