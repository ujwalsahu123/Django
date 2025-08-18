import google.generativeai as genai
from django.conf import settings
import json

# Configure the Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize the model with the working model version
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

def get_ecomm_context():
    """Return a static summary of product categories and sample products for Gemini context."""
    context = (
        "We sell Mobiles, Laptops, Top Wear, and Bottom Wear. "
        "Some popular brands are Samsung, Redmi, and FashionBrand. "
        "Example products: Samsung Galaxy M1 (Mobile, Rs. 18000), FashionBrand Top Wear (Rs. 999), Example Laptop (Rs. 55000). "
        "You can answer questions about prices, brands, categories, and offers."
    )
    return context

def get_ai_response(user_message):
    """Get AI response based on user message and ecomm context"""
    ecomm_context = get_ecomm_context()
    prompt = f"""You are ShopBot, a smart and friendly assistant for our e-commerce website.
Here is some information about our products:
{ecomm_context}

Instructions:
- Be friendly, helpful, and concise
- Use only the product data provided
- If asked about prices, brands, or categories, use the exact information from the data
- For questions outside of the provided data, give general e-commerce advice
- Don't make up information about products that aren't in the data

User message: {user_message}"""
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        print(f"Error in get_ai_response: {str(e)}")
        return "I apologize, but I'm having trouble right now. Please try again later."
