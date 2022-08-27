
import sys
import json
import spotipy
import pprint as pp
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

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
            url.append("youtube.com" + str(r["url_suffix"]))
    print("url=" + str(url))

    # begin downloading songs
    if (len(url) == 0):
        print("No links to download")
        sys.exit(0)

    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        "postprocessors": [{  # Extract audio using ffmpeg
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)
    print("Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    main()
