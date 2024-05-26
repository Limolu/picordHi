import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands

class HelpControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="picord_help", description="顯示所有可用指令的操作說明")
    async def picord_help(self, interaction: Interaction):
        help_message = """
        **PiCord 使用說明**

        **燈光控制指令：**
        1. `/light_on` - 立即開燈。
        2. `/light_off` - 立即關燈。
        3. `/light_time_on 時間 定時任務的名字` - 設置定時開燈，時間格式為 HH:MM。
        4. `/light_time_off 時間 定時任務的名字` - 設置定時關燈，時間格式為 HH:MM。
        5. `/light_delete 定時任務的名字` - 刪除指定的定時任務。
        6. `/light_search` - 查詢所有設置的定時任務。

        **權限管理指令：**
        1. `/light_perm 成員` - 分發控制燈光的權限給指定成員。
        2. `/light_unperm 成員` - 移除指定成員的控制燈光的權限。
        3. `/light_perm_search` - 查詢擁有 `打光師` 身分組的成員。

        **注意事項：**
        - 只有具有相應權限的用戶才能執行這些指令。
        - 時間格式需要使用24小時制的 HH:MM 格式，並確保使用半形冒號。

        如果有任何問題，請聯絡伺服器管理員。
        """
        await interaction.response.send_message(help_message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpControl(bot))
