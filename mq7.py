import discord
from discord import Interaction
from discord.ext import commands, tasks
from discord import app_commands
import serial
import os
from datetime import datetime, timedelta

# 初始化串口通信
ser = serial.Serial('/dev/ttyUSB0', 9600)  # 請根據實際串口號進行更改

class COControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def read_sensor(self):
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            return int(line)
        return None

    @app_commands.command(name="check_co", description="檢查一氧化碳濃度")
    async def check_co(self, interaction: Interaction):
        co_level = self.read_sensor()
        if co_level is not None:
            if co_level > 300:  # 300為過高的門檻
                await interaction.response.send_message(f"警告！一氧化碳濃度過高：{co_level}")
            else:
                await interaction.response.send_message(f"一氧化碳濃度正常：{co_level}")
        else:
            await interaction.response.send_message("無法讀取感測器數據。")

async def setup(bot):
    await bot.add_cog(COControl(bot))
