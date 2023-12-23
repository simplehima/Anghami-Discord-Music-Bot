import os
import discord
from discord.ext import commands
import yt_dlp
from discord import Intents
import requests
import re
import asyncio
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

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

default_img = "https://media1.giphy.com/media/FpAzqWwF3LWSTtTyg4/giphy.gif"

def extract_song_info(url):
    response = requests.get(url)
    html_content = response.text

    pattern = r'{"@context":"http:\/\/schema.org\/","@type":"MusicRecording","name":"(.+?)","byArtist":{"@type":"MusicGroup","name":"(.+?)","@id":"(.+?)"},"inAlbum":{"@type":"MusicAlbum","name":"(.+?)","@id":"(.+?)"},'
    matches = re.findall(pattern, html_content)

    songs = []
    for match in matches:
        song_name = match[0]
        artist_name = match[1]
        album_name = match[3]
        songs.append((song_name, artist_name, album_name))

    return songs


class Song:
    def __init__(self, url):
        self.info = yt_dlp.YoutubeDL(ytdl_options).extract_info(f'ytsearch:{url}', download=False)['entries'][0]
        self.title = self.info['title']
        self.duration = self.info['duration']


@bot.command()
async def play(ctx, url):
    playlist_songs = extract_song_info(url)
    voice_channel = ctx.author.voice.channel

    if not ctx.voice_client:
        voice_client = await voice_channel.connect()
    else:
        voice_client = ctx.voice_client

    if voice_client.is_playing():
        await ctx.send("🎶 Bot is already playing audio.")
        return

    bot.stopped = False  # Flag to track if stop command was used
    bot.skip = False  # Flag to track if skip command was used
    bot.paused = False  # Flag to track if pause command was used

    current_song_count = 1  # Track the current song count

    async def play_song(song_info):
        nonlocal current_song_count  # Access the current_song_count variable from the outer scope

        if bot.stopped:
            return  # Stop playing if stop command was used

        song_name, artist_name, _ = song_info
        song = Song(f'{song_name} {artist_name}')
        audio_source = discord.FFmpegPCMAudio(song.info['url'])

        if not voice_client.is_connected():
            await voice_channel.connect()

        voice_client.play(audio_source)

        embed = discord.Embed(title="🎶 Now Playing 💓", description=f"**{song.title}** ({song.duration} seconds)", color=discord.Color.green())
        embed.set_thumbnail(url=default_img)

        if current_song_count == 1:
            embed.add_field(name="Total Songs", value=str(len(playlist_songs)), inline=False)

        message = await ctx.send(embed=embed)

        while voice_client.is_playing():
            if bot.skip:
                voice_client.stop()
                break
            if bot.paused:
                voice_client.pause()
                while bot.paused:
                    await asyncio.sleep(1)
                voice_client.resume()
            await asyncio.sleep(1)

        if bot.stopped:
            await voice_client.disconnect()
        else:
            await message.delete()

        current_song_count += 1  # Increment the current song count

    for i, song_info in enumerate(playlist_songs):
        await play_song(song_info)

        if i < len(playlist_songs) - 1 and not bot.stopped:
            await ctx.send(f"⏯️ Playing song {i+1}/{len(playlist_songs)}")  # Send the current song number and the total number of songs

        if bot.skip:
            bot.skip = False

    if not bot.stopped:
        await voice_client.disconnect()


@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        bot.stopped = True
        embed = discord.Embed(title="Stop ⏹️", description="Player stopped and disconnected.", color=discord.Color.red())
        embed.set_thumbnail(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDE0ZjczNjE2ZjE3YjdjNDQ1YTRkMTUxYTk4MzdiYTVhNDA1NzY2NCZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/wKnceDnhLqX70U9a2V/giphy.gif")
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(title="Stop ⏹️", description="⚠️ No audio is playing.", color=discord.Color.red()))


@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        bot.skip = True
        embed = discord.Embed(title="Skip ⏭️", description="Skipping the current song.", color=discord.Color.gold())
        embed.set_thumbnail(url="https://media4.giphy.com/media/nVE8OaIGkUhf7rkieR/giphy.gif?cid=ecf05e47bfmg4e4soz8txfcuqmq7h97v58n9xqakuyqnhxrk&ep=v1_gifs_search&rid=giphy.gif&ct=g")
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(title="Skip ⏭️", description="⚠️ No audio is playing.", color=discord.Color.red()))


@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        bot.paused = True
        embed = discord.Embed(title="Pause ⏸️", description="Playback paused.", color=discord.Color.blue())
        embed.set_thumbnail(url="https://cdn.dribbble.com/users/2065859/screenshots/7134385/media/280bfd85736f25fca6d8447c46fb0d5e.gif")
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(title="Pause ⏸️", description="⚠️ No audio is playing.", color=discord.Color.red()))


@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_paused():
        bot.paused = False
        embed = discord.Embed(title="Resume ▶️", description="Playback resumed.", color=discord.Color.green())
        embed.set_thumbnail(url="https://cdn.dribbble.com/users/2065859/screenshots/7134385/media/280bfd85736f25fca6d8447c46fb0d5e.gif")
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(title="Resume ▶️", description="Audio is not paused.", color=discord.Color.red()))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Oops! 😓", description="⚠️ That's an invalid command. Please use !help to view all available commands.", color=discord.Color.red())
        await ctx.send(embed=embed)

bot.remove_command('help')
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", description="List of available commands", color=discord.Color.blue())
    embed.set_thumbnail(url="https://media.tenor.com/AcrJynkiNzcAAAAM/cmd-command.gif")
    embed.add_field(name="!play <URL>", value="Plays 🎶 a song or a playlist from YouTube.", inline=False)
    embed.add_field(name="!stop", value="Stops🛑 the player and disconnects from the voice channel.", inline=False)
    embed.add_field(name="!skip", value="Skips ⏭️ the current song.", inline=False)
    embed.add_field(name="!pause", value="Pauses ⏸️ the playback.", inline=False)
    embed.add_field(name="!resume", value="Resumes ▶️ the playback.", inline=False)
    embed.add_field(name="!Help", value="Show this message.", inline=False)
    embed.set_footer(text="Bot created by Hima Azab 💕")
    await ctx.send(embed=embed)


bot.run(os.getenv('DISCORD_TOKEN'))