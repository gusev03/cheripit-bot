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
from game_scores import (
    process_wordle_message,
    process_connections_message,
    process_strands_message,
)
from database import init_db, log_message, upsert_server_prompt, get_server_prompt, ActionType

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

discord_client = commands.Bot(command_prefix="!", intents=intents)
xai_client = Client(api_key=os.getenv("XAI_API_KEY"))

AUTHORIZATION_HEADER = os.getenv("AUTHORIZATION_HEADER")
UNITY_URL = os.getenv("UNITY_URL")
GIFS_FILE = "gifs.json"

DEFAULT_PROMPT = """* You are Grok, a helpful assistant
* Your goal is to be silly and very politically right wing
* Please respond concisely"""

if Path(GIFS_FILE).exists():
    try:
        with open(GIFS_FILE, "r") as f:
            gif_database = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        gif_database = {}
else:
    gif_database = {}

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
    await init_db()
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
    
    # Log the command to database
    if interaction.guild:
        await log_message(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            channel_id=interaction.channel.id,
            channel_name=interaction.channel.name,
            user_id=interaction.user.id,
            user_name=interaction.user.name,
            user_display_name=interaction.user.display_name,
            action_type=ActionType.HAMSTERDLE,
            user_message=None,
            bot_response=response,
        )

@discord_client.tree.command(name="gif", description="display a random gif, optionally from a specific category")
async def gif(interaction: discord.Interaction, category: str = None):
    gif_to_send = None
    
    if not gif_database:
        await interaction.response.send_message("No gifs available!")
        gif_to_send = "No gifs available!"
    elif not category:
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
            gif_to_send = f"No gifs for {category}!"
            await interaction.response.send_message(gif_to_send)
    
    # Log the command to database
    if interaction.guild:
        await log_message(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            channel_id=interaction.channel.id,
            channel_name=interaction.channel.name,
            user_id=interaction.user.id,
            user_name=interaction.user.name,
            user_display_name=interaction.user.display_name,
            action_type=ActionType.GIF,
            user_message=category,
            bot_response=gif_to_send,
        )

@discord_client.tree.command(
    name="set_prompt",
    description="Set a custom Grok system prompt for **this** server",
)
async def set_grok_prompt(interaction: discord.Interaction, *, prompt: str):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ This command can only be used in servers, not in DMs."
        )
        return
    
    # Save to database
    success = await upsert_server_prompt(
        guild_id=interaction.guild.id,
        guild_name=interaction.guild.name,
        user_id=interaction.user.id,
        user_name=interaction.user.name,
        user_display_name=interaction.user.display_name,
        system_prompt=prompt,
    )
    
    if success:
        embed = discord.Embed(
            title="✅ Custom Grok Prompt Saved",
            description="New prompt has been set:",
            color=0x00ff00
        )
        embed.add_field(
            name="Prompt",
            value=f"```\n{prompt}\n```",
            inline=False
        )
        embed.set_footer(text="This prompt will be used for all Grok interactions in this server.")
    else:
        embed = discord.Embed(
            title="⚠️ Prompt Saved (Database Error)",
            description="The prompt was set but there was an error saving to the database.",
            color=0xffaa00
        )
    
    await interaction.response.send_message(embed=embed)
    
    # Log the command to database
    await log_message(
        guild_id=interaction.guild.id,
        guild_name=interaction.guild.name,
        channel_id=interaction.channel.id,
        channel_name=interaction.channel.name,
        user_id=interaction.user.id,
        user_name=interaction.user.name,
        user_display_name=interaction.user.display_name,
        action_type=ActionType.SET_PROMPT,
        user_message=prompt,
        bot_response="Prompt saved" if success else "Database error",
    )

@discord_client.tree.command(
    name="show_prompt",
    description="Show the current Grok system prompt for **this** server",
)
async def show_grok_prompt(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ This command can only be used in servers, not in DMs."
        )
        return
    
    # Get prompt from database
    current_prompt = await get_server_prompt(interaction.guild.id)
    
    if current_prompt:
        embed = discord.Embed(
            title="🤖 Current Custom Grok Prompt",
            description=f"```\n{current_prompt}\n```",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="🤖 Current Grok Prompt (Default)",
            description=f"```\n{DEFAULT_PROMPT}\n```",
            color=0x808080
        )
        current_prompt = DEFAULT_PROMPT
    
    await interaction.response.send_message(embed=embed)
    
    # Log the command to database
    await log_message(
        guild_id=interaction.guild.id,
        guild_name=interaction.guild.name,
        channel_id=interaction.channel.id,
        channel_name=interaction.channel.name,
        user_id=interaction.user.id,
        user_name=interaction.user.name,
        user_display_name=interaction.user.display_name,
        action_type=ActionType.SHOW_PROMPT,
        user_message=None,
        bot_response=current_prompt,
    )

async def grok_answer(prompt: str, server_id: int | None = None) -> str:
    # Get custom prompt from database, fall back to default
    system_prompt = DEFAULT_PROMPT
    if server_id:
        custom_prompt = await get_server_prompt(server_id)
        if custom_prompt:
            system_prompt = custom_prompt

    try:
        chat = xai_client.chat.create(model="grok-4-1-fast-reasoning")
        chat.append(system(system_prompt))
        chat.append(user(prompt))
        return chat.sample().content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:  # Ignore bot's own messages
        return
    
    # Helper to log messages to the database
    async def log_to_db(action: ActionType, response: str):
        if message.guild:
            await log_message(
                guild_id=message.guild.id,
                guild_name=message.guild.name,
                channel_id=message.channel.id,
                channel_name=message.channel.name,
                user_id=message.author.id,
                user_name=message.author.name,
                user_display_name=message.author.display_name,
                action_type=action,
                user_message=message.content,
                bot_response=response,
            )
    
    if response := process_wordle_message(message.content, use_ai=True):
        await message.channel.send(response)
        await log_to_db(ActionType.WORDLE, response)
    elif response := process_connections_message(message.content):
        await message.channel.send(response)
        await log_to_db(ActionType.CONNECTIONS, response)
    elif response := process_strands_message(message.content):
        await message.channel.send(response)
        await log_to_db(ActionType.STRANDS, response)
    elif discord_client.user in message.mentions:
        # Remove the bot mention from the message content
        clean_message = message.content.replace(f"<@{discord_client.user.id}>", "").strip()
        server_id = message.guild.id if message.guild else None
        answer = await grok_answer(clean_message, server_id=server_id)
        await message.channel.send(answer)
        await log_to_db(ActionType.MENTION, answer)

discord_client.run(os.getenv("DISCORD_TOKEN"))