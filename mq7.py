import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands
import serial
import os

# 初始化串口通信
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # 确保端口和波特率正确
except serial.SerialException as e:
    print(f"无法连接到串口: {e}")
    ser = None  # 设置为None以防止未连接时继续尝试读取

class COControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def read_sensor(self):
        if ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"读取到的数据: {line}")  # 打印传感器读取到的数据
                return int(line)
            except ValueError:
                print("无法解析传感器数据为整数")
        return None

    @app_commands.command(name="check_co", description="检查一氧化碳浓度")
    async def check_co(self, interaction: Interaction):
        co_level = self.read_sensor()
        if co_level is not None:
            if co_level > 300:  # 300为过高的门槛
                await interaction.response.send_message(f"警告！一氧化碳浓度过高：{co_level}")
            else:
                await interaction.response.send_message(f"一氧化碳浓度正常：{co_level}")
        else:
            await interaction.response.send_message("无法读取传感器数据。")

async def setup(bot: commands.Bot):
    await bot.add_cog(COControl(bot))
