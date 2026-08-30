from langchain_google_genai import ChatGoogleGenerativeAI
import os

os.environ["GEMINI_API_KEY"] = "dummy"

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
try:
    print(llm.model)
except Exception as e:
    print(e)
