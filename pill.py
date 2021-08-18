from PIL import Image, ImageDraw, ImageFont     # Importing PIL to generate and manipulate  images
from text import Text, Font                     # My own script with a Text class and Enumerator of Fonts
import weather_codes                            # Lookup dictionary to convert Weather Code into the appropriate icon
from io import BytesIO                          # Used to store the output images in memory instead of saving them to disk


### CONSTANTS for creating the image canvas and formatting other elements
CANVAS_SIZE = (1000, 1100)
BG_COLOUR   = (255, 255, 255)
MODE        = 'RGB'
ICON_POS    = (100, 200)


# saving as a binary variable instead of saving to disk
# https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
# https://stackoverflow.com/questions/27652121/get-binary-representation-of-pil-image-without-saving


###### CLASSIC REPORT #################################################
def create_weather_card_simplified(city:str, temperature:str, time:str, weather_code:str):
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


###### REPORT 2.0 #################################################
### Constants
TEMPLATE        = 'templates/hourly.png'                                # path to the image template
TEMPLATE_IMG    = Image.open(TEMPLATE)                                  # opens the template and stores it in memory

MARKER          = 'templates/marker.png'                                # path to the daily progress marker
MARKER_IMG      = Image.open(MARKER).convert('RGBA')                    # opens the marker icon with alpha layer and stores it in memory
marker_pos_y = 1051                                                     # position of the progress marker in the y-axis on top of the timeline

ICONS_64 = 'icons/64/{}.png'                                            # f-string path to the small 64x64 mono icons

icons_pos_y = 1069                                                      # position of the 64px icons in the y-axis
icons_pos_x = [134, 267, 400, 533, 666, 799]                            # positions of the 64px icons in the x-axis

forecast_pos_y = 1183                                                   # position of the forecast temp text in the y-axis under the icons
forecast_pos_x = [171, 306, 439, 572, 705, 839]                         # positions of the text in the x-axis
forecast_colours = ['#A5C3C8', '#65ADC4', '#FCC017', '#E19525', '#863C3D', '#26202C']   # colours of the forecast text


def create_weather_card_hourly(city: str, current_temp:str, current_code:str, time:str, forecast:list, forecast_codes:list, progress=int):
    '''
    Creates a weather card with six tri-hourly forecasts. (from 9AM to midnight)

    city: Name of the city to report on the weather
    current_temp: Current temperature there in Celsius
    current_code: Weather condition WWO code right now
    time: Local time at that city
    forecast: List of hourly forecasted temperatures at [9AM, 12PM, 3PM, 6PM, 9PM, 12AM]
    forecast_codes: List of hourly forecasted conditions at [9AM, 12PM, 3PM, 6PM, 9PM, 12AM]
    progress: Amount of minutes elapsed into current day
    '''
    
    # Copying the template image
    canvas = TEMPLATE_IMG.copy()

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
    marker = MARKER_IMG.copy()
    canvas.paste(marker, (progress, marker_pos_y), mask=marker)


    # Saving the created image to memory in BytesIO as a "file-like object" -> https://stackoverflow.com/questions/60006794/send-image-from-memory
    weather_card = BytesIO()
    canvas.save(weather_card, format='PNG')

    return weather_card
