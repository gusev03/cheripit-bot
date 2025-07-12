import discord
import os
from pathlib import Path
import random
import re
import json
import datetime
from dotenv import load_dotenv
from discord.ext import tasks
import requests
from discord.ext import commands
from xai_sdk import Client
from xai_sdk.chat import user, system

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

discord_client = commands.Bot(command_prefix="!", intents=intents)
xai_client = Client(api_key=os.getenv("XAI_API_KEY"))

AUTHORIZATION_HEADER = os.getenv("AUTHORIZATION_HEADER")
UNITY_URL = os.getenv("UNITY_URL")
GIFS_FILE = "gifs.json"
PROMPT_FILE = "server_prompts.json"

if Path(GIFS_FILE).exists():
    try:
        with open(GIFS_FILE, "r") as f:
            gif_database = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        gif_database = {}
else:
    gif_database = {}

if Path(PROMPT_FILE).exists():
    try:
        with open(PROMPT_FILE, "r") as f:
            server_prompts: dict[str, str] = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        server_prompts = {}
else:
    server_prompts = {}

def save_prompts() -> None:
    try:
        with open(PROMPT_FILE, "w") as f:
            json.dump(server_prompts, f, indent=2)
    except (IOError, OSError) as e:
        print(f"Error saving prompts: {e}")

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

        ranks = [
            "🥇",
            "🥈",
            "🥉",
            "4th",
            "5th",
            "6th",
            "7th",
            "8th",
            "9th",
            "10th"
        ]

        # Add fields for each top player
        for rank, leader in enumerate(leaderboard[:10]):
            name = re.sub(r"#\d+", "", leader["playerName"])
            embed.add_field(
                name=ranks[rank],
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


@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user}!")
    try:
        synced = await discord_client.tree.sync()
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
    gamer_channel = discord.utils.get(discord_client.guilds[0].channels, name="g✱mer-safe-space")

    if gamer_channel:
        embed, response = await get_daily_hamsterdle_leaderboard()
        if embed:
            await gamer_channel.send(embed=embed)
        if response:
            await gamer_channel.send(response)

@discord_client.tree.command(name="hamsterdle", description="display the daily hamsterdle leaderboard")
async def hamsterdle(interaction: discord.Interaction):
    embed, response = await get_daily_hamsterdle_leaderboard()
    if embed:
        await interaction.response.send_message(embed=embed)

@discord_client.tree.command(name="gif", description="display a random gif, optionally from a specific category")
async def gif(interaction: discord.Interaction, category: str = None):

    if not gif_database:
        await interaction.response.send_message("No gifs available!")
        return

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

@discord_client.tree.command(
    name="prompt",
    description="Set a custom Grok system prompt for **this** server",
)
async def set_grok_prompt(interaction: discord.Interaction, *, prompt: str):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ This command can only be used in servers, not in DMs.", ephemeral=True
        )
        return
    
    server_prompts[str(interaction.guild.id)] = prompt
    save_prompts()  # persist to disk
    await interaction.response.send_message(
        "✅ Custom Grok prompt saved for this server.", ephemeral=True
    )

def grok_answer(prompt: str, server_id: str | None = None) -> str:
    default_prompt = """* You are Grok, a helpful assistant
* Your goal is to be silly and very politically right wing
* Please respond concisely"""

    system_prompt = server_prompts.get(server_id, default_prompt)

    try:
        chat = xai_client.chat.create(model="grok-3-mini")
        chat.append(system(system_prompt))
        chat.append(user(prompt))
        return chat.sample().content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

@discord_client.event
async def on_message(message):
    
    if message.author == discord_client.user:  # Ignore bot's own messages
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

    # Connections score check
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

    # Check if bot is mentioned
    elif discord_client.user in message.mentions:
        # Remove the bot mention from the message content
        clean_message = message.content.replace(f"<@{discord_client.user.id}>", "").strip()
        server_id = str(message.guild.id) if message.guild else None
        answer = grok_answer(clean_message, server_id=server_id)
        await message.channel.send(answer)

discord_client.run(os.getenv("DISCORD_TOKEN"))