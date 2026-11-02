import os
import subprocess
import requests
import json
import qrcode
import logging
from datetime import datetime
from langchain.tools import tool
from duckduckgo_search import DDGS

logger = logging.getLogger("AIAgent.Tools")

# --- Вспомогательные функции для погоды ---
def get_coords(city):
    """Преобразует название города в координаты через Open-Meteo Geocoding API"""
    logger.info(f"Поиск координат для города: {city}")
    url = f"https://geocoding-api.open-meteo.com/v1/geocode?name={city}&count=1&language=ru&format=json"
    try:
        response = requests.get(url).json()
        if "results" in response:
            coords = response["results"][0]["latitude"], response["results"][0]["longitude"]
            logger.info(f"Координаты найдены: {coords}")
            return coords
    except Exception as e:
        logger.error(f"Ошибка при геокодинге {city}: {e}")
    return None, None

# --- Инструменты Агента ---

@tool
def web_search(query: str):
    """
    Поиск информации в интернете через DuckDuckGo. 
    Используйте этот инструмент для актуальных новостей или общих знаний.
    """
    logger.info(f"Запуск веб-поиска по запросу: {query}")
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            logger.info(f"Поиск завершен. Найдено результатов: {len(results)}")
            return "\n\n".join(results) if results else "Ничего не найдено."
    except Exception as e:
        logger.error(f"Ошибка веб-поиска: {e}")
        return f"Ошибка поиска: {e}"

@tool
def get_weather(city: str):
    """
    Получает текущую погоду в указанном городе.
    Принимает название города (например, 'Москва', 'Токио').
    """
    logger.info(f"Запрос погоды для города: {city}")
    lat, lon = get_coords(city)
    if lat is None:
        logger.warning(f"Город {city} не найден.")
        return f"Не удалось найти координаты для города {city}."
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        res = requests.get(url).json()
        if "current_weather" in res:
            cw = res["current_weather"]
            result = f"Погода в {city}: Температура {cw['temperature']}°C, Скорость ветра {cw['windspeed']} км/ч."
            logger.info(f"Погода получена: {result}")
            return result
    except Exception as e:
        logger.error(f"Ошибка API погоды: {e}")
    return "Ошибка при получении данных о погоде."

@tool
def get_crypto_price(coin: str, currency: str = "usd"):
    """
    Узнает курс криптовалюты.
    Аргументы: 
    - coin: id монеты (например, 'bitcoin', 'ethereum', 'solana')
    - currency: валюта (например, 'usd', 'eur', 'rub')
    """
    logger.info(f"Запрос курса {coin} в {currency}")
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin.lower()}&vs_currencies={currency.lower()}"
    try:
        res = requests.get(url).json()
        if coin.lower() in res:
            price = res[coin.lower()][currency.lower()]
            result = f"Курс {coin}: {price} {currency.upper()}"
            logger.info(f"Курс получен: {result}")
            return result
    except Exception as e:
        logger.error(f"Ошибка API CoinGecko: {e}")
    return f"Монета {coin} не найдена в базе CoinGecko."

@tool
def file_io(action: str, path: str, content: str = None):
    """
    Работа с файловой системой.
    - action: 'read' или 'write'
    - path: путь к файлу
    - content: содержимое (только для 'write')
    """
    logger.info(f"ФС операция {action} по пути: {path}")
    try:
        if action == "read":
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
                logger.info(f"Файл {path} прочитан ({len(data)} симв.)")
                return data
        elif action == "write":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Файл {path} успешно записан.")
            return f"Файл {path} успешно записан."
    except Exception as e:
        logger.error(f"Ошибка ФС {action}: {e}")
        return f"Ошибка ФС: {str(e)}"

@tool
def terminal_exec(command: str):
    """
    Выполнение терминальных команд.
    Используйте осторожно. Только безопасные команды (ls, dir, echo, date).
    """
    logger.info(f"Выполнение команды: {command}")
    try:
        forbidden = ["rm -rf", "format", "del /s", "mkfs"]
        if any(f in command for f in forbidden):
            logger.warning(f"Попытка выполнить запрещенную команду: {command}")
            return "Команда отклонена по соображениям безопасности."
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
        logger.info(f"Команда выполнена. Вывод: {output[:100]}...")
        return output
    except Exception as e:
        logger.error(f"Ошибка терминала: {e}")
        return f"Ошибка выполнения: {str(e)}"

@tool
def generate_qr(text: str):
    """
    Генерирует QR-код из переданного текста или ссылки.
    Сохраняет результат в файл 'qr_code.png'.
    """
    logger.info(f"Генерация QR для: {text}")
    try:
        qr = qrcode.make(text)
        qr.save("qr_code.png")
        logger.info("QR-код сохранен в qr_code.png")
        return "QR-код успешно создан и сохранен в файл qr_code.png"
    except Exception as e:
        logger.error(f"Ошибка QR: {e}")
        return f"Ошибка генерации QR: {str(e)}"

@tool
def manage_reminders(action: str, text: str = None, date_str: str = None):
    """
    Работа с напоминаниями.
    - action: 'add' (добавить), 'list' (список), 'clear' (очистить)
    - text: текст напоминания
    - date_str: дата и время в формате 'YYYY-MM-DD HH:MM'
    """
    logger.info(f"Управление напоминаниями: {action} {text if text else ''}")
    reminders_file = "reminders.json"
    try:
        if action == "list":
            if not os.path.exists(reminders_file): 
                logger.info("Список напоминаний пуст.")
                return "Напоминаний нет."
            with open(reminders_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Найдено напоминаний: {len(data)}")
                return data
        elif action == "add":
            if not text: 
                logger.warning("Попытка добавить напоминание без текста.")
                return "Ошибка: нужен текст напоминания."
            data = []
            if os.path.exists(reminders_file):
                with open(reminders_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            data.append({"text": text, "date": date_str or datetime.now().strftime("%Y-%m-%d %H:%M")})
            with open(reminders_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Напоминание '{text}' добавлено.")
            return f"Напоминание '{text}' добавлено."
        elif action == "clear":
            if os.path.exists(reminders_file): os.remove(reminders_file)
            logger.info("Все напоминания очищены.")
            return "Все напоминания удалены."
    except Exception as e:
        logger.error(f"Ошибка в manage_reminders: {e}")
        return f"Ошибка напоминаний: {str(e)}"

# Список всех инструментов для передачи в агента
all_tools = [web_search, get_weather, get_crypto_price, file_io, terminal_exec, generate_qr, manage_reminders]
