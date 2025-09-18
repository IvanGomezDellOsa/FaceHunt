import tkinter as tk
import os
from fh_gui import FaceHuntInputSelection


def main():
    root = tk.Tk()
    app = FaceHuntInputSelection(root)
    root.mainloop()


if __name__ == "__main__":
    main()
