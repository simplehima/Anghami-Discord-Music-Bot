import discord
from discord.ext import commands
import yt_dlp
from discord import Intents
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio

intents = Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
yt_dlp.utils.bug_reports_message = lambda: ''
queues = {}

class Song:
    def __init__(self, url):
        self.info = yt_dlp.YoutubeDL(ytdl_options).extract_info(f'ytsearch:{url}', download=False)['entries'][0]
        self.title = self.info['title']
        self.duration = self.info['duration']

def get_song_titles(url):
    # Configure the WebDriver (use the appropriate driver for your browser)
    driver = webdriver.Chrome()  # Example: using Chrome

    # Navigate to the URL
    driver.get(url)

    # Wait for the playlist content to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.container-table100'))
        )
    except TimeoutError:
        print("Timed out waiting for page to load")
        driver.quit()
        return []

    # Get the page source
    html = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML using Beautiful Soup
    soup = BeautifulSoup(html, "html.parser")

    # Find the container element with the specified class
    container = soup.find(class_='container-table100')

    # Find all <span> elements with the specified attribute within the container
    song_spans = container.find_all("span", attrs={"_ngcontent-anghami-web-v2-c202": ""})

    # Extract and filter the song titles
    song_titles = [span.text.strip() for span in song_spans if 'E' not in span.text]

    return song_titles
# Add a global variable to store the stop flag for each guild
stop_flags = {}

@bot.command()
async def play(ctx, url):
    global stop_flags
    guild_id = ctx.guild.id

    # Reset the stop flag for the guild when starting a new play command
    stop_flags[guild_id] = False

    song_titles = get_song_titles(url)
    default_img = "https://media1.giphy.com/media/FpAzqWwF3LWSTtTyg4/giphy.gif"

    if not ctx.voice_client:
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        ctx.voice_client.stop()

        for title in song_titles:
            # Check if the stop flag has been set and break the loop
            if stop_flags[guild_id]:
                break

            song = Song(title)
            audio_source = discord.FFmpegPCMAudio(song.info['url'], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
            audio_source = discord.PCMVolumeTransformer(audio_source)
            if ctx.voice_client:
                ctx.voice_client.play(audio_source)

            embed = discord.Embed(title=f"Now playing: {song.title}", color=discord.Color.blue())
            embed.set_thumbnail(url=default_img)
            embed.add_field(name="Duration", value=f"{song.duration} seconds", inline=True)
            await ctx.send(embed=embed)

            while ctx.voice_client and ctx.voice_client.is_playing():
                await asyncio.sleep(1)

        # Check if ctx.voice_client is not None before disconnecting
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    else:
        for title in song_titles:
            # Check if the stop flag has been set and break the loop
            if stop_flags[guild_id]:
                break

            song = Song(title)
            audio_source = discord.FFmpegPCMAudio(song.info['url'], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
            audio_source = discord.PCMVolumeTransformer(audio_source)
            if ctx.voice_client:
                ctx.voice_client.play(audio_source)

            embed = discord.Embed(title=f"Added to queue: {song.title}", color=discord.Color.green())
            embed.set_thumbnail(url=default_img)
            embed.add_field(name="Duration", value=f"{song.duration} seconds", inline=True)
            await ctx.send(embed=embed)

            while ctx.voice_client and ctx.voice_client.is_playing():
                await asyncio.sleep(1)

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        
        embed = discord.Embed(title="Skipped the current song.", color=discord.Color.red())
        embed.set_image(url="https://media4.giphy.com/media/nVE8OaIGkUhf7rkieR/giphy.gif?cid=ecf05e47bfmg4e4soz8txfcuqmq7h97v58n9xqakuyqnhxrk&ep=v1_gifs_search&rid=giphy.gif&ct=g")
        await ctx.send(embed=embed)

@bot.command()
async def stop(ctx):
    global stop_flags
    guild_id = ctx.guild.id

    if ctx.voice_client:
        # Set the stop flag for the guild
        stop_flags[guild_id] = True

        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        
        embed = discord.Embed(title="Stopped playback and cleared the queue.", color=discord.Color.red())
        embed.set_image(url="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjNmNmExOWUzNGFmNmI4OGE5NjYwYzczMzU4NjkxNDA1NmZiY2YzZSZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/LX8sm3UPwCpjxleARL/giphy.gif")
        await ctx.send(embed=embed)
        
# Run the bot with your token
bot.run('Your Bot Token Here')
