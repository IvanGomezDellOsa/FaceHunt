import deepface
import yt_dlp
import cv2
import numpy
import tkinter as tk
import re
import os
from fh_gui import FaceHuntInputSelection

# pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'

def main():
    root = tk.Tk()
    app = FaceHuntInputSelection(root)
    root.mainloop()

if __name__ == "__main__":
    main()


