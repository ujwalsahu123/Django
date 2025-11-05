import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print('GEMINI_API_KEY not found in .env')
    exit(1)

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    prompt = "You are PizzaBot, a friendly and knowledgeable assistant for our pizza shop.\nInstructions:\n- Be friendly and enthusiastic about our pizzas\n- Provide accurate information based on the pizza data provided\n- If asked about prices, sizes, or toppings, use the exact information from the data\n- For questions outside of the provided data, give general pizza-related advice\n- Keep responses concise but informative\n- Don't make up information about pizzas that aren't in the data\n\nUser message: What is the best pizza?"
    response = model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    print('Gemini response:')
    print(response.text if hasattr(response, 'text') else response)
except Exception as e:
    print('Error communicating with Gemini API:', e)
