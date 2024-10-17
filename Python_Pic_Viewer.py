import sys

from tkinterdnd2 import TkinterDnD

from image_viewer.ImageViewer import ImageViewer

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    viewer = ImageViewer(root)
    arguments = sys.argv[1:]
    if len(arguments) > 0 :
        viewer.open_single_file(arguments[0])
    root.mainloop()
