import requests
import pill


while True:
    city = input("Enter city name:\n>>> ")

    # Getting JSON weather data for requested city
    response = requests.get(f'https://wttr.in/{city}?format=j1')
    data = response.json()

    condition       = data['current_condition'][0]
    temperature     = condition['FeelsLikeC'] + '°'
    weather_code    = condition['weatherCode']
    local_time      = condition['localObsDateTime'][11:]
    description     = condition['weatherDesc'][0]['value']

    print(temperature)
    print(weather_code)
    print(local_time)
    print(description)

    pill.create_weather_card(city.upper(), temperature, local_time, weather_code)
    print('>>> PILL created weather report!')