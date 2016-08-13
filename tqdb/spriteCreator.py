import glob
import os

from PIL import Image


class SpriteCreator:
    '''Class that takes the bitmap outputs from the TQDB Parser and
    creates a single sprite image and the corresponding sprite stylesheet'''

    def __init__(self, sprite_dir, output_dir):
        # Image map will be used to categorize by sizes
        images_map = {}
        images = []

        # Iterate through all the files and make a list of the image objects
        for file in glob.glob(sprite_dir + '\\*.png'):
            image = Image.open(file)
            image.filename = os.path.basename(file).split('.')[0]
            images.append(image)

        # Iterate through all the image objects and organize them by size
        for image in images:
            width, height = image.size

            # Append this image to its size list, or create a new size list
            key = '{0}x{1}'.format(width, height)
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
        sprite_css = ('.{0} {{ background-position: {1}px {2}px; '
                      ' width: {3}px; height: {4}px; }}')

        # Keep track of the canvases (per size) and css (per image)
        css = []
        canvases = []

        # Run through the keys (sorted by descending height)
        for key in sorted_keys:
            canvas_width, canvas_height = tuple(map(int, key.split('x')))

            canvas = Image.new(mode='RGBA', size=(sprite_width, canvas_height),
                               color=(0, 0, 0, 0))
            x = 0

            # Iterate over all the images in this size:
            for image in images_map[key]:
                image_width, image_height = image.size
                if x + image_width <= sprite_width:
                    canvas.paste(image, (x, 0))
                    css.append(sprite_css.format(image.filename, 0 - x,
                               0 - sprite_height, image_width, image_height))
                    x += image_width

                else:
                    canvases.append(canvas)
                    canvas = Image.new(mode='RGBA', size=(sprite_width,
                                       canvas_height), color=(0, 0, 0, 0))
                    canvas.paste(image, (0, 0))
                    x = image_width
                    sprite_height += canvas_height
                    css.append(sprite_css.format(image.filename, 0,
                               0 - sprite_height, image_width, image_height))

            # Append last row
            if x < sprite_width:
                canvases.append(canvas)
                sprite_height += canvas_height

        # Create the new sprite image
        sprite_image = Image.new(mode='RGBA', size=(sprite_width,
                                 sprite_height), color=(0, 0, 0, 0))
        sprite_y = 0

        # Paste all the canvases on the sprite image
        for canvas in canvases:
            sprite_image.paste(canvas, (0, sprite_y))
            sprite_y += canvas.size[1]

        # Save the sprite
        sprite_image.save(output_dir + '/sprite.png', optimize=True)

        # Save the CSS
        css.sort()
        with open(output_dir + '/sprite.css', 'w') as css_file:
            for line in css:
                css_file.write("{0}\n".format(line))
