import disnake
from disnake.ext import tasks

from config import (
    DISCORD_KEY,
    DISCORD_GUILD_ID,
    DISCORD_TARGET_USER_ID,
    DISCORD_BAN_COOLDOWN,
)

intents = disnake.Intents.all()
bot = disnake.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    print(f"ID сервера: {DISCORD_GUILD_ID}")
    print(f"ID пользователя для бана: {DISCORD_TARGET_USER_ID}")
    print(f"Интервал бана: {DISCORD_BAN_COOLDOWN} секунд")
    
    # Проверяем доступность сервера
    guild = bot.get_guild(DISCORD_GUILD_ID)
    if guild:
        print(f"Сервер найден: {guild.name}")
        # Проверяем права бота на сервере
        perms = guild.me.guild_permissions
        print(f"Права бана: {perms.ban_members}")
    else:
        print("Сервер не найден!")
    
    ban_loop.start()
    print("Запущен цикл бана")


@tasks.loop(seconds=DISCORD_BAN_COOLDOWN)
async def ban_loop():
    print(f"\n[Запуск бана {ban_loop.current_loop}]")
    
    guild = bot.get_guild(DISCORD_GUILD_ID)
    if not guild:
        print("Ошибка: сервер не найден")
        return
    
    print(f"Попытка забанить пользователя с ID: {DISCORD_TARGET_USER_ID}")
    
    try:
        member = await guild.fetch_member(DISCORD_TARGET_USER_ID)
        print(f"Найден пользователь: {member} ({member.id})")
        print(f"Статус пользователя: {member.status}")
        print(f"Роли пользователя: {[role.name for role in member.roles]}")
    except disnake.NotFound:
        print(f"Пользователь {DISCORD_TARGET_USER_ID} не найден на сервере")
        return
    except disnake.Forbidden:
        print("Нет прав получать участника")
        return
    except disnake.HTTPException as e:
        print(f"Ошибка при получении участника: {e}")
        return

    # Проверяем, не забанен ли уже пользователь
    try:
        bans = await guild.bans()
        for ban_entry in bans:
            if ban_entry.user.id == DISCORD_TARGET_USER_ID:
                print(f"Пользователь {member} уже забанен")
                return
    except disnake.Forbidden:
        print("Нет прав для просмотра списка банов")
    except Exception as e:
        print(f"Не удалось проверить список банов: {e}")

    try:
        print("Попытка забанить...")
        await member.ban(
            reason="Автобан: набегатор, перманентный КД",
            delete_message_days=0,  # ← ИСПРАВЛЕНО: seconds → days
        )
        print(f"✓ Пользователь {member} успешно забанен")
    except disnake.Forbidden:
        print("✗ Ошибка: у бота нет прав на бан")
        print(f"Роль бота: {guild.me.top_role.name}")
        print(f"Роль пользователя: {member.top_role.name}")
    except disnake.HTTPException as e:
        print(f"✗ Ошибка Discord API: {e}")
    except Exception as e:
        print(f"✗ Неизвестная ошибка: {e}")


# Команда для ручного тестирования
@bot.event
async def on_message(message):
    if message.content == "!testban":
        guild = bot.get_guild(DISCORD_GUILD_ID)
        if guild:
            try:
                member = await guild.fetch_member(DISCORD_TARGET_USER_ID)
                await member.ban(
                    reason="Тест бана",
                    delete_message_days=0,  # ← ИСПРАВЛЕНО: seconds → days
                )
                await message.channel.send(f"✅ Пользователь {member} забанен")
            except disnake.Forbidden:
                await message.channel.send("❌ Нет прав для бана")
            except disnake.NotFound:
                await message.channel.send("❌ Пользователь не найден")
            except Exception as e:
                await message.channel.send(f"❌ Ошибка: {e}")
    
    # Проверка информации о боте
    elif message.content == "!botinfo":
        guild = bot.get_guild(DISCORD_GUILD_ID)
        if guild:
            me = guild.me
            perms = me.guild_permissions
            embed = disnake.Embed(
                title="Информация о боте",
                description=f"Сервер: {guild.name}",
                color=disnake.Color.blue()
            )
            embed.add_field(name="Имя бота", value=str(me), inline=True)
            embed.add_field(name="Права на бан", value="✅" if perms.ban_members else "❌", inline=True)
            embed.add_field(name="Высшая роль", value=me.top_role.name, inline=True)
            embed.add_field(name="Целевой ID", value=DISCORD_TARGET_USER_ID, inline=True)
            embed.add_field(name="Интервал", value=f"{DISCORD_BAN_COOLDOWN} сек", inline=True)
            await message.channel.send(embed=embed)
    
    # Проверка существования пользователя
    elif message.content == "!checkuser":
        guild = bot.get_guild(DISCORD_GUILD_ID)
        if guild:
            try:
                member = await guild.fetch_member(DISCORD_TARGET_USER_ID)
                embed = disnake.Embed(
                    title="Информация о пользователе",
                    description=f"ID: {DISCORD_TARGET_USER_ID}",
                    color=disnake.Color.green()
                )
                embed.add_field(name="Имя", value=str(member), inline=True)
                embed.add_field(name="Статус", value=str(member.status), inline=True)
                embed.add_field(name="Присоединился", value=member.joined_at.strftime("%Y-%m-%d %H:%M"), inline=True)
                embed.add_field(name="Роли", value=", ".join([role.name for role in member.roles[1:]]), inline=False)
                embed.add_field(name="Высшая роль", value=member.top_role.name, inline=True)
                await message.channel.send(embed=embed)
            except disnake.NotFound:
                await message.channel.send(f"❌ Пользователь {DISCORD_TARGET_USER_ID} не найден на сервере")
            except disnake.Forbidden:
                await message.channel.send("❌ Нет прав для просмотра участника")


if DISCORD_KEY == "NULL":
    raise RuntimeError("DISCORD_KEY не задан, бот остановлен")

bot.run(DISCORD_KEY)
