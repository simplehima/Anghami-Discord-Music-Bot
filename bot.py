import os
import discord
from discord.ext import commands
import yt_dlp
from discord import Intents
from bs4 import BeautifulSoup
import requests
import asyncio
from dotenv import load_dotenv


load_dotenv()
intents = Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Set the bot's presence when ready
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help for commands 🤖"))

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
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML using Beautiful Soup
    soup = BeautifulSoup(response.text, "html.parser")

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

            while ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
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

            while ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
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
        embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDE0ZjczNjE2ZjE3YjdjNDQ1YTRkMTUxYTk4MzdiYTVhNDA1NzY2NCZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/wKnceDnhLqX70U9a2V/giphy.gif")
        await ctx.send(embed=embed)


@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        embed = discord.Embed(title="Paused playback.", color=discord.Color.orange())
        embed.set_image(url="https://cdn.dribbble.com/users/2065859/screenshots/7134385/media/280bfd85736f25fca6d8447c46fb0d5e.gif")
        await ctx.send(embed=embed)


@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        embed = discord.Embed(title="Resumed playback.", color=discord.Color.green())
        embed.set_image(url="https://cdn.dribbble.com/users/2065859/screenshots/7134385/media/280bfd85736f25fca6d8447c46fb0d5e.gif")
        await ctx.send(embed=embed)


bot.remove_command('help')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
    embed.set_thumbnail(url="https://media.tenor.com/AcrJynkiNzcAAAAM/cmd-command.gif")
    embed.add_field(name="!play <url> 🎶", value="Play songs from the provided URL", inline=False)
    embed.add_field(name="!skip ⏩", value="Skip the current song", inline=False)
    embed.add_field(name="!stop ⏹️", value="Stop playback and clear the queue", inline=False)
    embed.add_field(name="!pause ⏸️", value="Pause playback", inline=False)
    embed.add_field(name="!resume ▶️", value="Resume playback", inline=False)
    embed.set_footer(text="Made by Hima")
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Oops! 😓", description="That's an invalid command. Please use !help to view all available commands.", color=discord.Color.red())
        await ctx.send(embed=embed)


# Run the bot with your token
bot.run(os.getenv('BOT_TOKEN'))
