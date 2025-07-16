"""Crop and scale a set of images to facilitate image stacking operations."""
import os
#import sys
import shutil
#from PIL import Image, ImageOps

def main():
    """Get starting folder, copy folder, run crop function & clean folder."""
    frames_folder = "video_frames"

    del_folders('cropped')
    shutil.copytree(frames_folder, 'cropped')

    print("start cropping and scaling...")
    os.chdir('cropped')
    crop_images()
    clean_folder(prefix_to_save='cropped')

    print("Done! \n")

def del_folders(name):
    """If a folder with a named prefix exists in directory, delete it."""
    contents = os.listdir()
    for item in contents:
        if os.path.isdir(item) and item.startswith(name):
            shutil.rmtree(item)

def clean_folder(prefix_to_save):
    """Delete all files in folder except those with a named prefix."""
    files = os.listdir()
    for file in files:
        if not file.startswith(prefix_to_save):
            os.remove(file)

def crop_images():
    pass
