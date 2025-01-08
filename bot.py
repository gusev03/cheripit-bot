import discord
import os
import random
import re
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Load GIF database
with open('gifs.json', 'r') as f:
    gif_database = json.load(f)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

@client.event
async def on_message(message):
    
    if message.author == client.user:  # Ignore bot's own messages
        return
    
    content = message.content.lower()

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
    elif scores := re.findall(r"(?i)wordle\s+\d+(?:,\d+)?\s+([0-6X])(?=/6\*?)", message.content):
        
        score = scores[0]

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

client.run(os.getenv("DISCORD_TOKEN"))