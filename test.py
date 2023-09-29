from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test GPT-3
gpt_turbo = AzureChatOpenAI(deployment_name="gpt-turbo", temperature=0)
prompt = "What is the weather today in Madrid?"
gpt3_answer = gpt_turbo.predict(prompt)
print(gpt3_answer)