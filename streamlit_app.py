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

#Spotify API keys
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")

#load gpt
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)


# Find name of a city in a user_query
def find_city(input_text):
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
    geo_data = requests.get(
        f"https://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=10&appid={API_WEATHER_KEY}&units").json()
    return geo_data[0]["lat"], geo_data[0]["lon"]


# Main function
def run_luna():
    st.title('🌚  Welcome to Luna')

    # creating a text box
    with st.form('my_form'):
        # waiting for user input
        user_query = st.text_area('Enter a question: ')
        submitted = st.form_submit_button('Submit')

        # if user_query is submitted
        if submitted:

            # let's make this model answer general questions and classify into topics
            identifying_topic = f""" Instruction: You have to identify the topic of a user query and match it ot one of the listed topic categories. 
                                Return a string with the name of the chosen category.
                                Categories: weather, other "
                                User query: {user_query}
                                Answer:
                                """
            query_topic = gpt_turbo.predict(identifying_topic)

            # responding to weather questions
            if "weather" == query_topic:
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
                    weather_description = weather.get("weather", [])[0].get("description")

                    # creating a more complete user question
                    llm_query = f"""
                    Instruction: You are an assistant that is providing information or advising the user.
                    Context (Weather details): in {weather['name']}, it is {weather['main']['temp']} degrees. Sky conditions: {weather_description}"
                    User query: {user_query}
                    Answer:
                    """
                    # generating answer
                    gpt3_answer = gpt_turbo.predict(llm_query)
                    st.text_area(label="Luna's answer: ", value=gpt3_answer, height=350)

                else:
                    st.text_area("Failed to retrieve weather. Status code:", response.status_code)

            # responding to other queries
            else:
                gpt3_answer = gpt_turbo.predict(user_query)
                st.text_area(label="Luna's answer: ", value=gpt3_answer, height=350)


run_luna()
