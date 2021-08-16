### DAVID LYNCH WEATHER REPORT!
### Gets current weather and forecasts for any location using wttr.in

# The discord bot commands
import discord
from discord.ext import commands, tasks
# The Slash Commands module
from discord_slash import SlashCommand, SlashContext                                                                    # used to create slash commands /
from discord_slash.utils.manage_commands import create_option, create_choice                                            # used to specify the type of argument required

from datetime import datetime                                                                                           # for David Lynch's classic weather report intro
import requests                                                                                                         # python's curl command

import pill                                                                                                             # My script to create pretty weather cards c:


###### CONSTANTS #################################################
URL = 'https://wttr.in/{}'
TEXTCHANNEL = 349267380452589568


#The command prefix of all the commands
bot = commands.Bot(command_prefix='🌞 ', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)                                                                           # Initialises the @slash decorator - NEEDS THE SYNC COMMANDS to be true
guild_ids = [349267379991347200]                                                                                        # The Server ID - not sure why this is needed

print("_____________DAVID LYNCH INITIALISED_____________")


###### DISCORD STUFF //// #################################################  
# Runs this when the bot becomes online
@bot.event
async def on_ready():
    today = datetime.today().strftime('%B %#d, %Y')
    weekday = datetime.today().strftime('%A')
    print(f'Good morning. It\'s {today}, and it\'s a {weekday}!')                                                        # just a print in the console to confirm the bot is running
    
    await bot.change_presence(activity=discord.Game('Golden sunshine all along the way! 🌞'))                           # custom status
    # daily_msg.start()                                                                                                   # starts the daily greeting loop



###### TASKS #################################################
# Announces the date and tells everyone to have a great day :D
@tasks.loop(hours=24)
async def daily_msg():
    today = datetime.today().strftime('%B %#d, %Y')                                                                     # Removing the leading 0 -> Windows: %#d, Linux: %-d
    weekday = datetime.today().strftime('%A')
    msg = f'Good morning. It\'s {today}, and it\'s a {weekday}.\nEveryone: have a great day!'

    print(msg)

    channel = bot.get_channel(TEXTCHANNEL)                                                                              # Gets the #textchatgenerals channel directly
    await channel.send(msg)                                                                                             # sends the message to the channel
    


###### SLASH COMMANDS //// #################################################                                            -> https://discord-py-slash-command.readthedocs.io/en/latest/gettingstarted.html
# David Lynch's intro from his weather report videos. Gonna put this on a loop running every morning :)
@slash.slash(name="report",
             description="Weather report 😎⛅📅",
             guild_ids=guild_ids)
async def report(ctx):
    today = datetime.today().strftime('%B %#d, %Y')
    weekday = datetime.today().strftime('%A')
    msg = f'Good morning. It\'s {today}, and it\'s a {weekday}!'
    await ctx.send(content=msg)



# Getting the actual weather rn
@slash.slash(name="weather",
             description="The current weather report 😎🌞",
             guild_ids=guild_ids)

async def weather(ctx, city = "Los Angeles"):
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
    pill.create_weather_card(city.upper(), temperature, local_time, weather_code)

    await ctx.send(file=discord.File('weather_report.png'))



# Getting the future weather forecast
@slash.slash(name='forecast',                                                                                           # Name of the Slash command / not the function itself
            guild_ids=guild_ids,                                                                                        # For some reason, this is needed here
            description='The weather forecast report 😎🌞⛅🌧️📅',                                                     # The command's description in the discord UI
            options=[                                                                                                   # Variables shown as choices - cool! but looks like a hot mess
                create_option(
                 name="city",
                 description="🏙️ Which city to report on? 🌇",
                 option_type=3,                                                                                         # 3 = STRING
                 required=False                                                                                         # Not required but maybe should be
               ),
               create_option(
                 name="days",
                 description="🌞 How many days to forecast? Default is 3. 📅",
                 option_type=3,                                                                                         # 3 = STRING
                 required=False,                                                                                        # Not required
                 choices=[
                  create_choice(                                                                                        # Today
                    name="Today",
                    value="1"
                  ),
                  create_choice(                                                                                        # Today and tomorrow
                    name="2 Days",
                    value="2"
                  ),
                  create_choice(                                                                                        # Today and tomorrow and after tomorrow
                    name="3 Days",
                    value=""
                  )
                ]
               )
             ])

# The weather forecast
async def forecast(ctx, city = "Los Angeles", days = ""):
    url = URL.format(city) + "?FTn" + days                                                                              # wttr.in link for the requested city and amount of days to forecast, plus the other options
    curl = requests.get(url)                                                                                            # Curling that url
    
    title = curl.text.split("\n")[0]                                                                                    # Getting the weather report title
    wttr = curl.text.split("\n",8)[8]                                                                                   # Removing the current weather info
    print(wttr)
    msg = '```' + wttr + '```'

    print(f'curling url: {url}')

    await ctx.send(content=f"**{title}**")
    await ctx.send(content=msg)



def weather_ascii(city='Los Angeles'):
    url = URL.format(city) + "?0FT"                                                                                     # wttr.in link for the requested city, getting only current info(0), no twitter follow(F), and no colours(T)
    curl = requests.get(url)                                                                                            # Curling that url
    wttr = '```' + curl.text + '```'                                                                                    # adding the discord code formatting for monospacing

    print(f'curling url: {url}')


#Runs the bot on the specified token
bot.run("ODc0MzgyODYxMTYyMTMxNTM2.YRGKfw.A43U2lWOMVH6gtRkgVNUMRjg6aU")



