from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from newsapi import NewsApiClient
import re
import os
import streamlit as st



# Load environment variables at the top to avoid errors
load_dotenv()

# I was not able to get the key to work loading from the env why?
API_WEATHER_KEY = os.getenv("API_WEATHER_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

#load gpt
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)

def format_links(match):
    """
    This function takes a regular expression match object and returns a string with an HTML link.
    Inputs:
        match: a regular expression match object
    Outputs:
        formatted_link: string
    """

    url = match.group(0)
    return f'<a href="{url}" target="_blank">{url}</a>'


# news response
def news_response(user_query):
    """
    This function takes a user query and returns a news article related to the query.
    Inputs:
        user_query: string
    Outputs:
        formatted_answer: string
    """
    identifying_news_topic = f""" Instruction: You have to identify whether or not the the news-related user query is interested in one topic of news specifically. Fin the list fo possible topics below. 
                        Possible topics: business, entertainment, health, science, sports, technology, other.
                        Return a string with the news topic.
                        User query: {user_query}
                        Answer:
                        """

    news_topic = gpt_turbo.predict(identifying_news_topic)
    print(news_topic)

    newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

    if news_topic == "other":
        top_headlines = newsapi.get_top_headlines(
            q=f'{news_topic}',
            category='general',
            language='en',
            page=2)

    else:
        top_headlines = newsapi.get_top_headlines(
            category=f'{news_topic}',
            language='en',
            page=2)

    print(top_headlines)

    if top_headlines["status"] == 'ok':
        # extracting data
        articles = top_headlines["articles"]
        information = []
        for article in articles[:6]:
            information.append((article["title"], article["description"], article["url"]))

        # creating a more complete user question
        llm_query = f"""
                        Instruction: You are an assistant that is providing information or advising the user.
                        Context (news articles): {information}
                        User query: {user_query}
                        Format of the answer: circular bullet point with title. Under title write a 2 line the description of the news article. Under description is the url of the news article.
                        Answer:
                        """

        gpt3_answer = gpt_turbo.predict(llm_query)

        # Use a regular expression to find URLs in the text and format them as clickable links
        formatted_answer = re.sub(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            format_links, gpt3_answer)

        # Display the formatted answer with clickable hyperlinks in a Streamlit text area
        # st.markdown allows rendering of HTML, which is needed to display the clickable links
        return formatted_answer # st.markdown(formatted_answer, unsafe_allow_html=True)

    else:
        return top_headlines["status"]