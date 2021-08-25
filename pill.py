from typing import ClassVar
from PIL import Image, ImageDraw, ImageFont     # Importing PIL to generate and manipulate  images
from text import Text, Font                     # My own script with a Text class and Enumerator of Fonts
import weather_codes                            # Lookup dictionary to convert Weather Code into the appropriate icon
from io import BytesIO                          # Used to store the output images in memory instead of saving them to disk
import recolour                                 # My script to recolour imagines using PIL and NumPy to a new solid colour
from PIL import ImageColor                      # To convert #Hex colour to R,G,B


### CONSTANTS for creating the image canvas and formatting other elements
CANVAS_SIZE = (1000, 1100)
BG_COLOUR   = (255, 255, 255)
MODE        = 'RGB'
ICON_POS    = (100, 200)


###### HELPERS #################################################
# Loading and pasting forecast icons
def paste_forecast_icons(canvas:Image, forecast_codes:list, y_pos:int, coloured_icons=False):
    '''
    Pasting the right hourly condition icons in the right spot.

    canvas: The Image object where the weather card is being drawn
    forecast_codes: List of WWO weather condition codes
    y-pos: Position in the Y-axis for the condition icons
    coloured_icons: If True, colours each icon according to the timeline colours
    '''
    for i, code in enumerate(forecast_codes):
        icon_name = weather_codes.WWO_CODE[code]                    # getting the image name
        icon_path = ICONS_64.format(icon_name)                      # getting the full image path

        icon = Image.open(icon_path)                                # opening the image
        icon = icon.convert('RGBA')                                 # converting to transparent format
        # icon = icon.resize((64, 64), Image.LANCZOS)

        if coloured_icons:                                           # recolouring the icon if a colour has been specified (for dark mode)
            colour = DARK_FRCST_COLOURS[i]
            icon = recolour.recolour(icon, ICON_COLOUR_64, colour)


        position = (icons_pos_x[i], y_pos)                          # getting the icon position
        canvas.paste(icon, position, mask=icon)                     # pasting at desired position with alpha masking

    return canvas

# Creating Text elements
def create_text_elements(city:str, temp:str, datetime:str, forecast_temps:list, accent:str, y_pos:int, colours:list, colour_headings=True):
    '''
    Creating all the Text elements to display on the weather card.

    city: Name of the city in uppercase
    temp: The temperature to highlight in big numbers (current or average forcast)
    datetime: Subtitle above city name (either current local time or forecast's local date)
    forecast_temps: List of hourly forecast temperatures
    accent: Colour to accent the main text (in #Hex code)
    y_pos: Position in the Y-axis for the forecast temperature text
    colours: List of HEX code colours to use for colouring the forecast text
    colour_headings: Whether the city name and date should be accented coloured
    '''

    # Main Text
    city = Text(city,           (100, 148), Font.BOLD_CONDENSED,    accent if colour_headings else DARK_TXT_COLOUR  )
    datetime = Text(datetime,   (100, 80),  Font.CONDENSED,         accent if colour_headings else DARK_TXT_COLOUR  )
    temp = Text(temp,           (900, 132), Font.BOLD,              accent,                             anchor='rm' )
    text_elements = [city, temp, datetime]

    # Forecast temps
    for i, f in enumerate(forecast_temps):
        colour = colours[i]
        t = Text(f, (forecast_pos_x[i], y_pos), Font.BOLD_SMALL, colour, anchor='mm')
        text_elements.append(t)
    
    return text_elements

# Drawing Text elements
def draw_text_elements(canvas:Image, text_elements:list):
    '''
    Drawing the Text elements on the cavas.

    canvas: The Image object where the weather card is being drawn
    text_elements: List of Text objects
    '''
    draw = ImageDraw.Draw(canvas)
    for t in text_elements:
        draw.text(t.position, t.text, t.colour, t.font.value, t.anchor)
    
    return canvas

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
    canvas = paste_forecast_icons(canvas, forecast_codes, icons_pos_y)
    
    # Getting accent colour
    accent = weather_codes.ACCENT_COLOUR[weather_codes.WWO_CODE[current_code]]

    # Creating Text elements
    text = create_text_elements(city, current_temp, time, forecast, accent, forecast_pos_y, forecast_colours)

    # Adding Text elements to canvas
    canvas = draw_text_elements(canvas, text)
    
    # Adding day progress marker
    marker = MARKER_IMG.copy()
    canvas.paste(marker, (progress, marker_pos_y), mask=marker)

    # Saving the created image to memory in BytesIO as a "file-like object" -> https://stackoverflow.com/questions/60006794/send-image-from-memory
    weather_card = BytesIO()
    canvas.save(weather_card, format='PNG')

    return weather_card



###### TOMORROW'S FORECAST #################################################
### Constants
ICON_COLOUR     = (248,252,254)                                         # the shade of white used by all 128x128 the mono icons
ICON_COLOUR_64  = (250, 253, 255)                                       # the shade of white used by all 64x64 the mono icons (they're accidentally different but it's too annoying to fix that)

tomorrow_text_pos_y = 375                                               # position of the forecast temp text in the y-axis under the icons
tomorrow_icons_pos_y = 264                                              # y-position of the condition icons on the timeline
tomorrow_condition_pos = (540, 50)                                      # position of the average condition icon

### Light Mode Constants
FORECAST        = 'templates/forecast_light.png'                        # path to the image template
FORECAST_IMG    = Image.open(FORECAST)                                  # opens the template and stores it in memory

### Dark Mode Constants
DARK_FORECAST       = 'templates/forecast_trans.png'                                        # path to the image template
DARK_FORECAST_IMG   = Image.open(DARK_FORECAST).convert('RGBA')                             # opens the template and stores it in memory
DARK_TXT_COLOUR     = "#DFDEDC"                                                             # font colour for city name and date
dark_colours_hex    = ['#A5C3C8', '#65ADC4', '#FCC017', '#E19525', '#863C3D', '#AC97BE']    # icon colours
DARK_FRCST_COLOURS  = [ImageColor.getcolor(x, 'RGB') for x in dark_colours_hex]             # colours converted to RGB

### Dictionary of function arguments for each mode
LIGHT_MODE_VARS = {
    "canvas": FORECAST_IMG,
    "coloured_icons": False,
    "colours": forecast_colours,
    "colour_headings": True
}

DARK_MODE_VARS = {
    "canvas": DARK_FORECAST_IMG,
    "coloured_icons": True,
    "colours": dark_colours_hex,
    "colour_headings": False
}

def create_tomorrow_forecast(city:str, avg_temp:str, condition_code:str, date:str, forecast:list, forecast_codes:list, transparent=False):
    '''
    Creates a weather card for tomorrow's conditions with six tri-hourly forecasts. (from 9AM to midnight)

    city: Name of the city to report on the weather
    avg_temp: Average forecasted temperature in Celsius
    condition_code: Weather condition WWO code for overall forecasted condition
    date: Local date of next day as "MONTH day"
    forecast: List of hourly forecasted temperatures at [9AM, 12PM, 3PM, 6PM, 9PM, 12AM]
    forecast_codes: List of hourly forecasted conditions at [9AM, 12PM, 3PM, 6PM, 9PM, 12AM]
    transparent: If the background should be transparent (dark mode). Otherwise light mode.
    '''
    # Getting all the default values of the correct mode at once instead of having a ton of ifs
    VARS = LIGHT_MODE_VARS if not transparent else DARK_MODE_VARS

    # Copying the template image
    canvas = VARS['canvas'].copy()

    # Getting accent colour
    accent = weather_codes.ACCENT_COLOUR[weather_codes.WWO_CODE[condition_code]]
    accent_rgb = ImageColor.getcolor(accent, 'RGB') # converting it to RGB for the recolour script

    # Loading and pasting the weather icon
    icon_name =  weather_codes.WWO_CODE[condition_code]
    icon_path = f'icons/128/{icon_name}.png'
    icon = Image.open(icon_path)

    # Colouring the icon to fit its accent colour
    coloured_icon = recolour.recolour(icon, ICON_COLOUR, accent_rgb)
    canvas.paste(coloured_icon, tomorrow_condition_pos, mask=coloured_icon)

    # Loading and pasting forecast icons
    canvas = paste_forecast_icons(canvas, forecast_codes, tomorrow_icons_pos_y, coloured_icons=VARS['coloured_icons'])

    # CREATING TEXT ELEMENTS
    text = create_text_elements(city, avg_temp, date, forecast, accent, tomorrow_text_pos_y, colours=VARS['colours'], colour_headings=VARS['colour_headings'])

    # ADDING TEXT ELEMENTS TO CANVAS
    canvas = draw_text_elements(canvas, text)

    # Saving the created image to memory in BytesIO as a "file-like object" -> https://stackoverflow.com/questions/60006794/send-image-from-memory
    weather_card = BytesIO()
    canvas.save(weather_card, format='PNG')

    return weather_card
