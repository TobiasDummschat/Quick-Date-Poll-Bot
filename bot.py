from babel.dates import format_datetime
from datetime import datetime as dt
import dateutil.parser
import discord
from emoji import emojize
import locale
import re
from sys import argv



# start: /datepoll
# end: /datepoll or end of input_str
# input_str: list of iso 8601 formats separated by whitespace or commas

try:
    with open("token.txt") as file:
        TOKEN = file.read()
except FileNotFoundError:
    print("FileNotFoundError: Store your bot's access token in token.txt")

activity = discord.Activity(type=discord.ActivityType.listening, name="/datepoll help")
client = discord.Client(activity=activity)
formats = dict()
locales = dict()


def to_date(date_str):
   return dateutil.parser.parse(date_str)


def input_to_date_list(input_str):
    dates = []
    command = "/datepoll"
    separators = "\s|,"
    
    start_command_pos = input_str.find(command)
    if start_command_pos != -1:
        list_start = start_command_pos + len(command)
        input_str = input_str[list_start:]
        end_command_pos = input_str.find(command)
        if end_command_pos != -1:
            input_str = input_str[:end_command_pos]
    
        date_str_list = re.split(separators, input_str)
        date_str_list = [s for s in date_str_list if s != ""]

        for date in date_str_list:
            dates.append(dateutil.parser.parse(date))

    return dates


def get_indicators(num):
    out = []
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    letters = ["regional_indicator_" + letter for letter in alphabet]
    numbers_without_zero = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "keycap_ten"]
    numbers_with_zero = ["zero"] + numbers_without_zero
    if num < 11:
        out = numbers_without_zero
    elif num == 11:
        out = numbers_with_zero
    elif num <= 26:
        out = letters
    elif num <= 36:
        out = numbers_without_zero + letters
    elif num <= 37:
        out = numbers_with_zero + letters
    return [emojize(":" + emoji_str + ":", use_aliases=True) for emoji_str in out]

def formatted_dates_to_out(formatted_dates):
    num = len(formatted_dates)
    if 0 == num:
        return "Error: No date entered.", -1
    if num > 37:
        return "Error: Too many dates entered. Maximum is 37", -1

    lines = []
    indicators = get_indicators(num)
    for i in range(num):
        lines.append(indicators[i] + " " + formatted_dates[i])
    lines.append(emojize(":no_entry_sign:") + " None of the above")
    return "\n".join(lines), num


def process(message):
    input_str = message.content
    dates = input_to_date_list(input_str)
    formatted_dates = [format_datetime(date, format=formats[message.guild.id], locale=locales[message.guild.id]) for date in dates]
    return formatted_dates_to_out(formatted_dates)




@client.event
async def on_message(message):
    if not message.guild.id in formats.keys():
        format_str = "cccc, yyyy-mm-dd"
        formats[message.guild.id] = format_str

    if not message.guild.id in locales.keys():
        locale_str = message.guild.preferred_locale
        locales[message.guild.id] = locale_str.replace("-","_")

    if message.author == client.user:
        return

    if message.content == "/datepoll help":
        await message.add_reaction(emojize(":partying_face:"))
        msg = '''You can use me to set up quick date polls.

I listen to messages containing "/datepoll" followed by a list of ISO 8601 dates separated by whitespace or commas. The list must be at least 1 and at most 37 dates long. The ISO 8601 format includes the YYYY-MM-DD format and many simplifications of it like MM-DD.

You can set the format of the returned dates by using "/datepoll format FORMAT" where FORMAT is a format using the Unicode Date Format Patterns, which can be found here:
https://www.unicode.org/reports/tr35/tr35-dates.html#Date_Format_Patterns

    You can set the locale of the returned dates by using "/datepoll locale LOCALE where LOCALE is a locale such as en_US or de_DE using the ISO language and country codes.'''
        await message.channel.send(msg)
        return

    format_command = "/datepoll format"
    if message.content.startswith(format_command):
        format_str = message.content[len(format_command)+1:]
        formats[message.guild.id] = format_str

    locale_command = "/datepoll locale"
    if message.content.startswith(locale_command):
        locale_str = message.content[len(locale_command)+1:]
        locales[message.guild.id] = locale_str

    msg, num = process(message)
    response = await message.channel.send(msg)

    if num != -1:
        indicators = get_indicators(num)
        for emoji in indicators[:num]:
            await response.add_reaction(emoji)
        await response.add_reaction(emojize(":no_entry_sign:", use_aliases=True))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)