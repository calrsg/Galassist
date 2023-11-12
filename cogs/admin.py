import discord
from discord.ext import commands
from discord import app_commands
import os

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.hybrid_command(name="load", with_app_command=True, description="Load a cog.")
    async def load(self, ctx, extension):
        # awful fix for errors with unknown filenames
        load_success = False
        for filename in os.listdir("./cogs"):
            if f"{extension}.py" == filename:
                await self.bot.load_extension(f"cogs.{extension}")
                await ctx.send(f"**{extension}** loaded successfully")
                load_success = True
        if not load_success:
            await ctx.send(f"**{extension}** has *not* been loaded, please check cog name.")

    @commands.is_owner()
    @commands.hybrid_command(name="unload", with_app_command=True, description="Unload a cog")
    async def unload(self, ctx, extension):
        # awful fix for errors with unknown filenames
        unload_success = False
        for filename in os.listdir("./cogs"):
            if f"{extension}.py" == filename:
                if filename == "admin.py":
                    await ctx.send(f"**admin** cannot be unloaded, only reloaded.")
                    return
                await self.bot.unload_extension(f"cogs.{extension}")
                await ctx.send(f"**{extension}** unloaded successfully")
                unload_success = True
        if not unload_success:
            await ctx.send(f"**{extension}** has *not* been unloaded, please check cog name.")

    @commands.is_owner()
    @commands.hybrid_command(name="reload", with_app_command=True, description="Reload a cog.")
    async def reload(self, ctx, extension):
        # awful fix for errors with unknown filenames
        reload_success = False
        for filename in os.listdir("./cogs"):
            if f"{extension}.py" == filename:
                await self.bot.unload_extension(f"cogs.{extension}")
                await self.bot.load_extension(f"cogs.{extension}")
                await ctx.send(f"**{extension}** reloaded successfully")
                reload_success = True
        if not reload_success:
            await ctx.send(f"**{extension}** has *not* been reloaded, please check cog name.")

    @commands.is_owner()
    @commands.hybrid_command(name="listcogs", with_app_command=True, description="List all cogs in the cogs folder.")
    async def listcogs(self, ctx):
        cogs = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cogs.append(filename)
        await ctx.send(f"Found the following cogs: {str(cogs)[1:-1]}")


async def setup(bot):
    # take name of class, pass in the bot
    await bot.add_cog(Admin(bot))