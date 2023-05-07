import os
import re


def load_image_files(folder_path):
    return sorted([f for f in os.listdir(folder_path) if f.startswith("frame_") and f.endswith(".png")], key=natural_sort_key)


def get_folder_list(anims_path):
    return sorted([folder for folder in os.listdir(anims_path) if os.path.isdir(os.path.join(anims_path, folder))], key=natural_sort_key)


def get_icon_structure(root_path):
    icon_structure = {}
    for folder in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder)
        if os.path.isdir(folder_path):
            icon_structure[folder] = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")], key=natural_sort_key)

    return icon_structure

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]