import discord
from discord.ext import commands
import random
import asyncio
import youtube_dl
import os

# Папка с изображениями
images_folder = 'C:\\Users\\prost\\OneDrive\\Desktop\\new\\Test\\DiscordBot\\images'
# Переменная для хранения состояния обработки сообщений
processing_messages = False

# Список интересных фактов
facts = [
    "Пчёлы общаются друг с другом с помощью танцев.",
    "В космосе нет звука.",
    "Улитки могут спать до трех лет подряд.",
    "Осьминоги имеют три сердца.",
    "Самая маленькая кость в человеческом теле находится в ухе."
]

# Создаем экземпляр Intents и включаем все необходимые intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Добавляем это, чтобы бот мог использовать голосовые каналы

# Создаем экземпляр бота с intents
bot = commands.Bot(command_prefix='!', intents=intents)


# Событие, которое срабатывает при готовности бота к работе
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')  # Или название канала
    if channel:
        await channel.send(f'Добро пожаловать на сервер, {member.mention}!')



# Событие, которое срабатывает при получении сообщения
@bot.event
async def on_message(message):
    if processing_messages:
        return
    # Проверяем, что сообщение не от самого бота, чтобы избежать бесконечного цикла
    if message.author == bot.user or message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # Отправляем обратно полученное сообщение
    await message.reply(message.content + "!")


@bot.command(name='calc')
async def calc(ctx, expression):
    try:
        result = eval(expression)
        await ctx.send(f'Результат: {result}')
    except Exception as e:
        await ctx.send(f'Ошибка: {e}')


@bot.command(name='image')
async def image(ctx):
    image_file = random.choice(os.listdir(images_folder))
    await ctx.send(file=discord.File(os.path.join(images_folder, image_file)))


# Команда, которая отправляет случайный интересный факт
@bot.command(name='факт')
async def fact(ctx):
    # Выбираем случайный факт из списка
    random_fact = random.choice(facts)
    # Отправляем факт в канал
    await ctx.send(random_fact)


# Команда для остановки бота
@bot.command(name='stop')
@commands.is_owner()  # Только владелец бота может использовать эту команду
async def stop(ctx):
    await ctx.send("Останавливаюсь...")
    await bot.close()


@bot.command(name='join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('Вы должны находиться в голосовом канале.')
        return

    channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()

@bot.command(name='play')
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.send('Бот не находится в голосовом канале.')
        return

    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']

    ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=URL))


@bot.command(name='remind')
async def remind(ctx, time: int, *, message: str):
    await ctx.send(f'Напоминание установлено. Я напомню вам через {time} секунд.')
    await asyncio.sleep(time)
    await ctx.send(f'Напоминание: {message}')


@bot.command(name='угадай')
async def guess(ctx):
    global processing_messages
    if processing_messages:
        return

    # Включаем временное отключение обработки сообщений
    processing_messages = True
    number = random.randint(1, 100)
    await ctx.send('Я загадал число от 1 до 100. Попробуйте угадать!')

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    while True:
        guess = await bot.wait_for('message', check=check)
        try:
            guess = int(guess.content)
        except ValueError:
            await ctx.send('Пожалуйста, введите число.')
            continue

        if guess < number:
            await ctx.send('Слишком мало!')
        elif guess > number:
            await ctx.send('Слишком много!')
        else:
            await ctx.send('Вы угадали!')
            processing_messages = False
            break



# Запуск бота (токен ниже)
bot.run('bot token')





