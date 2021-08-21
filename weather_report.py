###### DESCRIPTION #################################################
### Handles the Weather API requests and calls to the pill script. Called from David Lynch to simplify the Discord Bot.


###### IMPORTS #################################################
import requests                                                                                         # python's curl command
from datetime import datetime                                                                           # getting current local time and checking for nighttime
import pill                                                                                             # My script to create pretty weather cards c:


###### CONSTANTS #################################################
URL         = 'https://wttr.in/{}'
WEATHERAPI  = 'http://api.weatherapi.com/v1/forecast.json?key=b9b5e3684034451a9b5151027211308&q={}&days=3'
night       = datetime(1, 2, 3, hour=21, minute=0).time()
dawn        = datetime(1, 2, 3, hour=6, minute=0).time()
HOURS = [9, 12, 15, 18, 21, 23]                                                                         # we only want 9AM, 12PM, 3PM, 6PM, 9PM, and 12AM



###### HELPERS #################################################
# Gets the URL to the icon from weatherapi.com and extracts only the 3 digit icon code
def get_code_from_json(forecast) -> str:
    code = forecast['condition']['icon'][-7:-4]
    return code

# Gets temperature forecast from weatherapi, rounds it to full digit and adds degree symbol
def get_temp(forecast) -> str:
    try:    temp = round(forecast['temp_c'])
    except: temp = round(forecast['feelslike_c'])

    return f'{temp}º'

# Getting the local time in datetime format
def get_time(local_time:str):
    try:
        local_datetime = datetime.strptime(local_time, '%H:%M').time()
    except:                                                                                                 # in case the localtime is something ' 1:55' with the whitespace, otherwise we get errors
        local_datetime = datetime.strptime(local_time[1:], '%H:%M').time()
    
    return local_datetime

# Translates minutes elapsed into corresponding X-Position in the daily timeline
def get_daily_progress(local_datetime:datetime) -> int:
    minutes_elapsed = local_datetime.minute + (local_datetime.hour * 60)                                    # gets the total amount of minutes elapsed this day thus far
    w = 133/3                                                                                               # each hour block is 1/3 of the square, and the square is 133px wide
    m = w/60                                                                                                # converts the hour block into minute blocks
    progress = int((m * minutes_elapsed) - 232.5)                                                           # anything before 232.5 minutes does not show up, so shift everything to the left

    return progress

# Getting forecasted temperature and condition at specified hours
def get_hourly_forecast(forecast_dict:dict):    
    temps = [get_temp(forecast_dict[x]) for x in HOURS]                                                     # getting the temperature forecast at each hour specified, rounded to full digit
    codes = [get_code_from_json(forecast_dict[x]) for x in HOURS]                                           # getting the forecast condition code
    codes[-1] = '999'                                                                                       # hardcoding the code at 12AM to be the Moon

    return temps, codes

# Taking a YYYY-MM-DD date string and formatting it as MONTH day (AUGUST 21)
def get_formatted_date(date_str:str) -> str:
    date = datetime.strptime(date_str, '%Y-%m-%d')                                                          # converting the date to datetime so that we can format it differently
    date_formatted = date.strftime('%B %d').upper()                                                         # formatting the date as AUGUST 21 (month_name day)

    return date_formatted

###


###### WEATHER FUNCTIONS #################################################

### Simplified Classic
def weather_simplified(city:str):
    '''
    Gets only the current temperature and condition, no forecasting, using data from wttr.in
    
    city: which city to get weather conditions
    '''
    url = URL.format(city) + "?format=j1"                                                                               # wttr.in link for JSON data of the requested city
    response = requests.get(url)                                                                                        # getting the data from the above link
    data = response.json()                                                                                              # converting it into a dictionary

    # Extracting the data we want
    condition       = data['current_condition'][0]
    temperature     = condition['FeelsLikeC'] + '°'
    weather_code    = condition['weatherCode']
    local_time      = condition['localObsDateTime'][11:]
    description     = condition['weatherDesc'][0]['value']

    # Creating the weather card image
    pill.create_weather_card_simplified(city.upper(), temperature, local_time, weather_code)


### 2.0 version with hourly forecasts
def weather_report(city:str):
    # Getting weather data from weatherapi.com
    response = requests.get(WEATHERAPI.format(city))
    data = response.json()

    # Reading and formatting current values from the dictionary
    current_data = data['current']
    current_temp = get_temp(current_data)
    current_code = get_code_from_json(current_data)                                                                     # current condition code
    local_time = data['location']['localtime'][-5:]                                                                     # getting the local time (without the date)

    local_datetime = get_time(local_time)                                                                               # gets the local time in datetime.time format
    
    # Checking if it's nighttime
    if local_datetime >= night or local_datetime <= dawn:                                                               # changes the condition to Moon (999) if it's night
        current_code = '999'
    
    # Getting the hourly forecast values
    forecast = data['forecast']['forecastday'][0]['hour']                                                               # all hourly forecasts are children of this element
    hours = [9, 12, 15, 18, 21, 23]                                                                                     # we only want 9AM, 12PM, 3PM, 6PM, 9PM, and 12AM
    hourly_temp = [get_temp(forecast[x]) for x in hours]                                                                # getting the temperature forecast at each hour specified, rounded to full digit
    hourly_code = [get_code_from_json(forecast[x]) for x in hours]                                                      # getting the forecast condition code
    hourly_code[-1] = '999'                                                                                             # hardcoding the code at 12AM to be the Moon

    progress = get_daily_progress(local_datetime)                                                                       # translates minutes elapsed into corresponding X-Position in the daily timeline

    # FINALLY creates the image and saves it to memory!
    weather_card = pill.create_weather_card_hourly(city.upper(), current_temp, current_code, local_time, hourly_temp, hourly_code, progress)

    return weather_card


###############################
def tomorrow(city:str):
    # Getting weather data from weatherapi.com
    response = requests.get(WEATHERAPI.format(city))
    data = response.json()

    # Reading and formatting current values from the dictionary
    forecast = data['forecast']['forecastday'][1]
    avg_temp = round(forecast['day']['avgtemp_c'])                                                          # getting the average temperature forecasted, rounded
    avg_temp = f'{avg_temp}º'                                                                               # adding the degrees symbol
    condition_code = get_code_from_json(forecast['day'])                                                    # getting the forecasted condition code
    
    # Forecast date
    date = forecast['date']                                                                                 # getting tomorrow's date string
    date_formatted = get_formatted_date(date)

    # Getting the hourly forecast values
    forecast_dict = forecast['hour']                                                                        # all hourly forecasts are children of this element
    hourly_temps, hourly_codes = get_hourly_forecast(forecast_dict)

    # Creating the weather card image
    weather_card = pill.create_tomorrow_forecast(city.upper(), avg_temp, condition_code, date_formatted, hourly_temps, hourly_codes)

    return weather_card