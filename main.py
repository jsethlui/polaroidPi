#!/usr/bin/env python3

import sys
import json
import spotipy
import webbrowser

def main():
    with open("./config.json") as j:
        data = json.load(j)
        CLIENT_ID = data["client_id"]
        CLIENT_SECRET = data["client_secret"]
        USERNAME = data["username"]    
    
    oauthObject = spotipy.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, "http://google.com/")
    token = oauthObject.get_access_token(as_dict=True)["access_token"]
    spotifyObject = spotipy.Spotify(auth=token)

    user = spotifyObject.current_user()
    playlists = spotifyObject.current_user_playlists()["items"]
    
    print("Enter playlist: ")
    for i in range(len(playlists)):
        s  = str(i)
        s += " " + str(playlists[i]["name"]) 
        print(s)

    sys.exit(0)

if __name__ == "__main__":
    main()
