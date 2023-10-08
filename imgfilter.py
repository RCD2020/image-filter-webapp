from PIL import Image

class ImgFilter:
    def __init__(self, path):
        self.img = Image.open(path)

    