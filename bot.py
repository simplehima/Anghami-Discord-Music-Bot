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

@bot.command()
async def play(ctx, url):
    song_titles = get_song_titles(url)

    if not ctx.voice_client:
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        ctx.voice_client.stop()

        for title in song_titles:
            song = Song(title)
            audio_source = discord.FFmpegPCMAudio(song.info['url'], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
            audio_source = discord.PCMVolumeTransformer(audio_source)
            ctx.voice_client.play(audio_source)
            await ctx.send(f'Now playing: {song.title} ({song.duration} seconds)')

            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)

        await ctx.voice_client.disconnect()

    else:
        for title in song_titles:
            song = Song(title)
            audio_source = discord.FFmpegPCMAudio(song.info['url'], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
            audio_source = discord.PCMVolumeTransformer(audio_source)
            ctx.voice_client.play(audio_source)
            await ctx.send(f'Added to queue: {song.title} ({song.duration} seconds)')

            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped playback and cleared the queue.")
        
# Run the bot with your token
bot.run('Your Bot Token Here')
