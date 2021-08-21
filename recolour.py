# recolouring an image using numpy
### Re-colouring an image using PIL and NumPy
# from : https://stackoverflow.com/questions/3752476/python-pil-replace-a-single-rgba-color

from PIL import Image
import numpy as np

# re-colour SVG: https://stackoverflow.com/questions/61824128/python-change-color-in-svg-and-export-to-svg-png-pdf



def recolour(image:Image, old_colour:tuple, new_colour:tuple) -> Image:
    data = np.array(image)                                                                              # "data" is a height x width 4-dimensional numpy array
    r, g, b, a = data.T                                                                                 # temporarily unpack the colour channels for readability

    
    replace = (r == old_colour[0]) & (g == old_colour[1]) & (b == old_colour[2])                        # replace current colour with desired colour, leaving alpha values alone
    data[..., :-1][replace.T] = new_colour                                                              # replacing the values that match the current colour with the new desired colour

    image_coloured = Image.fromarray(data)                                                              # converts the numpy array back into image format

    return image_coloured




if __name__ == "__main__":
    PATH = 'icons/128/{}.png'
    NAMES = ['cloudy', 'Fog', 'HeavyShowers', 'LightRain', 'LightShowers', 'Moon']

    colour_to_replace = (250, 253, 255)
    new_colour = (254,192,22)

    for n in NAMES:
        icon = PATH.format(n)
        img = Image.open(icon)

        new_img = recolour(img, colour_to_replace, new_colour)
        new_img.show()
    
else:
    print('RECOLOUR IMPORTED')