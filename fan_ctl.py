import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
import requests
import time
import matplotlib.pyplot as plt
import re
import matplotlib.font_manager as fig
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import asyncio
import RPi.GPIO as GPIO
import numpy as np
from io import BytesIO

class MissingRoleError(app_commands.AppCommandError):
    pass

class FanControl(commands.Cog):
    def __init__(self, bot):
        self.auto_fan_task = None
        self.bot = bot
        self.LED_PIN = 16
        self.last_on_time = 0
        self.last_off_time = 0
        self.auto_fan_timeout = 1800
        self.base_url = "http://120.114.142.58:10001/upload.php"

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

    def gpio_on(self):
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        self.last_on_time = time.time()
        return "風扇已成功開啟。"

    def gpio_off(self):
        GPIO.output(self.LED_PIN, GPIO.LOW)
        self.last_off_time = time.time()
        return "風扇已成功關閉。"

    
    #異步
    async def fan_control_loop(self):
        """異步循環，根據溫度自動控制風扇。"""
        while True:
            print("檢查溫度...")
            response = requests.get(self.base_url)
            data = response.json()
            temperature_str = data.get("temperature")

            temperature_match = re.search(r'\d+', temperature_str)
            if temperature_match:
                temperature = int(temperature_match.group())
                
            current_time = time.time()

            if temperature > 28:
                print("溫度過高，開起風扇。")
                if current_time - self.last_on_time >= self.auto_fan_timeout:
                    print("自動風扇超時，開啟風扇。")
                    self.gpio_on()
                else:
                    print("風扇已經開啟，不需要再次開啟。")
            else:
                ("溫度正常，關閉風扇。")
                if current_time - self.last_off_time >= self.auto_fan_timeout:
                    print("自動風扇超時，關閉風扇。")
                    self.gpio_off()

            await asyncio.sleep(60)

    @app_commands.command(name="自動風扇", description="根據溫度自動控制風扇。")
    async def auto_fan(self, interaction: discord.Interaction):
        if self.auto_fan_task is None or self.auto_fan_task.done():
            self.auto_fan_task = asyncio.create_task(self.fan_control_loop())
            await interaction.response.send_message("自動風扇已啟動，將每分鐘檢查一次溫度。")
        else:
            await interaction.response.send_message("自動風扇已經在運行中。")

    @app_commands.command(name="停止自動風扇", description="停止自動風扇的控制循環。")
    async def stop_auto_fan(self, interaction: discord.Interaction):
        if self.auto_fan_task and not self.auto_fan_task.done():
            self.auto_fan_task.cancel()
            await interaction.response.send_message("自動風扇已停止。")
        else:
            await interaction.response.send_message("自動風扇未在運行。")

    @app_commands.command(name="風扇開啟", description="開啟風扇。")
    async def fan_on(self, interaction: discord.Interaction):
        result = self.gpio_on()
        await interaction.response.send_message(result)

    @app_commands.command(name="風扇關閉", description="關閉風扇。")
    async def fan_off(self, interaction: discord.Interaction):
        result = self.gpio_off()
        await interaction.response.send_message(result)

    @app_commands.command(name="查詢溫度", description="獲取最新的溫度和濕度。")
    async def temp(self, interaction: discord.Interaction):
        response = requests.get(self.base_url)
        data = response.json()
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        timestamp = data.get("timestamp")
        await interaction.response.send_message(f"溫度: {temperature}°C, 濕度: {humidity}%, 時間：{timestamp}")


    @app_commands.command(name="歷史溫度", description="查詢歷史溫度。")
    async def history_temp(self, interaction: discord.Interaction):

        await interaction.response.defer()
        embed = discord.Embed(title="歷史溫度查詢", description="請選擇查詢歷史溫度的某一天。")

        # 創建下拉選單
        select = Select(
            placeholder="選擇一個日期...",
            options=[
                discord.SelectOption(label="今天", description="查看今天的歷史數據", value="0"),
                discord.SelectOption(label="一天前", description="查看一天前的歷史數據", value="1"),
                discord.SelectOption(label="兩天前", description="查看兩天前的歷史數據", value="2"),
                discord.SelectOption(label="三天前", description="查看三天前的歷史數據", value="3"),
                discord.SelectOption(label="四天前", description="查看四天前的歷史數據", value="4"),
                discord.SelectOption(label="五天前", description="查看五天前的歷史數據", value="5"),
                discord.SelectOption(label="六天前", description="查看六天前的歷史數據", value="6")
            ]
        )

        async def select_callback(interaction: discord.Interaction):
            
            days_ago = int(select.values[0])
            start_time, end_time = self.get_day_timespan(days_ago)

            # 獲取圖像並發送給用戶
            plot = await self.generate_plot(start_time)
            await interaction.response.send_message(file=discord.File(plot, 'temperature_plot.png'))

        select.callback = select_callback

        view = View()
        view.add_item(select)

        await interaction.followup.send(embed=embed, view=view)

    # 用於生成圖表的函數
    async def generate_plot(self, start_time):
        day_param = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')

        url = f"{self.base_url}?day={day_param}"
        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API 回應數據: {data}")
            except ValueError:
                raise Exception("無效的json")
            
            if isinstance(data, list):
                timestamps = []
                temperatures = []
                humidities = []

                for entry in data:
                    if 'timestamp' in entry and 'temperature' in entry and 'humidity' in entry:
                        timestamp = entry['timestamp']
                        temperature = entry['temperature']
                        humidity = entry['humidity']
                    else:
                        print(f"數據格式錯誤: {entry}")

                    timestamps.append(timestamp)
                    temperatures.append(temperature)
                    humidities.append(humidity)
                    
                hours_only = [re.search(r'\b(\d{2}):', timestamp).group(1) for timestamp in timestamps]

                # 繪製圖表
                plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
                plt.rcParams['axes.unicode_minus'] = False

                plt.figure(figsize=(12, 8))
                plt.plot(hours_only, temperatures, label='溫度', color='red')
                plt.plot(hours_only, humidities, label='濕度', color='blue')

                plt.title(f'{day_param}的溫度和濕度隨時間變化')
                plt.xlabel('時間(小時)')
                plt.ylabel('數值')
                
                plt.gca().tick_params(axis='y', labelsize=10)
                plt.gca().tick_params(axis='x', labelsize=8)
                
                plt.legend()

                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                return buf
            else:
                raise Exception("非有效列表")
        else:
            raise Exception(f"無法從資料庫獲取數據，狀態碼: {response.status_code}")

    # 根據選擇的天數返回該天的時間範圍
    def get_day_timespan(self, days_ago):
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
        start_time = today - timedelta(days=days_ago)
        end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
    
        return int(start_time.timestamp()), int(end_time.timestamp())

# Bot setup
async def setup(bot):
    await bot.add_cog(FanControl(bot))
