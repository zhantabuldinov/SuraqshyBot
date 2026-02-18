import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyCVkokgcVIhKxf0DL8yM2R5g5NcQDVIc0w"
genai.configure(api_key=GEMINI_API_KEY)

print("Доступные модели:")
print("=" * 50)

try:
    for model in genai.list_models():
        print(f"\n📌 {model.name}")
        print(f"   Версия: {model.display_name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"   Методы: {model.supported_generation_methods}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("\nПопытаюсь получить информацию о models...")
    
    # Альтернативный способ
    try:
        response = genai.list_models()
        for model in response:
            print(f"✓ {model}")
    except Exception as e2:
        print(f"❌ Ошибка: {e2}")
