import google.generativeai as genai
from django.conf import settings
from .models import Pizza
import json

# Configure the Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize the model with the working model version
model = genai.GenerativeModel("models/gemini-2.5-pro")

# Configure the model settings
generation_config = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

def get_pizza_context():
    """Get pizza information as context for the AI"""
    pizzas = Pizza.objects.all()
    pizza_data = []
    for pizza in pizzas:
        pizza_data.append({
            'name': pizza.name,
            'description': pizza.description,
            'price': str(pizza.price),
            'size': pizza.get_size_display(),
            'toppings': pizza.toppings
        })
    return json.dumps(pizza_data, indent=2)

def get_ai_response(user_message):
    """Get AI response based on user message and pizza context"""
    pizza_context = get_pizza_context()
    
    prompt = f"""You are PizzaBot, a friendly and knowledgeable assistant for our pizza shop.
    Here is the information about our available pizzas:
    {pizza_context}
    
    Instructions:
    - Be friendly and enthusiastic about our pizzas
    - Provide accurate information based on the pizza data provided
    - If asked about prices, sizes, or toppings, use the exact information from the data
    - For questions outside of the provided data, give general pizza-related advice
    - Keep responses concise but informative
    - Don't make up information about pizzas that aren't in the data
    
    User message: {user_message}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        if response and hasattr(response, 'text'):
            return response.text
        else:
            print(f"Unexpected response format: {response}")
            return "I apologize, but I couldn't generate a proper response. Please try asking in a different way."
    except Exception as e:
        print(f"Error in get_ai_response: {str(e)}")
        return "I apologize, but I'm having trouble right now. Please try again later."
