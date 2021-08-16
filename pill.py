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



TEMPLATE = 'templates/hourly2.png'
ICONS_64 = 'icons/64/{}.png'
MARKER   = 'templates/marker.png'

icons_pos_y = 1069
icons_pos_x = [134, 267, 400, 533, 666, 799]

forecast_pos_y = 1183
forecast_pos_x = [164, 299, 432, 565, 698, 832]
forecast_pos_x = [x + 7 for x in forecast_pos_x]
forecast_colours = ['#A5C3C8', '#65ADC4', '#FCC017', '#E19525', '#863C3D', '#26202C']

marker_pos_y = 1051

def create_weather_card_hourly(city: str, current_temp:str, current_code:str, time:str, forecast:list, forecast_codes:list, progress=int):
    '''
    Creates a weather card with 3-hourly forecasts.

    city: Name of the city to report on the weather
    current_temp: Current temperature there in Celsius
    current_code: Weather condition WWO code right now
    time: Local time at that city
    forecast: List of hourly forecasted temperatures at [9AM, 12PM, 3PM, 6PM, 9PM, 12AM]
    forecast_codes: List of hourly forecasted conditions at [9AM, 12PM, 3PM, 6PM, 9PM, 12AM]
    progress: Amount of minutes elapsed into current day
    '''
    
    # Loading the canvas template
    canvas = Image.open(TEMPLATE)

    # Loading and pasting the weather icon
    icon_name =  weather_codes.WWO_CODE[current_code]
    icon_path = f'icons/{icon_name}.png'
    icon = Image.open(icon_path)
    canvas.paste(icon, ICON_POS)

    # Loading and pasting forecast icons
    for i, code in enumerate(forecast_codes):
        icon_name = weather_codes.WWO_CODE[code]                    # getting the image name
        icon_path = ICONS_64.format(icon_name)                      # getting the full image path

        print(icon_name, icon_path)

        icon = Image.open(icon_path)                                # opening the image
        icon = icon.convert('RGBA')                                 # converting to transparent format
        # icon = icon.resize((64, 64), Image.LANCZOS)

        position = (icons_pos_x[i], icons_pos_y)                    # getting the X position
        canvas.paste(icon, position, mask=icon)                     # pasting at desired position with alpha masking
    

    # CREATING TEXT ELEMENTS
    accent = weather_codes.ACCENT_COLOUR[weather_codes.WWO_CODE[current_code]]

    # Current Conditions
    city = Text(city,           (100, 148), Font.BOLD_CONDENSED,    accent              )
    temp = Text(current_temp,   (900, 132), Font.BOLD,              accent, anchor='rm' )
    time = Text(time,           (100, 80),  Font.CONDENSED,         accent              )
    text = [city, temp, time]

    # Forecast temps
    for i, f in enumerate(forecast):
        colour = forecast_colours[i]
        t = Text(f, (forecast_pos_x[i], forecast_pos_y), Font.BOLD_SMALL, colour, anchor='mm')
        text.append(t)


    # ADDING TEXT ELEMENTS
    draw = ImageDraw.Draw(canvas)
    for t in text:
        draw.text(t.position, t.text, t.colour, t.font.value, t.anchor)

    
    # ADDING DAY PROGRESS MARKER
    marker = Image.open(MARKER).convert('RGBA')
    canvas.paste(marker, (progress, marker_pos_y), mask=marker)


    # Saving the created image
    canvas.save('hourly.png', format='PNG', quality=100, optimize=True)
    canvas.show()




# create_weather_card('Sao Pedro de Moel', '21', '04:44 PM', '116')
# hourly_weather('LOS ANGELES', '25', '116', '11:37 AM', [26, 30, 31, 29, 27, 26], ['116', '116', '176', '176', '176', '999'])