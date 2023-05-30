# Anghami Bot

Anghami Bot is a Discord bot that allows you to play songs from Anghami and create playlists in your voice channels.

## Features

- Play songs from Anghami in your Discord voice channels.
- Create playlists by providing Anghami playlist URLs.
- Supports queuing multiple songs for continuous playback.
- Easy-to-use commands to control the bot.

## Requirements

- Python 3.6+
- `discord.py` library (`pip install discord.py`)
- `yt-dlp` library (`pip install yt-dlp`)
- `pip install python-dotenv`
- ~Chrome WebDriver (or WebDriver compatible with your browser)~

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies mentioned in the "Requirements" section.
   ~3. Download the appropriate WebDriver for your browser and place it in the project directory.~
3. Place `'YOUR_BOT_TOKEN'` in the `.env` file with your actual Discord bot token.

## Usage

1. Invite the bot to your Discord server.
2. Run the bot using the following command: `python bot.py`
3. Use the following command to play songs from Anghami: `!play [Anghami playlist URL]`

## Contributing

Contributions are welcome! If you have any suggestions, improvements, or bug fixes, feel free to open an issue or submit a pull request.

## Bot Update to Version 3.0

### Changelog

1- Added Skip Command

2-Added Stop Command

3-Fixed The song not playing till the end

4-Show Now Playing Song

5- Improve discord embed message for commands

6- Added More Commands { Pause, Resume, Help }

7- Add Support for dotenv

8- Fix Playing Wrong Song [by extracting artist name]

### ToDo List

~1- Add More Commands { Pause, Resume, Help }~

~2- Fix Playing Wrong Song~

~3- Improve stability~

~4- Put it on my Could for 24/7 Online~

~5- Improve discord embed message for commands~

~6- Add .env~

7- Support for docker

8- support for slash commands

## Disclaimer

This project is for educational purposes only. The developers of this bot are not responsible for any misuse or illegal activities conducted with the bot. Please use the bot responsibly and respect the terms of service of Anghami and Discord.

## License

This project is licensed under the [MIT License](LICENSE).
