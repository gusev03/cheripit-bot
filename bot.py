import discord
import os
import random
import re
import json
import datetime
from dotenv import load_dotenv
from discord.ext import tasks
import requests

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

AUTHORIZATION_HEADER = os.getenv("AUTHORIZATION_HEADER")
UNITY_URL = os.getenv("UNITY_URL")

# Load GIF database
with open("gifs.json", "r") as f:
    gif_database = json.load(f)


async def get_daily_hamsterdle_leaderboard() -> tuple[discord.Embed | None, str]:
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {AUTHORIZATION_HEADER}",
        }
        response = requests.get(UNITY_URL, headers=headers)
        leaderboard = response.json()["results"]

        embed = discord.Embed(
            title="🐹 Daily Hamsterdle Leaderboard", color=0x964B00  # Brown
        )

        medals = ["🥇", "🥈", "🥉"]

        # Add fields for each top player
        for rank, leader in enumerate(leaderboard[:3]):
            name = re.sub(r"#\d+", "", leader["playerName"])
            embed.add_field(
                name=medals[rank],
                value=f"**{name}**\nScore: {leader['score']}",
                inline=False,
            )

        # Add timestamp
        embed.timestamp = datetime.datetime.now()

        # Add response message
        response = ""
        if len(leaderboard) < 3:
            response += "You suckers better play the daily hamsterdle! The leaderboard is empty! "

        # Calculate time until leaderboard expires (7:00 UTC)
        current_time = datetime.datetime.now(datetime.timezone.utc)
        hours_until_expiry = (7 - current_time.hour) % 24

        if hours_until_expiry == 0:
            response += "The daily hamsterdle is over! Congratulations to the winners!"
        else:
            response += f"{hours_until_expiry} hours until the daily hamsterdle ends!"

        return embed, response
    except Exception as e:
        return (
            None,
            "There is an error with the daily hamsterdle leaderboard. Golem, please fix it.",
        )


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

    general_channel = discord.utils.get(client.guilds[0].channels, name="general")
    if general_channel:
        await general_channel.send("Guess who just got an upgrade 👀")

    send_daily_message.start()


@tasks.loop(
    time=[
        datetime.time(hour=1, tzinfo=datetime.timezone.utc),  # 5 PM PT
        datetime.time(hour=2, tzinfo=datetime.timezone.utc),  # 6 PM PT
        datetime.time(hour=3, tzinfo=datetime.timezone.utc),  # 7 PM PT
        datetime.time(hour=4, tzinfo=datetime.timezone.utc),  # 8 PM PT
        datetime.time(hour=5, tzinfo=datetime.timezone.utc),  # 9 PM PT
        datetime.time(hour=6, tzinfo=datetime.timezone.utc),  # 10 PM PT
        datetime.time(hour=7, tzinfo=datetime.timezone.utc),  # 11 PM PT
    ]
)
async def send_daily_message():
    general_channel = discord.utils.get(client.guilds[0].channels, name="general")

    if general_channel:
        embed, response = await get_daily_hamsterdle_leaderboard()
        if embed:
            await general_channel.send(embed=embed)
        if response:
            await general_channel.send(response)


@client.event
async def on_message(message):
    if message.author == client.user:  # Ignore bot's own messages
        return

    content = message.content.lower()

    # Command for daily hamsterdle leaderboard
    if content == "!hamsterdle":
        embed, response = await get_daily_hamsterdle_leaderboard()
        if embed:
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(response)  # Error message
        return

    # Check for keywords and send GIFs
    if "fortnite" in content:
        gif_to_send = random.choice(gif_database["fortnite"])
        await message.channel.send(gif_to_send)
    elif "liar" in content:
        gif_to_send = random.choice(gif_database["liars_bar"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["among us", "amongus"]):
        gif_to_send = random.choice(gif_database["among_us"])
        await message.channel.send(gif_to_send)
    elif "lethal" in content:
        gif_to_send = random.choice(gif_database["lethal"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["mine", "craft"]):
        gif_to_send = random.choice(gif_database["minecraft"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["zelda", "link", "totk", "botw"]):
        gif_to_send = random.choice(gif_database["zelda"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["joe", "biden"]):
        gif_to_send = random.choice(gif_database["biden"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["donald", "trump"]):
        gif_to_send = random.choice(gif_database["trump"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["brawl stars", "brawlstars"]):
        gif_to_send = random.choice(gif_database["brawl_stars"])
        await message.channel.send(gif_to_send)
    elif "hamster" in content:
        gif_to_send = random.choice(gif_database["hamster"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["vc", "voicechat", "voice chat"]):
        gif_to_send = random.choice(gif_database["voice_chat"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["costco", "cost co"]):
        gif_to_send = random.choice(gif_database["costco"])
        await message.channel.send(gif_to_send)
    elif any(x in content for x in ["peter", "griffin"]):
        gif_to_send = random.choice(gif_database["peter_griffin"])
        await message.channel.send(gif_to_send)

    # Wordle score check
    elif wordle_scores := re.findall(
        r"(?i)wordle\s+\d+(?:,\d+)?\s+([0-6X])(?=/6\*?)", message.content
    ):
        score = wordle_scores[0]

        if score == "X":
            await message.channel.send("You lost! ;(")
        elif score == "1":
            await message.channel.send("You totally looked up the answer!")
        elif score == "2":
            await message.channel.send("Yeeeesh what a score!")
        elif score == "3":
            await message.channel.send("Good score!")
        elif score == "4":
            await message.channel.send("Decent score!")
        elif score == "5":
            await message.channel.send("I think we can do better tomorrow!")
        elif score == "6":
            await message.channel.send("That was a close one!")
        else:
            await message.channel.send(f"Are you sure that's a valid score?")

    elif connections_scores := re.findall(
        r"connections\s*(?:puzzle\s*)?#?\d+\s*((?:(?:🟨|🟩|🟦|🟪){4}\s*){1,6})",
        message.content,
        re.IGNORECASE,
    ):
        rows = connections_scores[0].strip().split()
        is_loss = (
            len(rows) == 6 and len(set(rows[-1])) > 1
        )  # Check if last row has different colors

        if is_loss:
            await message.channel.send("You lost! Better luck tomorrow!")
        else:
            await message.channel.send("Nice job solving the Connections!")


client.run(os.getenv("DISCORD_TOKEN"))
