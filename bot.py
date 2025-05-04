import discord
import os
import random
import re
import json
import datetime
from dotenv import load_dotenv
from discord.ext import tasks
import requests
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

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

        # If leaderboard is empty, don't generate an embed or response
        if not leaderboard:
            return None, None

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

        # Calculate time until leaderboard expires (7:00 UTC)
        current_time = datetime.datetime.now(datetime.timezone.utc)
        hours_until_expiry = (7 - current_time.hour) % 24

        if hours_until_expiry == 0:
            response = "The daily hamsterdle is over! Congratulations to the winners!"
        else:
            response = f"{hours_until_expiry} hours until the daily hamsterdle ends!"

        return embed, response
    except Exception as e:
        return (
            None,
            "There is an error with the daily hamsterdle leaderboard. Golem, please fix it.",
        )


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    send_daily_message.start()


@tasks.loop(
    time=[
        datetime.time(hour=1, tzinfo=datetime.timezone.utc),  # 5 PM PT
        datetime.time(hour=7, tzinfo=datetime.timezone.utc)  # 11 PM PT
    ]
)
async def send_daily_message():
    gamer_channel = discord.utils.get(client.guilds[0].channels, name="g✱mer-safe-space")

    if gamer_channel:
        embed, response = await get_daily_hamsterdle_leaderboard()
        if embed:
            await gamer_channel.send(embed=embed)
        if response:
            await gamer_channel.send(response)

@client.tree.command(name="hamsterdle", description="display the daily hamsterdle leaderboard")
async def hamsterdle(interaction: discord.Interaction):
    embed, response = await get_daily_hamsterdle_leaderboard()
    if embed:
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(response)

@client.tree.command(name="gif", description="display a random gif, optionally from a specific category")
async def gif(interaction: discord.Interaction, category: str = None):
    if not category:
        # Get a random category and then a random gif from that category
        category = random.choice(list(gif_database.keys()))
        gif_to_send = random.choice(gif_database[category])
        await interaction.response.send_message(gif_to_send)
    else:
        # Convert category to lowercase and replace spaces with underscores
        category = category.lower().replace(' ', '_')
        
        if category in gif_database:
            gif_to_send = random.choice(gif_database[category])
            await interaction.response.send_message(gif_to_send)
        else:
            await interaction.response.send_message(f"No gifs for {category}!")

@client.event
async def on_message(message):
    if message.author == client.user:  # Ignore bot's own messages
        return

    # Wordle score check
    if wordle_scores := re.findall(
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
