import discord
from discord import Interaction
from discord.ext import commands, tasks
from discord import app_commands
import RPi.GPIO as GPIO
import json
from datetime import datetime, timedelta

class LightControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.LED_PIN = 26
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        self.light_state = "off"
        self.SCHEDULE_FILE = 'home/chang/picord/data/light_schedule.json'
        self.schedule = self.load_schedule()
        self.schedule_checker.start()

    def load_schedule(self):
        try:
            with open(self.SCHEDULE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_schedule(self):
        with open(self.SCHEDULE_FILE, 'w') as f:
            json.dump(self.schedule, f)

    @tasks.loop(minutes=1)
    async def schedule_checker(self):
        now = datetime.now().time()
        for task in self.schedule:
            task_time = datetime.strptime(task["time"], '%H:%M').time()
            if now >= task_time and now < (datetime.combine(datetime.today(), task_time) + timedelta(minutes=1)).time():
                if task["command"] == "on" and self.light_state == "off":
                    GPIO.output(self.LED_PIN, GPIO.HIGH)
                    self.light_state = "on"
                elif task["command"] == "off" and self.light_state == "on":
                    GPIO.output(self.LED_PIN, GPIO.LOW)
                    self.light_state = "off"
                self.schedule.remove(task)
                self.save_schedule()

    @app_commands.command(name="light_on", description="立即開燈")
    async def light_on_now(self, interaction: Interaction):
        if self.light_state == "off":
            GPIO.output(self.LED_PIN, GPIO.HIGH)
            self.light_state = "on"
            await interaction.response.send_message("電燈已開啟")
        else:
            await interaction.response.send_message("電燈已經是開啟狀態")

    @app_commands.command(name="light_off", description="立即關燈")
    async def light_off_now(self, interaction: Interaction):
        if self.light_state == "on":
            GPIO.output(self.LED_PIN, GPIO.LOW)
            self.light_state = "off"
            await interaction.response.send_message("電燈已關閉")
        else:
            await interaction.response.send_message("電燈已經是關閉狀態")

    @app_commands.command(name="light_time_on", description="設置開燈定時")
    @app_commands.describe(time="設置時間 (HH:MM)", task_id="定時任務ID")
    async def light_schedule_on(self, interaction: Interaction, time: str, task_id: str):
        try:
            time_obj = datetime.strptime(time, '%H:%M').time()
            if any(task['id'] == task_id for task in self.schedule):
                await interaction.response.send_message(f"ID '{task_id}' 已被使用，請換一個ID")
                return
            for task in self.schedule:
                if task['time'] == time and task['command'] != "on":
                    await interaction.response.send_message(f"已存在 {task['time']} 的相反操作，請重新設置")
                    return
            self.schedule.append({"id": task_id, "command": "on", "time": time, "user": interaction.user.name})
            self.save_schedule()
            await interaction.response.send_message(f"電燈將於 {time} 開啟 (ID: {task_id})")
        except ValueError:
            await interaction.response.send_message("時間格式錯誤，請使用 HH:MM 格式")

    @app_commands.command(name="light_time_off", description="設置關燈定時")
    @app_commands.describe(time="設置時間 (HH:MM)", task_id="定時任務ID")
    async def light_schedule_off(self, interaction: Interaction, time: str, task_id: str):
        try:
            time_obj = datetime.strptime(time, '%H:%M').time()
            if any(task['id'] == task_id for task in self.schedule):
                await interaction.response.send_message(f"ID '{task_id}' 已被使用，請換一個ID")
                return
            for task in self.schedule:
                if task['time'] == time and task['command'] != "off":
                    await interaction.response.send_message(f"已存在 {task['time']} 的相反操作，請重新設置")
                    return
            self.schedule.append({"id": task_id, "command": "off", "time": time, "user": interaction.user.name})
            self.save_schedule()
            await interaction.response.send_message(f"電燈將於 {time} 關閉 (ID: {task_id})")
        except ValueError:
            await interaction.response.send_message("時間格式錯誤，請使用 HH:MM 格式")

    @app_commands.command(name="light_delete", description="刪除定時任務")
    @app_commands.describe(task_id="定時任務ID")
    async def light_delete(self, interaction: Interaction, task_id: str):
        for task in self.schedule:
            if task['id'] == task_id:
                self.schedule.remove(task)
                self.save_schedule()
                await interaction.response.send_message(f"定時任務 {task_id} 已刪除")
                return
        await interaction.response.send_message(f"未找到ID為 {task_id} 的定時任務")

    @app_commands.command(name="light_search", description="查詢所有定時任務")
    async def light_search(self, interaction: Interaction):
        if self.schedule:
            response = "定時任務列表:\n"
            for task in self.schedule:
                response += f"ID：{task['id']}, 時間：{task['time']}, 操作：{task['command']}\n"
            await interaction.response.send_message(response)
        else:
            await interaction.response.send_message("目前沒有定時任務")

async def setup(bot):
    await bot.add_cog(LightControl(bot))
