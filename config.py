"""
Этот модуль содержит все основные конфигурации Dev-bot.
"""

import json
import os

import pytz
import requests
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

def get_env_variable(name: str, default: str = "NULL") -> str:
    """
    Функция для безопасного получения переменных окружения.
    Если переменная не найдена, возвращает значение по умолчанию.
    """
    value = os.getenv(name)
    if not value:
        print(f"Предупреждение: {name} не найден в файле .env. "
              f"Используется значение по умолчанию: {default}"
        )
        return default
    return value

# Получение переменных из окружения
DISCORD_KEY = get_env_variable("DISCORD_KEY")
DISCORD_GUILD_ID = int(get_env_variable("DISCORD_GUILD_ID", "1354120935225167883"))
DISCORD_TARGET_USER_ID = int(get_env_variable("DISCORD_TARGET_USER_ID", "1230142922314354840"))
DISCORD_BAN_COOLDOWN = int(get_env_variable("DISCORD_BAN_COOLDOWN", "60"))