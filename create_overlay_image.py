
"""
Script Name: Visual SDF
Author: Hisashi Ishida
Date Created: 2023-12-24
Last Modified: 2023-12-24
Version: 1.0

Description:
    This script processes a set of images from four specified folders. 
    It applies a color overlay to the original images based on the red channel values 
    from corresponding VF, bone1, and bone2 images. The user can specify the paths 
    to the folders containing the original, VF, bone1, and bone2 images, 
    as well as an output folder for the processed images. 
    Additionally, a space resolution value can be provided for further image processing.

Usage:
 python create_overlay_image.py --original path/to/original --vf path/to/vf 
    --bone1 path/to/bone1 --bone2 path/to/bone2 --output path/to/output 
    --spaceresolution <value>
"""


import click
from PIL import Image
import os
import re

# Thresholds
red_thres = 2.0
yellow_thres = 4.0

#Colors to ignore in the overlay process
L1_bone_color = (242, 215, 145)  # L1 minus drilling
L2_bone_color = (241, 215, 144)  # L2 minus drilling
L3_bone_color = (240, 215, 145)  # L3 minus drilling
L4_bone_color = (242, 213, 146)  # L4 minus drilling
vf_color = (245, 233, 253)  # Vetebral Forman

# Function to check if the pixel is 'colored'
def is_colored(pixel):
    return any(value > 0.0 for value in pixel)

def is_boneORVF(pixel):
    return pixel in [L1_bone_color, L2_bone_color, L3_bone_color, L4_bone_color, vf_color]

# Function to apply overlay
def apply_overlay(original, vf, bone1, bone2, spaceres):
    for x in range(original.width):
        for y in range(original.height):
            pixel_original = original.getpixel((x, y))

            # if there is no color
            if not is_colored(pixel_original):
                continue
            
            # If the pixel is bone or VF
            if is_boneORVF(pixel_original):
                continue

            dist_vf    = (vf.getpixel((x, y))[0]/255.0 - vf.getpixel((x, y))[1]/255.0) * 600.0 * spaceres
            dist_bone1 = (bone1.getpixel((x, y))[0]/255.0 - bone1.getpixel((x, y))[1]/255.0) * 600.0 * spaceres
            dist_bone2 = (bone2.getpixel((x, y))[0]/255.0 - bone2.getpixel((x, y))[1]/255.0) * 600.0 * spaceres

            # Determine color based on the condition            
            if dist_vf < 0.1 or dist_bone1 < 0.1 or dist_bone2 < 0.1:
                color = (139, 0, 0)  # Dark Red
            elif dist_vf < red_thres or dist_bone1 < red_thres or dist_bone2 < red_thres:
                color = (255, 0, 0)  # Red
            elif dist_vf < yellow_thres or dist_bone1 < yellow_thres or dist_bone2 < yellow_thres:
                color = (255, 255, 0)  # Yellow
            else:
                color = (0, 128, 0)  # Green

            original.putpixel((x, y), color)

    return original

@click.command()
@click.option('--original', 'original_folder', type=click.Path(exists=True), help='Path to original images folder', required=True)
@click.option('--vf', 'vf_folder', type=click.Path(exists=True), help='Path to VF sdfimages folder', required=True)
@click.option('--bone1', 'bone1_folder', type=click.Path(exists=True), help='Path to first bone sdf images folder', required=True)
@click.option('--bone2', 'bone2_folder', type=click.Path(exists=True), help='Path to second bone sdfimages folder', required=True)
@click.option('--output', 'output_folder', type=click.Path(), help='Path to output folder where processed images will be saved', required=True)
@click.option('--sr', 'spaceresolution', type=float, help='Space resolution value', required=True)

def main(original_folder, vf_folder, bone1_folder, bone2_folder, output_folder, spaceresolution):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process images
    for filename in os.listdir(original_folder):
        if filename.endswith(".png") and filename.startswith("plane00"):
            number = re.search(r'plane00(\d+)', filename).group(1)
            original_path = os.path.join(original_folder, filename)
            vf_path = os.path.join(vf_folder, f'edtplane_{number}.png')
            bone1_path = os.path.join(bone1_folder, f'edtplane_{number}.png')
            bone2_path = os.path.join(bone2_folder, f'edtplane_{number}.png')

            if all(os.path.exists(path) for path in [vf_path, bone1_path, bone2_path]):
                original = Image.open(original_path).convert('RGB')
                vf = Image.open(vf_path).convert('RGB')
                bone1 = Image.open(bone1_path).convert('RGB')
                bone2 = Image.open(bone2_path).convert('RGB')

                # Apply overlay to original image
                result_image = apply_overlay(original, vf, bone1, bone2, spaceresolution)
                result_image.save(os.path.join(output_folder, f'overlayed_image_{number}.png'))

    print("Image processing complete.")

if __name__ == '__main__':
    main()
