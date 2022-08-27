
import os
import sys
import json
import spotipy
import multiprocessing
import pprint as pp
from yt_dlp import YoutubeDL
from playsound import playsound
from youtube_search import YoutubeSearch

ydl_opts = {
    'format': 'mp3/bestaudio/best',
    "postprocessors": [{  # Extract audio using ffmpeg
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
    }]
}

def main():
    # instantiate secret data
    with open("./config.json") as j:
        data = json.load(j)
        CLIENT_ID = data["client_id"]
        CLIENT_SECRET = data["client_secret"]
        USERNAME = data["username"]

    # set up spotipy
    oauthObject = spotipy.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, "http://google.com/")
    token = oauthObject.get_access_token(as_dict=True)["access_token"]
    spotifyObject = spotipy.Spotify(auth=token)
    user = spotifyObject.current_user()
    playlists = spotifyObject.current_user_playlists()["items"]

    # user menu
    for i in range(len(playlists)):
        s  = str(i)
        s += " " + str(playlists[i]["name"]) 
        print(s)
    opt = int(input("Enter playlist: "))
    playlistID = playlists[opt]["id"]
    playlistItems = spotifyObject.playlist_items(playlistID)
    
    # extract the song name and artist(s)
    url = []
    for item in playlistItems["items"]:
        songName = item["track"]["name"]
        artistNames = []
        
        for artist in item["track"]["artists"]:
            artistNames.append(artist["name"])  
        
        # do a Youtube search with song name and artists
        searchParameter = str(songName) + ", " + " ".join(artistNames)
        res = YoutubeSearch(searchParameter, max_results=1).to_dict()   # assume the first result is the song we're looking for
        
        # append the url
        for r in res:
            url.append("https://youtube.com" + str(r["url_suffix"]))
        d = {"song_name": songName, "artist_names": artistNames}

    # begin downloading songs
    if (len(url) == 0):
        print("No links to download")
        sys.exit(0)

    # begin downloading songs
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    # begin playing songs, use Control-C to skip to next song
    # reference: https://stackoverflow.com/questions/57158779/how-to-stop-audio-with-playsound-module
    files = os.listdir(os.getcwd())
    for f in files:
        try:
            if (".mp3" not in str(f)):
                continue
            print("Now playing: " + str(f))
            p = multiprocessing.Process(target=playsound, args=(str(f),))
            p.start()
            while (p.is_alive()):       # while process is alive, continue blocking
                continue
        except KeyboardInterrupt:
            p.terminate()
            continue

    print("Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    main()
