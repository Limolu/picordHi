import discord
import RPi.GPIO as GPIO
import asyncio
import json
from datetime import datetime, timedelta

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

# 設置GPIO
LED_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# 設置Intents
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# JSON文件路徑
SCHEDULE_FILE = '/home/pi/light_schedule.json'

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

# 跟踪燈泡狀態
light_state = "off"  # 默認為關閉狀態

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.loop.create_task(schedule_checker())

@client.event
async def on_message(message):
    global light_state
    if message.author == client.user:
        return

    if message.content.startswith('/light'):
        parts = message.content.split(' ')
        command = parts[1]

        if command == "on" or command == "off":
            if len(parts) == 4:
                time_str = parts[2]
                task_id = parts[3]
                try:
                    time_obj = datetime.strptime(time_str, '%H:%M').time()
                    # 檢查ID是否重複
                    if any(task['id'] == task_id for task in schedule):
                        await message.channel.send(f"ID '{task_id}' 已被使用，請換一個ID")
                        return
                    # 檢查時間是否已被設定為相反的操作
                    for task in schedule:
                        if task['time'] == time_str:
                            if task['command'] != command:
                                await message.channel.send(f"已存在 {task['time']} 的相反操作，是否要取代? 請輸入 `/light replace {task['id']}` 來取代原本的設定")
                                return
                    # 添加新的定時任務
                    schedule.append({
                        "id": task_id,
                        "command": command,
                        "time": time_str,
                        "user": message.author.name
                    })
                    save_schedule(schedule)
                    await message.channel.send(f"電燈將於 {time_str} {'開啟' if command == 'on' else '關閉'} (ID: {task_id})")
                except ValueError:
                    await message.channel.send("時間格式錯誤，請使用 HH:MM 格式")
            else:
                if command == "on":
                    if light_state == "off":
                        GPIO.output(LED_PIN, GPIO.HIGH)
                        light_state = "on"
                        await message.channel.send("電燈已開啟")
                    else:
                        await message.channel.send("電燈已經是開啟狀態")
                elif command == "off":
                    if light_state == "on":
                        GPIO.output(LED_PIN, GPIO.LOW)
                        light_state = "off"
                        await message.channel.send("電燈已關閉")
                    else:
                        await message.channel.send("電燈已經是關閉狀態")

        elif command == "delete":
            if len(parts) == 3:
                task_id = parts[2]
                for task in schedule:
                    if task['id'] == task_id:
                        schedule.remove(task)
                        save_schedule(schedule)
                        await message.channel.send(f"定時任務 {task_id} 已刪除")
                        return
                await message.channel.send(f"未找到ID為 {task_id} 的定時任務")
        
        elif command == "search":
            if schedule:
                response = "定時任務列表:\n"
                for task in schedule:
                    response += f"ID: {task['id']}, 時間: {task['time']}, 操作: {task['command']}\n"
                await message.channel.send(response)
            else:
                await message.channel.send("目前沒有定時任務")
        
        elif command == "replace":
            if len(parts) == 3:
                task_id = parts[2]
                for task in schedule:
                    if task['id'] == task_id:
                        schedule.remove(task)
                        save_schedule(schedule)
                        await message.channel.send(f"原定時任務 {task_id} 已被刪除，請重新設置新的定時任務")
                        return
                await message.channel.send(f"未找到ID為 {task_id} 的定時任務")

        else:
            await message.channel.send("使用 `/light on HH:MM ID` 設置定時開燈，`/light off HH:MM ID` 設置定時關燈，`/light delete ID` 刪除定時任務，`/light search` 查詢定時任務")

async def schedule_checker():
    global light_state
    while True:
        now = datetime.now().time()
        for task in schedule:
            task_time = datetime.strptime(task["time"], '%H:%M').time()
            if now >= task_time and now < (datetime.combine(datetime.today(), task_time) + timedelta(minutes=1)).time():
                if task["command"] == "on" and light_state == "off":
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    light_state = "on"
                elif task["command"] == "off" and light_state == "on":
                    GPIO.output(LED_PIN, GPIO.LOW)
                    light_state = "off"
                schedule.remove(task)
                save_schedule(schedule)
        await asyncio.sleep(60)

# 運行Discord Bot
client.run(TOKEN)
