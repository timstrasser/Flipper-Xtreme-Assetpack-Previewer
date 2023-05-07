from PIL import Image, ImageTk, ImageOps
import re

def create_custom_palette(fg_color, bg_color):
    palette = []
    for i in range(256):
        if i < 128:
            palette.extend(bg_color)
        else:
            palette.extend(fg_color)
    return palette


def extract_dimensions_from_filename(filename):
    match = re.search(r'(\d+)x(\d+)', filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 128, 64


def load_image(image_path):
    return Image.open(image_path)


def resize_image(image, new_width, new_height):
    return image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)


def apply_dithering(image, fg_color, bg_color):
    image_grayscale = ImageOps.grayscale(image)
    image_dithered = image_grayscale.convert('1', dither=Image.FLOYDSTEINBERG)
    image_dithered_palette = image_dithered.convert('P')
    image_dithered_palette.putpalette(create_custom_palette(fg_color, bg_color))
    return image_dithered_palette
