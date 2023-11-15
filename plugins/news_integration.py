from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
import os
from bs4 import BeautifulSoup
import requests

# Load environment variables at the top to avoid errors
load_dotenv()

# KEY
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

#load gpt
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)

def format_links(match) -> str:
    """
    This function takes a regular expression match object and returns a string with an HTML link.
    Inputs:
        match: a regular expression match object
    Outputs:
        formatted_link: string
    """
    url = match.group(0)
    return f'<a href="{url}" target="_blank">{url}</a>'


def web_scrape(url: str) -> str:
    """This function takes an url and returns the text of all paragraphs in the page.
    Inputs: url
    Outputs: paragraphs """
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        max_paragraphs = 1
        # Extract specific elements, e.g., all paragraphs
        paragraphs = soup.find_all('p')[:max_paragraphs]
        return paragraphs

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def get_week():
    """
    This function returns the current week number.
    Inputs: None
    Outputs: week number
    """
    return datetime.now().strftime("%U")


# news response
def news_response(user_query:str) -> str:
    """
    This function takes a user query and returns a news article related to the query.
    Inputs:
        user_query: string
    Outputs:
        formatted_answer: string
    """
    # keyword extraction
    identifying_news_keyword = f""" Instruction: You have to identify the keyword of a user query and match it ot one of the listed keywords.
                                Return a string with the name of the chosen keyword.
                                EXAMPLE 1
                                User query: What is the latest news on the stock market?
                                Answer: stock
                                EXAMPLE 2:
                                User query: What is the latest news on the coronavirus?
                                Answer: coronavirus
                                
                                User query: {user_query}
                                Answer:     
    """
    news_key_word = gpt_turbo.predict(identifying_news_keyword)

    # date extraction
    identifying_date = f""" Instruction: You have to identify the date indicated in the user query and match it ot one of the listed options: today, yesterday, this_week, last_week, this_month, this_year
                            Return a string with the name of the chosen option.
                            EXAMPLE 1: tech news today
                            Answer: today
                            User query: {user_query}
                            Answer: """
    time_frame = gpt_turbo.predict(identifying_date)

    date_functions = {
        "today": lambda: datetime.now().strftime("%Y-%m-%d"),
        "yesterday": lambda: (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "this_week": lambda: (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"),
        "last_week": lambda: (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "this_month": lambda: datetime.now().strftime("%Y-%m"),
        "this_year": lambda: datetime.now().strftime("%Y"),
    }

    # if the user does not specify a time frame, we will use the current date, else we call the lambda function
    if time_frame not in date_functions:
        end_date = start_date = datetime.now().strftime("%Y-%m-%d")
    else:
        date_function = date_functions[time_frame]
        start_date = date_function()  # Call the lambda function
        end_date = datetime.now().strftime("%Y-%m-%d")

    # API call
    top_headlines = requests.get(
        f"https://newsapi.org/v2/everything?q={news_key_word}&from={start_date}&to={end_date}&sortBy=relevancy&apiKey={NEWS_API_KEY}"
    ).json()

    print(top_headlines)
    formatted_results = []

    # check if the request was successful & process the article contents
    try:
        if top_headlines["totalResults"] == 0:
            return "No results found. Please try again or be more specific."
        # extracting data
        articles = top_headlines["articles"]
        for article in articles[:5]:
            if article["description"] is None:
                break
            print(article["description"])
            article_web = web_scrape(article["url"])
            llm_query_description = f""" Instruction: You have to provide a 20 word description of the news article using the information provided in the article. This is to use in a news API program.
            Context (news article): {article_web}"""
            gpt3_answer_description = gpt_turbo.predict(llm_query_description)
            formatted_result = f"- **{article['title']}**\n {gpt3_answer_description}\n  **URL:** {article['url']}"
            formatted_results.append(formatted_result)

        formatted_results = '\n'.join(formatted_results)
        return formatted_results

    except Exception as e:
        return top_headlines["status"]