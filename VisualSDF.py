
"""
Script Name: Visual SDF
Author: Hisashi Ishida
Date Created: 2023-12-22
Last Modified: 2023-12-22
Version: 1.0

Description:
    This script combines two images by overlaying SDF images onto the original segmented sliced image.
    It uses the SDF image to fill transparent or non-colored pixels of the orginal segmented image.

Usage:
    Run the script from the command line with three arguments:
    1. Path to the original segmentedimage.
    2. Path to the SDF image.
    3. Path where the combined image will be saved.

    Example:
    python3 VisualSDF.py --ori path_to_original_image.png --sdf path_to_sdf_image.png --ouitput path_to_output_image.png
"""


from PIL import Image
import click


def combine_images(original_path, overlay_path, output_path):
    # Open the images
    original = Image.open(original_path)
    overlay = Image.open(overlay_path)

    # # Resize overlay to match original image's size
    assert original.size == overlay.size, "The images must be of the same size."
    

    # Convert to RGBA if necessary
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    # New blank image with the same size
    combined = Image.new('RGBA', original.size)

    # Load pixel data
    original_data = original.load()
    overlay_data = overlay.load()
    combined_data = combined.load()

    # Iterate through each pixel
    for y in range(original.size[1]):
        for x in range(original.size[0]):
            # Get pixel data
            original_pixel = original_data[x, y]
            overlay_pixel = overlay_data[x, y]

            # Check if original pixel is transparent or non-colored
            if original_pixel[3] == 0 or original_pixel[:3] == (0, 0, 0):
                combined_data[x, y] = overlay_pixel
            else:
                combined_data[x, y] = original_pixel

    # Save the combined image
    combined.save(output_path)


@click.command()
@click.option('--ori', type=click.Path(exists=True), help='Path to the original image.', required=True)
@click.option('--sdf', type=click.Path(exists=True), help='Path to the sdf image.', required=True)
@click.option('--output', type=click.Path(), help='Path to output.', required=True)
def main(ori, sdf, output):
    """
    Combine two images. This script overlays the sdf image (specified by --sdf) onto the original image 
    (specified by --ori) wherever the original image has transparent or non-colored pixels, 
    and saves the result to the path specified by --output.
    """
    combine_images(ori, sdf, output)
    click.echo(f"Combined image saved to {output}")

if __name__ == '__main__':
    main()
