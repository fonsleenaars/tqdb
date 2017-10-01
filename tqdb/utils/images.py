import glob
import os
import subprocess

from PIL import Image
from shutil import rmtree


class SpriteCreator:
    """
    SpriteCreator class.

    Class that takes the bitmap outputs from the TQDB Parser and creates a
    single sprite image and the corresponding sprite stylesheet.

    """
    def __init__(self, sprite_dir, output_dir):
        # Image map will be used to categorize by sizes
        images_map = {}
        images = []

        # Iterate through all the files and make a list of the image objects
        for file in glob.glob(f'{sprite_dir}\\*.png'):
            image = Image.open(file)
            image.filename = os.path.basename(file).split('.')[0]
            images.append(image)

        # Iterate through all the image objects and organize them by size
        for image in images:
            width, height = image.size

            # Append this image to its size list, or create a new size list
            key = f'{width}x{height}'
            if key in images_map:
                images_map[key].append(image)
            else:
                images_map[key] = [image]

        # Keep a sorted list of the keys (descending by height):
        sorted_keys = list(images_map.keys())
        sorted_keys.sort(key=lambda x: int(x.split('x')[1]))

        # Maximum width of the sprite is 768px
        sprite_width = 768
        sprite_height = 0
        sprite_css = ('.{0} {{\n'
                      '  background-position: {1} {2};\n'
                      '  width: {3};\n'
                      '  height: {4};\n}}\n')

        # Keep track of the canvases (per size) and css (per image)
        css = []
        canvases = []

        # Run through the keys (sorted by descending height)
        for key in sorted_keys:
            canvas_width, canvas_height = tuple(map(int, key.split('x')))

            canvas = Image.new(mode='RGBA',
                               size=(sprite_width, canvas_height),
                               color=(0, 0, 0, 0))
            x = 0

            # Iterate over all the images in this size:
            for index, image in enumerate(images_map[key]):
                image_width, image_height = image.size
                if x + image_width < sprite_width:
                    canvas.paste(image, (x, 0))
                    css.append(sprite_css.format(
                        image.filename,
                        f'{0 - x}px' if 0 - x != 0 else 0 - x,
                        (f'{0 - sprite_height}px'
                         if 0 - sprite_height != 0
                         else 0 - sprite_height),
                        f'{image_width}px' if image_width != 0 else image_width,
                        (f'{image_height}px'
                         if image_height != 0
                         else image_height)))
                    x += image_width

                elif x + image_width == sprite_width:
                    canvas.paste(image, (x, 0))
                    css.append(sprite_css.format(
                        image.filename,
                        f'{0 - x}px' if 0 - x != 0 else 0 - x,
                        (f'{0 - sprite_height}px'
                         if 0 - sprite_height != 0
                         else 0 - sprite_height),
                        f'{image_width}px' if image_width != 0 else image_width,
                        (f'{image_height}px'
                         if image_height != 0
                         else image_height)))

                    if index == len(images_map[key]) - 1:
                        # Last image, append canvas:
                        canvases.append(canvas)
                        sprite_height += canvas_height
                    else:
                        # More images to come, reset row:
                        x += image_width
                else:
                    canvases.append(canvas)
                    canvas = Image.new(mode='RGBA',
                                       size=(sprite_width, canvas_height),
                                       color=(0, 0, 0, 0))
                    canvas.paste(image, (0, 0))
                    x = image_width
                    sprite_height += canvas_height

                    css.append(sprite_css.format(
                        image.filename,
                        0,
                        (f'{0 - sprite_height}px'
                         if 0 - sprite_height != 0
                         else 0 - sprite_height),
                        f'{image_width}px' if image_width != 0 else image_width,
                        (f'{image_height}px'
                         if image_height != 0
                         else image_height)))

            # Append last row
            if x < sprite_width:
                canvases.append(canvas)
                sprite_height += canvas_height

        # Create the new sprite image
        sprite_image = Image.new(mode='RGBA',
                                 size=(sprite_width, sprite_height),
                                 color=(0, 0, 0, 0))
        sprite_y = 0

        # Paste all the canvases on the sprite image
        for canvas in canvases:
            sprite_image.paste(canvas, (0, sprite_y))
            sprite_y += canvas.size[1]

        # Save the sprite
        sprite_image.save(f'{output_dir}/sprite.png', optimize=True)

        # Save the CSS
        css.sort()
        with open(f'{output_dir}/sprite.css', 'w') as css_file:
            for line in css:
                css_file.write(f'{line}\n')

        # Remove all the images
        rmtree(sprite_dir)


###############################################################################
#                              BITMAP UTILITY                                 #
###############################################################################
def save_bitmap(item, item_type, graphics, textures):
    if 'bitmap' not in item:
        return

    bitmap = item['bitmap']
    tag = item['tag']
    del(item['bitmap'])

    if item_type == 'ItemArtifactFormula':
        tag = item['classification'].lower()
    elif 'classification' in item:
        # If the file already exists, append a counter:
        if (item['classification'] != 'Rare' and
           os.path.isfile(f'{graphics}{tag}.png')):
            # Append the type:
            counter = 1
            images = glob.glob(graphics)
            for image in enumerate(images):
                if tag in images:
                    counter += 1

            tag += f'-{counter}'

    # Run the texture viewer if a bitmap and tag are set:
    if tag and os.path.isfile(f'{textures}{bitmap}'):
        command = ['utils/textureviewer/TextureViewer.exe',
                   f'{textures}{bitmap}',
                   f'{graphics}{tag}.png']
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
