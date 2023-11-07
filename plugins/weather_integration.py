from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import en_core_web_sm
import geocoder

# Load environment variables at the top to avoid errors
load_dotenv()

# I was not able to get the key to work loading from the env why?
API_WEATHER_KEY = os.getenv("API_WEATHER_KEY")

#load gpt
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)

# Find name of a city in a user_query
def find_city(input_text):
    """
    This function takes a user query and returns the name of a city if it is mentioned in the query.
    Inputs:
        input_text: string
    Outputs:
        city_name: string
    """

    # Load the spaCy model
    nlp = en_core_web_sm.load()
    doc = nlp(input_text)

    # In spaCy, GPE stands for "Geopolitical Entity," which often refers to countries, cities, or states.
    # If the city name is an entity recognised by spaCy & has the GPE location prefix, return the city name
    for entity in doc.ents:
        if entity.label_ == 'GPE':
            return entity.text
    else:
        return None

# Find coordinates of a city
def find_coordinates(city_name):
    """
    This function takes a city name and returns its coordinates.
    Inputs:
        city_name: string
    Outputs:
        lat: float
        lon: float
    """

    geo_data = requests.get(
        f"https://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=10&appid={API_WEATHER_KEY}&units").json()
    return geo_data[0]["lat"], geo_data[0]["lon"]


def weather_response(user_query):
    """
    This function takes a user query and returns a weather report.
    Inputs:
        user_query: string
    Outputs:
        formatted_answer: string
    """

    city = find_city(user_query)
    if city:
        lat, lon = find_coordinates(city)
    else:
        g = geocoder.ipinfo("me")
        lat, lon = g.latlng
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_WEATHER_KEY}&units=metric")

    if response.status_code == 200:
        weather = response.json()
        if city:
            location = city
        else:
            location = weather['name']
        weather_description = weather.get("weather", [])[0].get("description")

        # creating a more complete user question
        llm_query = f"""
        Instruction: You are an assistant that is providing information or advising the user.
        Context (Weather details): in {location}, it is {weather['main']['temp']} degrees. Sky conditions: {weather_description}"
        User query: {user_query}
        Answer (limit to 2 lines):
        """

        # generating answer
        gpt3_answer = gpt_turbo.predict(llm_query)
        return gpt3_answer

    else:
        return st.text_area("Failed to retrieve weather. Status code:", response.status_code)

