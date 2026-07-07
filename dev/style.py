import tkinter as tk

BG = "#07070d"
CARD = "#11131d"
CARD_SOFT = "#1f2031"
TEXT = "#f5f5f7"
MUTED = "#9da3b8"
ACCENT = "#7fc7ff"
BORDER = "#ffffff"


def style_frame(frame: tk.Frame) -> None:
    frame.configure(
        bg=CARD,
        bd=0,
        highlightbackground=BORDER,
        highlightthickness=1,
    )


def style_label(label: tk.Label, size: int = 11, bold: bool = False) -> None:
    label.configure(
        bg=CARD,
        fg=TEXT,
        font=("Inter", size, "bold" if bold else "normal"),
    )


def style_button(button: tk.Button) -> None:
    button.configure(
        bg="#1d1f2d",
        fg=TEXT,
        activebackground="#2c3048",
        activeforeground=TEXT,
        bd=0,
        highlightthickness=0,
        padx=14,
        pady=10,
        cursor="hand2",
    )
