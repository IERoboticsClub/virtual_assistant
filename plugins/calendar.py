from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import en_core_web_sm
import base64
import json
import requests
import icalendar
from datetime import datetime, timezone


# Load environment variables at the top to avoid errors
load_dotenv()

#load gpt
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0.5)

def create_calendar_file(calendar_URL):
    url = calendar_URL
    file_path = "lauraUniCalendar.ics"  # The name you want to give to the downloaded file
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
            print(f"File downloaded and saved as '{file_path}'")
    else:
        print("Failed to download the file. Check the URL or try again later.")

def get_event_by_title(file_path, title):
    # Open the .ics file and parse its contents
    with open(file_path, 'rb') as f:
        cal = icalendar.Calendar.from_ical(f.read())

    # List to store found events
    matching_events = []

    # Splitting the title input into individual words
    input_words = title.lower().split()

    # Current date and time in UTC (aware datetime)
    now = datetime.now(timezone.utc)

    # Accessing events from the calendar
    for component in cal.walk():
        if len(matching_events) >= 5:
            break  # Exit the loop once 5 events are found
        if component.name == "VEVENT":
            # Access individual event details
            event_summary = component.get('summary').lower()
            event_start = component.get('dtstart').dt

            # Check if any word from the user input matches any word in the event title
            if any(word in event_summary for word in input_words) and event_start > now:
                matching_events.append({
                    "summary": component.get('summary'),
                    "start": event_start,
                    "end": component.get('dtend').dt
                })

    # Sort the events by start time (closest events first)
    matching_events.sort(key=lambda x: x['start'])

    return matching_events[:5]  # Return only the 5 closest upcoming events

def get_events_on_day(file_path, day):
    # Open the .ics file and parse its contents
    with open(file_path, 'rb') as f:
        cal = icalendar.Calendar.from_ical(f.read())

    # List to store events happening on the specified day
    events_on_day = []

    # Iterate through calendar events
    for component in cal.walk():
        if component.name == "VEVENT":
            # Access individual event details
            event_start = component.get('dtstart').dt

            # Check if the event's start date matches the provided day
            if event_start.date() == day:
                events_on_day.append({
                    "summary": component.get('summary'),
                    "start": event_start,
                    "end": component.get('dtend').dt
                })

    return events_on_day

def calendar_response(user_query, calendar_event):
    file_path = 'lauraUniCalendar.ics'  # Replace with your .ics file path
    event_title =  calendar_event
    found_events = get_event_by_title(file_path, event_title)

    formatted_event_string=""

    if found_events:
        for event in found_events:
            formatted_event_string+=(f"Event: {event['summary']}\n")
            formatted_event_string+=(f"Start: {event['start']}\n")
            formatted_event_string+=(f"End: {event['end']}\n\n")
    else:
        formatted_event_string+="No upcoming events found with that title."
    
    if len(formatted_event_string) > 1:
        llm_query = f"""
        Instruction: You are an assistant that is retrieving instances of a class/event in a user's calendar.
        Context (Event/Class occurances): here are the upcoming {event_title} classes/events in your calendar:  {formatted_event_string}"
        User query: {user_query}
        Answer: 
        """
        # generating answer
        gpt3_answer = gpt_turbo.predict(llm_query)
        #luna_response = f"\n\nHere is a playlist of the top songs by {artist}:\n {artistSongs}"
            
        st.text_area(label="Luna's answer: ", value=gpt3_answer, height=350)

    else:
        st.text_area("Failed to retrieve calendar information.")

