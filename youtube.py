import discord
from discord.ext import commands
import yt_dlp

class Song:
    def __init__(self, url):
        self.info = yt_dlp.YoutubeDL(ytdl_options).extract_info(f'ytsearch:{url}', download=False)['entries'][0]
        self.title = self.info['title']

intents = discord.Intents.all()  
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

@bot.command()
async def play(ctx, *args):   
    song_name = ' '.join(args)
    
    voice_channel = ctx.author.voice.channel
        
    try:
        if not ctx.voice_client:
            voice_client = await voice_channel.connect()
        else:
            voice_client = ctx.voice_client

        song = Song(song_name)
        
        audio_source = discord.FFmpegPCMAudio(song.info['url'])
        voice_client.play(audio_source)
        
        # Wait for the audio source to finish playing
        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()
        await ctx.send(f'Finished playing song: {song.title}')

    except Exception as e:
        await ctx.send('Could not play song: ' + str(e))
        return

@play.error
async def play_error(ctx, error):
    await ctx.voice_client.disconnect()  
    await ctx.send('An error occurred: ' + str(error))

bot.run(os.getenv('DISCORD_TOKEN'))