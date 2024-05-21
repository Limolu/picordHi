import discord
import RPi.GPIO as GPIO
import asyncio

TOKEN = 'MTIzNjk4NzAzNjkyNjQ4MDQ2NQ.GxKJGt.XWLyyN83xAWcJAVTO2Pziu-YwuxCeFRHkjWP7o'

# 設置GPIO
LED_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!light'):
        command = message.content.split(' ')[1]
        if command == "on":
            GPIO.output(LED_PIN, GPIO.HIGH)
            await message.channel.send("Light turned ON")
        elif command == "off":
            GPIO.output(LED_PIN, GPIO.LOW)
            await message.channel.send("Light turned OFF")
        else:
            await message.channel.send("Invalid command. Use !light on or !light off")

# 運行Discord Bot
client.run(TOKEN)
