import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands
import serial
import os
import asyncio  # 用于实现异步延时

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
        """读取传感器数据"""
        print("讀取傳感器數據")
        if ser is None:
            print("ser None!")
            return None
        if ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"讀取到的數據: {line}")  # 打印傳感器讀取到的數據
                return int(line)
            except ValueError as e:
                print("捕捉錯誤e")
                print(e)
        print("返回None")
        return None

    async def get_average_reading(self, interval, count):
        """获取传感器在指定时间间隔内的平均值"""
        readings = []
        for _ in range(count):
            co_level = self.read_sensor()
            if co_level is not None:
                readings.append(co_level)
            await asyncio.sleep(interval)
        if readings:
            average = sum(readings) / len(readings)
            print(f"平均值: {average}")
            return average
        else:
            print("没有有效的读数")
            return None

    @app_commands.command(name="check_co", description="檢查一氧化碳濃度")
    async def check_co(self, interaction: Interaction):
        print("命令開始執行")

        await interaction.response.defer()  # 防止超時

        # 检测设置
        interval = 5  # 每次读取间隔时间（秒）
        check_count = 3  # 每次检测的读数次数
        threshold = 300  # 超标门槛
        required_exceed_count = 2  # 必须有2次超标

        # 第一次检测
        print("進行第一次檢測")
        first_average = await self.get_average_reading(interval, check_count)
        if first_average is None:
            await interaction.followup.send("無法讀取傳感器數據。:smiling_face_with_tear: ")
            return

        # 如果第一次检测超标，进行后续检测
        if first_average > threshold:
            exceed_count = 1  # 超标计数
            for i in range(2):  # 再检测两次
                print(f"進行第{i+2}次檢測")
                next_average = await self.get_average_reading(interval, check_count)
                if next_average is None:
                    await interaction.followup.send("無法讀取傳感器數據。:smiling_face_with_tear: ")
                    return

                if next_average > threshold:
                    exceed_count += 1

                if exceed_count >= required_exceed_count:
                    await interaction.followup.send(f":warning: 警告！多次檢測到一氧化碳濃度過高。")
                    return

            # 如果没有达到超标次数要求
            await interaction.followup.send(f"一氧化碳濃度超標但未達到警告標準。")
        else:
            await interaction.followup.send(f"一氧化碳濃度正常。")

async def setup(bot: commands.Bot):
    await bot.add_cog(COControl(bot))
