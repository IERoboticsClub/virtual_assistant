# AI and Robotics Virtual Assistant

![hacktoberfest](https://img.shields.io/badge/Hacktoberfest-2023-blueviolet?style=for-the-badge&logo=appveyor)

<br>

# Table of Contents
[1. Project Description](#project-description)<br>
[2. Project Goals](#project-goals)<br>
[3. Development Setup](#development-setup)<br>
[4. Contributing](#contributing)<br>

## Project Description

Imagine having a digital assistant that can chat with you like a real person, providing you with instant and relevant information whenever you need it. That's the power of an AI virtual assistant and our vision is inspired by J.A.R.V.I.S (Iron Man's AI assistant). We want to create a virtual assistant that can help you with your day-to-day tasks, such as finding information on the web, scheduling meetings, and more.

The overall workflow of a virtual assistant starts with voice or text interaction. If the input was voice, it is converted into text and then use that text to find the intent of the user. Once we have the intent, we can use it to find the relevant information and respond back to the user. The response can be in the form of text or voice, depending on the user's preference.

![Virtual Assistant Workflow](./assets/assistant-workflow.png)



## Project Goals

- Create a virtual assistant that can chat with you like a real person
- Provide instant and relevant information whenever you need it
- Help you with your day-to-day tasks, such as finding information on the web, scheduling meetings, and more


## Development Setup

1. Create a `.env` file with your Azure API credentials

2. Create and activate a virtual environment
```bash
python3 -m venv venv && . venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```


## Contributing ✨

Follow the steps in `CONTRIBUTING.md` to contribute to this project.