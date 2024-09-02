import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands
import serial
import os

# 初始化串口通信
print("cog執行")
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # 確定端口與波特率正確
    print("串口初始化成功")
except serial.SerialException as e:
    print(f"無法連接到串口: {e}")
    ser = None  # None防止沒連接時繼續讀取
print("cog初始化完成")

class COControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def read_sensor(self):
        print("讀取傳感器數據")
        if ser is None:
            print("ser None!")
            return None
        if ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"讀取到的數據: {line}")  # 打印傳感器讀取到的數據
                return int(line)
            except e:
                print("捕捉錯誤e")
                print(e)
        print("返回None")        
        return None

    @app_commands.command(name="check_co", description="檢查一氧化碳濃度")
    async def check_co(self, interaction: Interaction):
        print("命令開始執行")

        await interaction.response.defer() #防止超時

        co_level = self.read_sensor()
        print("傳感器讀取完成")
        if co_level is not None:
            if co_level > 300:  # 300為過高門檻
                await interaction.followup.send(f":warning: 警告！一氧化碳濃度過高：{co_level}")
            else:
                await interaction.followup.send(f"一氧化碳濃度正常：{co_level}")
        else:
            await interaction.followup.send("無法讀取傳感器數據。:smiling_face_with_tear: ")

async def setup(bot: commands.Bot):
    await bot.add_cog(COControl(bot))