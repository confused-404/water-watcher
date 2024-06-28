from dotenv import load_dotenv
import google.generativeai as genai
import os

class Model():
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        # print("api key Added \n\n\n\n\n")
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    def generate(self, prompt):
        return self.model.generate_content(prompt).text