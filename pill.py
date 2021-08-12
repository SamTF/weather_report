from PIL import Image, ImageDraw, ImageFont     # Importing PIL to generate and manipulate  images
from text import Text, Font                     # My own script with a Text class and Enumerator of Fonts
import weather_codes                            # Lookup dictionary to convert Weather Code into the appropriate icon


### CONSTANTS for creating the image canvas and formatting other elements
CANVAS_SIZE = (1000, 1100)
BG_COLOUR   = (255, 255, 255)
MODE        = 'RGB'
ICON_POS    = (100, 200)


# saving as a binary variable instead of saving to disk
# https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
# https://stackoverflow.com/questions/27652121/get-binary-representation-of-pil-image-without-saving



def create_weather_card(city:str, temperature:str, time:str, weather_code:str):
    '''
    Creates a cool pretty weather card reporting on the current weather conditions of a specified city.
    city: The name of the city;
    temperature: The current temperature there (in Celsius);
    time: The *local* time when the weather conditions were observed;
    weather_code: Three digit code representing current weather conditions
    '''
    # CREATING CANVAS
    canvas = Image.new(MODE, CANVAS_SIZE, BG_COLOUR)

    # LOADING AND PASTING WEATHER ICON
    icon_name =  weather_codes.WWO_CODE[weather_code]
    icon_path = f'icons/{icon_name}.png'
    icon = Image.open(icon_path)
    canvas.paste(icon, ICON_POS)

    # CREATING TEXT ELEMENTS
    accent = weather_codes.ACCENT_COLOUR[icon_name]
    city = Text(city,           (100, 148), Font.BOLD_CONDENSED,    accent              )
    temp = Text(temperature,    (900, 132), Font.BOLD,              accent, anchor='rm' )
    time = Text(time,           (100, 80),  Font.CONDENSED,         accent              )
    text = [city, temp, time]

    # ADDING TEXT ELEMENTS
    draw = ImageDraw.Draw(canvas)
    for t in text:
        draw.text(t.position, t.text, t.colour, t.font.value, t.anchor)

    # EXPORTING IMAGE
    canvas.save('weather_report.png')
    # canvas.show()



# create_weather_card('Sao Pedro de Moel', '21', '04:44 PM', '116')
