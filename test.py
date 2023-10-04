from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import en_core_web_sm
import geocoder


# I was not able to get the key to work loading from the env why?
API_WEATHER_KEY = os.getenv("API_WEATHER_KEY")


# Find name of a city in a prompt
def find_city(input_text):
    # Load the spaCy model
    nlp = en_core_web_sm.load()
    doc = nlp(input_text)

    # if the city name is in the data_base & has the location prefix return the city name:
    for entity in doc.ents:
        if entity.label_ == 'GPE':
            return entity.text
    else:
        return None


# Find coordinates of a city
def find_coordinates(city_name):
    geo_data = requests.get(
        f"https://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=10&appid={API_WEATHER_KEY}&units").json()
    return geo_data[0]["lat"], geo_data[0]["lon"]


# Main function
def run_luna():
    # Load environment variables (if needed)
    load_dotenv()

    st.title('🌚 Welcome to Luna')

    # creating a text box
    with st.form('my_form'):
        # waiting for user input
        prompt = st.text_area('Enter a question: ')
        submitted = st.form_submit_button('Submit')

        # if prompt is submitted
        if submitted:

            # responding to weather questions
            if "weather" in prompt:
                city = find_city(prompt)
                if city:
                    lat, lon = find_coordinates(city)
                else:
                    g = geocoder.ipinfo("me")
                    lat, lon = g.latlng
                response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_WEATHER_KEY}&units=metric")
                if response.status_code == 200:
                    weather = response.json()
                    weather_description = weather.get("weather", [])[0].get("description")
                    st.text_area(label="Luna's answer", value=f"In {weather['name']} it is {weather['main']['temp']} degrees. Sky conditions: {weather_description}", height=350)
                else:
                    st.text_area("Failed to retrieve weather. Status code:", response.status_code)

            # responding to other queries
            else:
                gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)
                gpt3_answer = gpt_turbo.predict(prompt)
                st.text_area(label="Luna's answer: ", value=gpt3_answer, height=350)


run_luna()
