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
    pass

def clean_folder(prefix_to_save):
    pass

def crop_images():
    pass
