from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import en_core_web_sm
import base64
import json

# Load environment variables at the top to avoid errors
load_dotenv()

#Spotify API keys
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

#Spotify API access to tokens
def get_token():
    auth_string = spotify_client_id + ":" + spotify_client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")  # Corrected encoding and decoding

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': spotify_refresh_token,
    }

    result = requests.post(url, headers=headers, data=data)

    if result.status_code == 200:
        json_result = result.json()
        if "access_token" in json_result:
            token = json_result["access_token"]
            return token
        else:
            print("The 'access_token' key is not present in the JSON response.")
    else:
        print(f"Error: {result.status_code} - {result.text}")

    return None

token = get_token()

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

#load gpt
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)

#Find name of artist in user_query
def find_artist(input_text):
    # Load the spaCy model
    nlp = en_core_web_sm.load()
    doc = nlp(input_text)

    # In spaCy, PERSON refers to names of people or fictional characters.
    # If the artist name is an entity recognised by spaCy & has the PERSON label, return the artist name
    for entity in doc.ents:
        if entity.label_ == 'PERSON':
            return entity.text
    else:
        return None

#Searches for artist information in Spotify API
def search_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }

    result = requests.get(url, headers=headers, params=params)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

#Returns a song by a specific artist from Spotify API
def get_song_by_artist(token, artist_id, country="US"):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    params = {"market": country}  
    result = requests.get(url, headers=headers, params=params)
    json_result = json.loads(result.content)
    tracks = json_result.get("tracks", [])
    return tracks

#Return the top 10 songs of the artist in a string
def format_artist_playlist(trackList):
    playlist =""
    for idx, song in enumerate (trackList):
        playlist += (f"{idx+1}. {song['name']}\n")
    return playlist



def music_response(user_query):
    #Responding to music questions
    artist = find_artist(user_query)
    artist_id = None 
    if artist:
        token = get_token()
        result = search_artist(token, artist)
        if result:
            artist_id = result["id"]
    if artist_id:  
        token = get_token()
        songs = get_song_by_artist(token, artist_id)
        artistSongs = format_artist_playlist(songs)



     
        # creating a more complete user question
        llm_query = f"""
        Instruction: You are an assistant that is complimenting music taste/artist choice, giving a fun fact about that type of music, and briefly wishing the user a good day
        Context (Music/Artist/Song details): {artist} is a great choice for today! did you know that {artist} holds this record?"
        User query: {user_query}
        Answer: 
        """
        # generating answer
        gpt3_answer = gpt_turbo.predict(llm_query)
        luna_response = f"\n\nHere is a playlist of the top songs by {artist}:\n {artistSongs}"
            
        st.text_area(label="Luna's answer: ", value=gpt3_answer + luna_response, height=350)

    else:
        st.text_area("Failed to retrieve music information.")

