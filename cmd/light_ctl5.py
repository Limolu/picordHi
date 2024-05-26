import discord
from discord import Interaction
from discord.ext import commands, tasks
from discord import app_commands
import RPi.GPIO as GPIO
import json
import os
from datetime import datetime, timedelta

class MissingRoleError(app_commands.AppCommandError):
    pass

def has_light_role():
    async def predicate(interaction: Interaction):
        role = discord.utils.get(interaction.guild.roles, name="打光師")
        if role not in interaction.user.roles:
            await interaction.response.send_message("你沒有權限操作燈光指令~", ephemeral=True)
        return True
    return app_commands.check(predicate)

class LightControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.LED_PIN = 26
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        self.light_state = "off"
        self.SCHEDULE_FILE = 'home/chang/picord/data/light_schedule.json'
        os.makedirs(os.path.dirname(self.SCHEDULE_FILE), exist_ok=True)
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
                self.save_schedule()

    @app_commands.command(name="light_on", description="立即開燈")
    @has_light_role()
    async def light_on_now(self, interaction: Interaction):
        if self.light_state == "off":
            GPIO.output(self.LED_PIN, GPIO.HIGH)
            self.light_state = "on"
            await interaction.response.send_message("電燈已開啟！")
        else:
            await interaction.response.send_message("電燈已經是開啟狀態。")

    @app_commands.command(name="light_off", description="立即關燈")
    @has_light_role()
    async def light_off_now(self, interaction: Interaction):
        if self.light_state == "on":
            GPIO.output(self.LED_PIN, GPIO.LOW)
            self.light_state = "off"
            await interaction.response.send_message("電燈已關閉！")
        else:
            await interaction.response.send_message("電燈已經是關閉狀態。")

    @app_commands.command(name="light_time_on", description="設置開燈定時")
    @app_commands.describe(時間="設置時間 (HH:MM)", 定時任務的名字="定時任務ID")
    @has_light_role()
    async def light_schedule_on(self, interaction: Interaction, 時間: str, 定時任務的名字: str):
        try:
            time_obj = datetime.strptime(時間, '%H:%M').time()
            if any(task['id'] == 定時任務的名字 for task in self.schedule):
                await interaction.response.send_message(f"ID '{定時任務的名字}' 已經被用過了，請換一個ID！")
                return
            for task in self.schedule:
                if task['time'] == 時間 and task['command'] != "on":
                    await interaction.response.send_message(f"已經存在 {task['time']} 的相反操作了，請重新設置！")
                    return
            self.schedule.append({"id": 定時任務的名字, "command": "on", "time": 時間, "user": interaction.user.name})
            self.save_schedule()
            await interaction.response.send_message(f"電燈將會於 {時間} 開起來！要記得你設置的定時任務的名字 `{定時任務的名字}` 唷！)")
        except ValueError:
            await interaction.response.send_message("時間格式錯誤，請使用 HH:MM 格式，冒號記得用半形！")

    @app_commands.command(name="light_time_off", description="設置關燈定時")
    @app_commands.describe(時間="設置時間 (HH:MM)", 定時任務的名字="定時任務ID")
    @has_light_role()
    async def light_schedule_off(self, interaction: Interaction, 時間: str, 定時任務的名字: str):
        try:
            time_obj = datetime.strptime(時間, '%H:%M').time()
            if any(task['id'] == 定時任務的名字 for task in self.schedule):
                await interaction.response.send_message(f"ID '{定時任務的名字}' 已經被用過了，請換一個ID！")
                return
            for task in self.schedule:
                if task['time'] == 時間 and task['command'] != "off":
                    await interaction.response.send_message(f"已經存在 {task['time']} 的相反操作了，請重新設置！")
                    return
            self.schedule.append({"id": 定時任務的名字, "command": "off", "time": 時間, "user": interaction.user.name})
            self.save_schedule()
            await interaction.response.send_message(f"電燈將會於 {時間} 關起來！要記得你設置的定時任務的名字 `{定時任務的名字}` 唷！)")
        except ValueError:
            await interaction.response.send_message("時間格式錯誤，請使用 HH:MM 格式，冒號記得用半形！")

    @app_commands.command(name="light_delete", description="刪除定時任務")
    @app_commands.describe(定時任務的名字="定時任務ID")
    @has_light_role()
    async def light_delete(self, interaction: Interaction, 定時任務的名字: str):
        for task in self.schedule:
            if task['id'] == 定時任務的名字:
                self.schedule.remove(task)
                self.save_schedule()
                await interaction.response.send_message(f"名叫 `{定時任務的名字}` 的定時任務已經幫你刪除了！")
                return
        await interaction.response.send_message(f"沒有名叫 `{定時任務的名字}` 的定時任務~")

    @app_commands.command(name="light_search", description="查詢所有定時任務")
    @has_light_role()
    async def light_search(self, interaction: Interaction):
        if self.schedule:
            response = "定時任務列表:\n"
            for task in self.schedule:
                response += f"任務的名字：{task['id']}，設定的時間：{task['time']}，操作：{task['command']}\n"
            await interaction.response.send_message(response)
        else:
            await interaction.response.send_message("目前沒有定時任務！")

async def setup(bot):
    await bot.add_cog(LightControl(bot))
