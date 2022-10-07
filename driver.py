
import os
import sys
import json
import time
import signal
import spotipy
import multiprocessing
import pprint as pp
from yt_dlp import YoutubeDL
from playsound import playsound
from youtube_search import YoutubeSearch
from concurrent.futures import ThreadPoolExecutor

log = {}

def signalHandler(sig, frame):
    print("\nExiting...")
    sys.exit(0)
   
def downloadSongs(url, playlistName):

    def download(u):
        ydl_opts = {
            'outtmpl': "music/" + str(playlistName) + '/%(title)s-%(id)s.%(ext)s',
            'format': 'mp3/bestaudio/best',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }        
        with YoutubeDL(ydl_opts) as ydl:    
            info = ydl.extract_info(u, download=False)
            videoURL = info.get("url", "")            
            videoID = info.get("id", "")
            videoTitle = info.get('title', "")        
            if (videoID not in log.keys()):
                # download and write these files to log as json format                
                ydl.download(u)        
                d = {str(videoID): {"title": str(videoTitle),
                                     "url": str(videoURL)
                                    }
                }
                log.update(d) 

    NUM_THREADS = len(url)
    with ThreadPoolExecutor(NUM_THREADS) as executor:
        for u in url:
            executor.submit(download, u)

    global log
    with open("log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=4)  
    return log

def main():
    # register signal handler
    signal.signal(signal.SIGINT, signalHandler)

    # check if log exists
    if (not os.path.exists("./log.json")):
        print("log.json does not exist, creating...")
        f = open("log.json", "w+")
        f.close()
    path = os.getcwd() + "/music"
    if (not os.path.exists(path)):
        print("directory named 'music' does not exist, creating...")
        os.makedirs(path)
        print("'music' successfully created...")        

    # instantiate secret data
    with open("./config.json") as j:
        data = json.load(j)
        CLIENT_ID = data["client_id"]
        CLIENT_SECRET = data["client_secret"]
        USERNAME = data["username"]

    # set up spotipy
    oauthObject = spotipy.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, "http://google.com/")
    token = oauthObject.get_access_token(as_dict=False)
    spotifyObject = spotipy.Spotify(auth=token)
    user = spotifyObject.current_user()
    playlists = spotifyObject.current_user_playlists()["items"]

    # user menu
    for i in range(len(playlists)):
        s  = str(i)
        s += " " + str(playlists[i]["name"]) 
        print(s)
    # opt = int(input("Enter playlist: "))
    opt = 0
    playlistID = playlists[opt]["id"]
    playlistItems = spotifyObject.playlist_items(playlistID)
    
    # check if directory with same name as playlist exists
    playlistName = playlists[opt]["name"]
    path = os.getcwd() + "/" + str(playlistName)
    if (not os.path.exists(path)):
        print("directory named '" + str(playlistName) + "' does not exist, creating...")
        os.makedirs(path)
        print("'" + str(playlistName) + "' successfully created...")

    # extract the song name and artist(s)
    url = []
    for item in playlistItems["items"]:
        songName = item["track"]["name"]
        artistNames = []
        
        for artist in item["track"]["artists"]:
            artistNames.append(artist["name"])  
        
        # do a Youtube search with song name and artists
        searchParameter = str(songName) + ", " + " ".join(artistNames)
        res = YoutubeSearch(searchParameter, max_results=1).to_dict()   # assume the first result is the song we"re looking for
        
        # append the url
        for r in res:
            url.append("https://youtube.com" + str(r["url_suffix"]))

    # check if there any videos to download first
    if (len(url) == 0):
        print("No links to download")
        sys.exit(0)

    global log
    log = {}
    stopDownload = False
    with open("./log.json", "r", encoding="utf-8") as j:
        try:
            log = json.load(j)
        except json.decoder.JSONDecodeError:
            print("Warning: nothing to read within log.json")
            stopDownload = True

    start = time.time()
    if (stopDownload):
        downloadSongs(url, playlistName)      
    print(time.time() - start)

    # begin playing songs, use Control-C to skip to next song
    # reference: https://stackoverflow.com/questions/57158779/how-to-stop-audio-with-playsound-module
    # path = os.getcwd() + "/music"
    # print(path)

    # files = os.listdir(path)
    # for f in files:
    #     try:
    #         if (".mp3" not in str(f)):
    #             continue
    #         print("Now playing: " + str(f))
    #         p = multiprocessing.Process(target=playsound, args=(f,))
    #         p.start()
    #         while (p.is_alive()):       # while process is alive, continue blocking
    #             continue
    #     except KeyboardInterrupt:
    #         p.terminate()
    #         continue

    print("Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    main()
