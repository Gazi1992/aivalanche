"""
Simple test script to verify Google Gemini API connection
"""
import google.generativeai as genai

API_KEY = "AIzaSyAx2VSqOPHuVNZFKGO89VDcI1PSZYStPew"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Say 'Hello! Gemini API is working!' if you can receive this message.")
    print("API Connection Successful!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"API Connection Failed: {e}")