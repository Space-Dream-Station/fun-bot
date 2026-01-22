import discord
from discord.ext import tasks

from config import (
    DISCORD_KEY,
    DISCORD_GUILD_ID,
    DISCORD_TARGET_USER_ID,
    DISCORD_BAN_COOLDOWN,
)

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Бот запущен как {client.user}")
    ban_loop.start()


@tasks.loop(seconds=DISCORD_BAN_COOLDOWN)
async def ban_loop():
    guild = client.get_guild(DISCORD_GUILD_ID)
    if not guild:
        return

    member = guild.get_member(DISCORD_TARGET_USER_ID)
    if not member:
        # Пользователь не на сервере (уже забанен или не зашёл)
        return

    try:
        await guild.ban(
            member,
            reason="Автобан: набегатор, перманентный КД",
            delete_message_days=0,
        )
        print(f"Пользователь {member} забанен")
    except discord.Forbidden:
        print("Ошибка: у бота нет прав на бан")
    except discord.HTTPException as e:
        print(f"Ошибка Discord API: {e}")


if DISCORD_KEY == "NULL":
    raise RuntimeError("DISCORD_KEY не задан, бот остановлен")

client.run(DISCORD_KEY)
