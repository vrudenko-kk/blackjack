"""Главное окно приложения Blackjack."""

import tkinter as tk
from tkinter import ttk


class App:
    """Собирает главное окно и игровое поле."""

    def __init__(self, root: tk.Tk) -> None:
        """Настроить окно и разместить игровое поле."""
        root.title("Blackjack")
        root.minsize(480, 320)

        content = ttk.Frame(root, padding=16)
        content.pack(fill="both", expand=True)

        self.table = tk.Canvas(
            content,
            width=720,
            height=400,
            background="#17543a",
            highlightthickness=0,
        )
        self.table.pack(fill="both", expand=True)
