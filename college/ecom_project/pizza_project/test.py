import google.generativeai as genai

def test_gemini_api():
    print("Testing Gemini API...")
    
    # Configure the API
    api_key = "AIzaSyCYEyMV5-qnVC1zoA-Pz4iiSV-NlLJ53Vo"
    print(f"\n1. Configuring API with key: {api_key[:10]}...")
    genai.configure(api_key=api_key)
    
    try:
        # List available models
        print("\n2. Available models:")
        for m in genai.list_models():
            print(f"- {m.name}")
            print(f"  Supported generation methods: {m.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {str(e)}")
    
    try:
        # Test with the correct model name
        model_names = [
            "models/gemini-2.5-pro"
        ]
        
        print("\n3. Testing different model names:")
        for model_name in model_names:
            try:
                print(f"\nTrying model name: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Test simple generation
                response = model.generate_content("Tell me a simple one-line joke about pizza")
                print(f"Response received: {response.text}")
                print(f"Success with model name: {model_name}")
                break
            except Exception as e:
                print(f"Failed with {model_name}: {str(e)}")
    
    except Exception as e:
        print(f"Error during model testing: {str(e)}")

if __name__ == "__main__":
    test_gemini_api()
