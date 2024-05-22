import discord
import RPi.GPIO as GPIO
import asyncio
import json
from datetime import datetime, timedelta

TOKEN = ''

# 設置GPIO
LED_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# 設置Intents
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# JSON文件路徑
SCHEDULE_FILE = '/home/chang/light_schedule.json'

# 加載或初始化定時任務
def load_schedule():
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f)

# 定時任務列表
schedule = load_schedule()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.loop.create_task(schedule_checker())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!light'):
        parts = message.content.split(' ')
        command = parts[1]

        if command == "on" or command == "off":
            if len(parts) == 3:
                time_str = parts[2]
                try:
                    time_obj = datetime.strptime(time_str, '%H:%M').time()
                    schedule.append({
                        "command": command,
                        "time": time_str,
                        "user": message.author.name
                    })
                    save_schedule(schedule)
                    await message.channel.send(f"電燈將於 {time_str} {'開啟' if command == 'on' else '關閉'}")
                except ValueError:
                    await message.channel.send("時間格式錯誤，請使用 HH:MM 格式")
            else:
                if command == "on":
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    await message.channel.send("電燈已開啟")
                elif command == "off":
                    GPIO.output(LED_PIN, GPIO.LOW)
                    await message.channel.send("電燈已關閉")
        else:
            await message.channel.send("使用`!light on`開啟電燈，`!light off`關閉電燈，或者`!light on HH:MM`設置定時開燈，`!light off HH:MM`設置定時關燈")

async def schedule_checker():
    while True:
        now = datetime.now().time()
        for task in schedule:
            task_time = datetime.strptime(task["time"], '%H:%M').time()
            if now >= task_time and now < (datetime.combine(datetime.today(), task_time) + timedelta(minutes=1)).time():
                if task["command"] == "on":
                    GPIO.output(LED_PIN, GPIO.HIGH)
                elif task["command"] == "off":
                    GPIO.output(LED_PIN, GPIO.LOW)
                schedule.remove(task)
                save_schedule(schedule)
        await asyncio.sleep(60)

# 運行Discord Bot
client.run(TOKEN)
