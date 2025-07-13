import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Access your API key (ensure OPENAI_API_KEY is set in your .env file)
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the ChatOpenAI instance
llm = ChatOpenAI(model="gpt-4o-mini",api_key=api_key)

# Test the setup
response = llm.invoke("Hello! Are you working?") 
print(response.content)