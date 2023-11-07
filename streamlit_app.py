from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
from plugins import news_integration
from plugins import weather_integration


# Load environment variables at the top to avoid errors
load_dotenv()

# I was not able to get the key to work loading from the env why?
API_WEATHER_KEY = os.getenv("API_WEATHER_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

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
            identifying_topic = f""" Instruction: You have to identify the topic of a user query and match it ot one of the listed categories. 
                                Return a string with the name of the chosen category.
                                Categories: weather, news, other "
                                User query: {user_query}
                                Answer:
                                """
            query_topic = gpt_turbo.predict(identifying_topic)

            # responding to weather questions
            if "weather" == query_topic:
                response = weather_integration.weather_response(user_query)
                return st.text_area(label="Luna's answer: ", value=response, height=350)

            # responding to news related queries
            elif "news" == query_topic:
                response = news_integration.news_response(user_query)
                if type(response) is str:
                    return st.markdown(response, unsafe_allow_html=True)
                else:
                    return st.text_area("Failed to retrieve news. Status code:", response)

            # responding to other queries
            else:
                gpt3_answer = gpt_turbo.predict(user_query)
                st.text_area(label="Luna's answer: ", value=gpt3_answer, height=350)


run_luna()
