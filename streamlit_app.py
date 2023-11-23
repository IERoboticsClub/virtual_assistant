from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import en_core_web_sm
import geocoder
import base64
import json
from plugins import music
from plugins import calendar

# Load environment variables at the top to avoid errors
load_dotenv()

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

#create calendar file
calendar.create_calendar_file("https://blackboard.ie.edu/webapps/calendar/calendarFeed/03fb9a31c0b64a7eb91bdefd50a3b662/learn.ics")




def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

#load gpt
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)


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
                                Categories: weather, music, scheduling/calendar, other "
                                User query: {user_query}
                                Answer:
                                """
            query_topic = gpt_turbo.predict(identifying_topic)

            #Responding to calendar questions

            if query_topic == "scheduling/calendar":
                identifying_calendar_event = f"""Instruction: You have to identify the event/class that the user is trying to find in their calendar/schedule. 
                                    Then, identify a keyword in that event/class title. For example, if a user asks about when their calculus class is, the keyword would be calculus.
                                    If they ask about their algorithms and data structures class, the keyword could be algorithms"
                                    Keywords: calculus, , scheduling, other "
                                    User query: {user_query}
                                    Answer:
                                    """
                calendar_event = gpt_turbo.predict(identifying_calendar_event)

                calendar.calendar_response(user_query, calendar_event)



            
            #Responding to music questions
            if "music" == query_topic:
                music.music_response(user_query)

        # responding to other queries
             #else:
                #gpt3_answer = gpt_turbo.predict(user_query)
                #st.text_area(label="Luna's answer: ", value=gpt3_answer, height=350)
            


run_luna()

