import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands

class PermissionControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_or_create_role(self, guild: discord.Guild, role_name: str):
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name)
        return role

    @app_commands.command(name="light_perm", description="分發控制燈光的權限給成員")
    @app_commands.describe(成員="指定要分發權限的成員")
    async def light_perm(self, interaction: Interaction, 成員: discord.Member):
        guild = interaction.guild
        role = await self.get_or_create_role(guild, "打光師")
        await 成員.add_roles(role)
        await interaction.response.send_message(f"已經給 {成員.mention} 分發了控制燈光的權限", ephemeral=True)

    @app_commands.command(name="light_unperm", description="移除控制燈光的權限")
    @app_commands.describe(成員="指定要移除權限的成員")
    async def light_unperm(self, interaction: Interaction, 成員: discord.Member):
        role = discord.utils.get(interaction.guild.roles, name="打光師")
        if role:
            await 成員.remove_roles(role)
            await interaction.response.send_message(f"已經移除了 {成員.mention} 的控制燈光的權限", ephemeral=True)
        else:
            await interaction.response.send_message(f"沒有找到 `打光師` 角色", ephemeral=True)

    @app_commands.command(name="light_perm_search", description="查詢擁有 `打光師` 身分組的成員")
    async def light_perm_search(self, interaction: Interaction):
        role = discord.utils.get(interaction.guild.roles, name="打光師")
        if not role:
            await interaction.response.send_message("尚未建立 '打光師' 角色，輸入`/light_perm`以及要給予權限的成員，即可建立！", ephemeral=True)
            return
        members_with_role = [member.mention for member in role.members]
        if members_with_role:
            await interaction.response.send_message("擁有 `打光師` 身分組的成員:\n" + "\n".join(members_with_role), ephemeral=True)
        else:
            await interaction.response.send_message("目前沒有成員擁有 `打光師` 身分組", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PermissionControl(bot))
