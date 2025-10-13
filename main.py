import os

# Hides unnecessary informational messages from TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tkinter as tk
from fh_gui import FaceHuntInputSelection


def main():
    root = tk.Tk()
    app = FaceHuntInputSelection(root)
    root.mainloop()


if __name__ == "__main__":
    main()
