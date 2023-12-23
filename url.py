import requests
import re

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

# Example usage
url = 'https://play.anghami.com/playlist/249727778'
playlist_songs = extract_song_info(url)
for i, song_info in enumerate(playlist_songs, start=1):
    print(f"Song {i}: {song_info[0]}")
    print(f"Artist {i}: {song_info[1]}")
    print(f"Album {i}: {song_info[2]}")
    print()
