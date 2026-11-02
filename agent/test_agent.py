import os
import logging
from dotenv import load_dotenv
from agent.agent import AIAgent

# Настройка логов для теста
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRunner")

def run_test():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ОШИБКА: OPENAI_API_KEY не установлен. Тест не может быть запущен.")
        return

    agent = AIAgent(memory_file="test_memory.json")
    
    tests = [
        {"name": "Погода", "input": "Какая сейчас погода в Москве?"},
        {"name": "Криптовалюта", "input": "Сколько сейчас стоит Bitcoin в USD?"},
        {"name": "QR-код", "input": "Создай QR-код для ссылки https://google.com"},
        {"name": "Память (Шаг 1)", "input": "Привет! Меня зовут Алексей."},
        {"name": "Память (Шаг 2)", "input": "Как меня зовут?"},
        {"name": "Поиск", "input": "Кто сейчас президент Франции?"},
    ]

    print("\n🚀 Запуск комплексного теста агента...\n" + "="*50)

    for test in tests:
        print(f"🧪 Тестируем: {test['name']}")
        print(f"❓ Запрос: {test['input']}")
        try:
            response = agent.run(test['input'])
            print(f"✅ Ответ: {response}")
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
        print("-" * 50)

    # Проверка файла QR
    if os.path.exists("qr_code.png"):
        print("🖼 Файл qr_code.png создан успешно.")
    else:
        print("❌ Файл qr_code.png не найден.")

    print("\n🎯 Тестирование завершено.")

if __name__ == "__main__":
    run_test()
