import os
from dotenv import load_dotenv
from agent.agent import AIAgent
from colorama import init, Fore, Style

init(autoreset=True)

def main():
    # Создаем .env если его нет (заглушка)
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=your_key_here")
        print(Fore.RED + "Файл .env создан. Пожалуйста, добавьте туда ваш OPENAI_API_KEY.")
        return

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print(Fore.RED + "Ошибка: OPENAI_API_KEY не найден в .env")
        return

    agent = AIAgent()
    print(Fore.CYAN + Style.BRIGHT + "\n🤖 AI-Агент запущен. Введите 'exit' для выхода.")
    print(Fore.WHITE + "Примеры: 'Какая погода в Москве?', 'Сколько стоит биткоин?', 'Создай QR-код для google.com'\n")

    while True:
        try:
            user_input = input(Fore.GREEN + "Вы: " + Style.RESET_ALL)
            if user_input.lower() in ["exit", "quit", "выход"]:
                break
            
            print(Fore.YELLOW + "Думаю...", end="\r")
            response = agent.run(user_input)
            print(Fore.CYAN + "Агент: " + Style.RESET_ALL + response + "\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"Ошибка: {e}")

if __name__ == "__main__":
    main()
