import discord
from discord.ext import tasks

from config import (
    DISCORD_KEY,
    DISCORD_GUILD_ID,
    DISCORD_TARGET_USER_ID,  # ← используем эту переменную
    DISCORD_BAN_COOLDOWN,
)

intents = discord.Intents.all()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Бот запущен как {client.user}")
    ban_loop.start()
    print(f"ID пользователя для бана: {DISCORD_TARGET_USER_ID}")

@tasks.loop(seconds=DISCORD_BAN_COOLDOWN)
async def ban_loop():
    guild = client.get_guild(DISCORD_GUILD_ID)
    if not guild:
        print("Ошибка: сервер не найден")
        return

    try:
        member = await guild.fetch_member(DISCORD_TARGET_USER_ID)  # ← используем переменную
        print(f"Найден пользователь: {member}")
    except discord.NotFound:
        print(f"Пользователь {DISCORD_TARGET_USER_ID} не найден на сервере")
        return
    except discord.Forbidden:
        print("Нет прав получать участника")
        return

    try:
        await guild.ban(
            member,
            reason="Автобан: набегатор, перманентный КД",
            delete_message_seconds=0,
        )
        print(f"Пользователь {member} забанен")
    except discord.Forbidden:
        print("Ошибка: у бота нет прав на бан")
    except discord.HTTPException as e:
        print(f"Ошибка Discord API: {e}")

if DISCORD_KEY == "NULL":
    raise RuntimeError("DISCORD_KEY не задан, бот остановлен")

client.run(DISCORD_KEY)

        # member = guild.get_member(1360018743404789903) # 1230142922314354840