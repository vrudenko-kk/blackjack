"""Точка входа в приложение Blackjack."""

import tkinter as tk

from src.app import App


def main() -> None:
    """Создать окно приложения и запустить цикл событий Tkinter."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
