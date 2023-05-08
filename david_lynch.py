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

import weather_report                                                                                                   # my script that handles API requests, formatting the data, and calling pill.py to create the images

import pandas as pd

###### CONSTANTS #################################################
TEXTCHANNEL = 349267380452589568
TOKEN_FILE = '.david_lynch.token'                                                                                       # Name of the text file storing the unique Discord bot token (very dangerous, do not share)
DAILY_FILE = 'daily_forecasts.csv'

# Gets the Discord bot token
def get_token(token_file):
    with open(token_file, 'r') as f:
        return f.read()

# Gets the CSV file containing the daily forecast database and returns it as a pandas dataframe
def get_daily_forecast_df() -> pd.DataFrame:
    try:
        df = pd.read_csv(DAILY_FILE, header=0, index_col=0)

    except:
        df = pd.DataFrame(columns=['userID', 'city'])
        df.set_index('userID', inplace=True)
    
    return df


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
    print(f'Good morning. It\'s {today}, and it\'s a {weekday}!')                                                       # just a print in the console to confirm the bot is running
    
    await bot.change_presence(activity=discord.Game('Golden sunshine all along the way! 🌞'))                           # custom status
    daily_msg.start()                                                                                                   # starts the daily greeting loop
    daily_forecast_task.start()                                                                                         # starts the daily forecast loop



###### TASKS #################################################
# Announces the date and tells everyone to have a great day :D
@tasks.loop(hours=24)
async def daily_msg():
    today = datetime.today().strftime('%B %#d, %Y')                                                                     # Removing the leading 0 -> Windows: %#d, Linux: %-d
    weekday = datetime.today().strftime('%A')
    msg = f'Good morning. It\'s {today}, and it\'s a {weekday}.\nEveryone: have a great day!'

    if weekday == 'Friday' or datetime.today().weekday() == 4:
        msg = f'Good morning. It\'s {today}, and if youuuuuuuuuuuuuu can believe it... *it\'s a {weekday} once again!*\nEveryone: have a great day!'

    print(msg)

    channel = bot.get_channel(TEXTCHANNEL)                                                                              # Gets the #textchatgenerals channel directly
    await channel.send(msg)                                                                                             # sends the message to the channel                                                                             

@tasks.loop(hours=24, seconds=10)
async def daily_forecast_task():
    print("Time for the daily forecast!")
    channel = bot.get_channel(TEXTCHANNEL)                                                                              # Gets the #textchatgenerals channel directly
    df = get_daily_forecast_df()                                                                                        # Gets the dataframe with users and their requested cities

    # loop over all items in the dataframe and create a weather report card for each user and their city
    for index, row in df.iterrows():
        weather_card = weather_report.weather_report(row.city)
        weather_card.seek(0)
        await channel.send(f"<@{index}> Here's the weather for **{row.city}** today, champ! 🕶️", file=discord.File(weather_card, 'weather_report.png'))


###### SLASH COMMANDS //// #################################################                                            -> https://discord-py-slash-command.readthedocs.io/en/latest/gettingstarted.html

### Getting the actual weather rn
@slash.slash(name="weather",
             description="The current weather report 😎🌞",
             guild_ids=guild_ids,
             options=[
                 create_option(
                    name="city",
                    description="🏙️ Which city to report on? 🌇",
                    option_type=3,                                                                                          # 3 = STRING
                    required=True
                ),
                 create_option(
                    name='simplified',
                    description='Full report with hourly forecasts, or classic simplified version?',
                    option_type=5,                                                                                          # 5 = BOOLEAN
                    required=False,
                )
             ])

async def weather(ctx, city, simplified=False):

    # Simplified report
    if simplified:
        weather_report.weather_simplified(city)
        await ctx.send(file=discord.File('weather_report.png'))
    
    # Full Report
    else:
        weather_card = weather_report.weather_report(city)
        weather_card.seek(0)                                                                                            # "Pillow sets the file pointer at the end when it saves. You'll have to seek back to the start of the buffer"
        await ctx.send(file=discord.File(weather_card, 'weather_report.png'))                                           # Sending an image as a bytes object from memory as "weather_report.png"



# Getting the future weather forecast
@slash.slash(name='forecast',                                                                                           # Name of the Slash command / not the function itself
            guild_ids=guild_ids,                                                                                        # For some reason, this is needed here
            description='The weather forecast report 😎🌞⛅🌧️📅',                                                     # The command's description in the discord UI
            options=[                                                                                                   # Variables shown as choices - cool! but looks like a hot mess
                create_option(
                 name="city",
                 description="🏙️ Which city to report on? 🌇",
                 option_type=3,                                                                                         # 3 = STRING
                 required=True
               ),
               create_option(
                   name="transparent",
                   description="Transparent PNG background instead of light solid background",
                   option_type=5,                                                                                       # 5 = BOOLEAN
                   required=False
               ),
               create_option(
                 name="period",
                 description="🌞 Time period to forecast. Default is tomorrow. 📅",
                 option_type=3,                                                                                         # 3 = STRING
                 required=False,                                                                                        # Not required
                 choices=[
                create_choice(                                                                                          # Tomorrow
                    name="Tomorrow",
                    value="1"
                  ),
                  create_choice(                                                                                        # Today and tomorrow and after tomorrow
                    name="3 Days",
                    value="3"
                  ),
                  create_choice(                                                                                        # Seven Days into the future
                    name="Weekly",
                    value="7"
                  )
                ]
               )
             ])

# The weather forecast
async def forecast(ctx, city, transparent = False, period = "1"):
    weather_card = weather_report.tomorrow(city, transparent)
    weather_card.seek(0)                                                                                            # "Pillow sets the file pointer at the end when it saves. You'll have to seek back to the start of the buffer"
    await ctx.send(file=discord.File(weather_card, 'weather_report.png'))                                           # Sending an image as a bytes object from memory as "weather_report.png"


# Choosing a 
@slash.slash(
        name='daily_forecast',
        guild_ids=guild_ids,
        description="🌞 Get a daily morning weather report for your chosen city! ⏰",
        options=[
            create_option(
                name="city",
                description="🏙️ Which city to report on? 🌇",
                option_type=3,                                                                                          # 3 = STRING
                required=True
            ),
            create_option(
                name="cancel",
                description="❌Cancel your daily forecast ✋",
                option_type=5,                                                                                          # 5 = BOOLEAN
                required=False
            )
        ]
)
async def daily_forecast(ctx, city:str, cancel:bool = False):
    df = get_daily_forecast_df()
    userID = ctx.author.id

    # Cancelling a user's daily forecast
    if cancel:
        # checking that the user is actually in the dataframe
        if userID not in df.index:
            await ctx.send("Can't cancel your daily forecast if you don't have one to begin with, champ! 👍")
            return
        
        # if so, delete their record
        df.drop(userID, inplace=True)
        await ctx.send("No more daily reports for you, pal! ✌️")
        df.to_csv(DAILY_FILE)
        return

    # Add/Update their record with the given city
    df.loc[userID] = city.capitalize()
    df.to_csv(DAILY_FILE)

    await ctx.send(f'Okay, I\'ll get you a weather report for **{city}** every morning! 👍')





### OLD ASCII COMMANDS

def weather_ascii(city='Los Angeles'):
    url = URL.format(city) + "?0FT"                                                                                     # wttr.in link for the requested city, getting only current info(0), no twitter follow(F), and no colours(T)
    curl = requests.get(url)                                                                                            # Curling that url
    wttr = '```' + curl.text + '```'                                                                                    # adding the discord code formatting for monospacing

    print(f'curling url: {url}')

def forecast(ctx, city = "Los Angeles", days = ""):
    url = URL.format(city) + "?FTn" + days                                                                              # wttr.in link for the requested city and amount of days to forecast, plus the other options
    curl = requests.get(url)                                                                                            # Curling that url
    
    title = curl.text.split("\n")[0]                                                                                    # Getting the weather report title
    wttr = curl.text.split("\n",8)[8]                                                                                   # Removing the current weather info
    print(wttr)
    msg = '```' + wttr + '```'

    print(f'curling url: {url}')


#Runs the bot on the specified token
if __name__ == '__main__':
    TOKEN = get_token(TOKEN_FILE)
    bot.run(TOKEN)




