import asyncio
import json

import discord
from discord.ext import commands
import time
import re

class TwitFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status = True
        self.log = TwitLog()
        self.bot.loop.create_task(self.init_log())

    async def init_log(self):
        await self.log.load()  # Load the data asynchronously

    @commands.Cog.listener()
    async def on_message(self, message):
        replace = ["twitter.com", "x.com"]
        ignore = ["fxtwitter.com", "vxtwitter.com"]
        if message.author.bot or not self.status:
            return
        for i in ignore:
            if i in message.content:
                return
        count = 0
        for r in replace:
            if r in message.content:
                count += 1
        if count > 0:
            new_content = ""
            url_regex = r"(https?:\/\/)(www\.)?(twitter\.com|x\.com)(\/[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?"

            urls = re.findall(url_regex, message.content)
            log_count = 0
            for url in urls:
                url = url[0] + url[1] + url[2] + url[3]
                for r in replace:
                    if r in url and "fxtwitter.com" not in url and "vxtwitter.com" not in url:
                        url = url.replace(r, "fxtwitter.com")
                        new_content += f"{url}\n"
                        log_count += 1

            if len(urls) > 0:
                await self.log.update(message.guild.id, message.author.id, log_count)
                prefix = f"Fixing Twitter link for {message.author.display_name}\n"
                new_content = prefix + new_content
                await message.reply(new_content, mention_author=False)

    @commands.is_owner()
    @commands.hybrid_command(name="twitstatus", with_app_command=True, description="Toggle Twitter link fixer.")
    async def twitstatus(self, ctx):
        if self.status:
            self.status = False
            await ctx.send("Twitter link fixer disabled.")
        else:
            self.status = True
            await ctx.send("Twitter link fixer enabled.")

    @commands.is_owner()
    @commands.hybrid_command(name="tfuser", with_app_command=True, description="Get stats for tweets fixed for a user.")
    async def tfuser(self, ctx, user: discord.Member = None, user_id: int = None):
        if user:
            num = await self.log.get_user_stats(user.id)
            return await ctx.send(f"{num} tweets fixed for {user.display_name}.")
        elif user_id:
            num = await self.log.get_user_stats(user_id)
            return await ctx.send(f"{num} tweets fixed for user matching ID {user_id}.")
        else:
            return await ctx.send("User or user ID must be passed in.")

    @commands.is_owner()
    @commands.hybrid_command(name="tfserver", with_app_command=True, description="Get stats for tweets fixed in a server.")
    async def tfserver(self, ctx, server_id):
        return await ctx.send(f"{await self.log.get_server_stats(server_id)} tweets fixed in server matching ID {server_id}.")

    @commands.is_owner()
    @commands.hybrid_command(name="tfall", with_app_command=True, description="Get stats for all tweets fixed.")
    async def tfall(self, ctx):
        server_stats, user_stats, total_fixed = await self.log.get_stats()
        embed = discord.Embed(title="Twitter Fix Stats", color=0x1DA1F2)
        embed.add_field(name="Total Tweets Fixed", value=total_fixed, inline=False)
        embed.add_field(name="Top Servers Fixed", value="\n".join([f"{v} : Server ID {k}" for k, v in list(server_stats.items())[:5]]), inline=False)
        embed.add_field(name="Top Users Fixed", value="\n".join([f"{v} : User ID {k}" for k, v in list(user_stats.items())[:5]]), inline=False)
        await ctx.send(embed=embed)

class TwitLog:
    def __init__(self):
        self.filepath = "twitlog.json"
        self.lock = asyncio.Lock()
        self.data = {}

    async def load(self):
        async with self.lock:
            with open(self.filepath, "r") as f:
                self.data = json.load(f)

    async def dump(self):
        async with self.lock:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)

    async def add_to_server(self, serverID, entryNum):
        serverID = str(serverID)
        async with self.lock:
            if serverID not in self.data["servers"]:
                self.data["servers"][serverID] = 0
            self.data["servers"][serverID] += entryNum

    async def add_to_user(self, userID, entryNum):
        userID = str(userID)
        async with self.lock:
            if userID not in self.data["users"]:
                self.data["users"][userID] = 0
            self.data["users"][userID] += entryNum

    async def add_total_fixed(self, entryNum):
        async with self.lock:
            self.data["links_fixed"] += entryNum

    async def get_stats(self):
        async with self.lock:
            sorted_servers = {k: v for k, v in sorted(self.data["servers"].items(), key=lambda item: item[1], reverse=True)}
            sorted_users = {k: v for k, v in sorted(self.data["users"].items(), key=lambda item: item[1], reverse=True)}
            total_fixed = self.data["links_fixed"]
            return sorted_servers, sorted_users, total_fixed

    async def get_server_stats(self, serverID):
        serverID = str(serverID)
        async with self.lock:
            if serverID not in self.data["servers"]:
                return 0
            return self.data["servers"][serverID]

    async def get_user_stats(self, userID):
        userID = str(userID)
        async with self.lock:
            if userID not in self.data["users"]:
                return 0
            return self.data["users"][userID]

    async def update(self, serverID, userID, entryNum):
        await self.add_to_server(serverID, entryNum)
        await self.add_to_user(userID, entryNum)
        await self.add_total_fixed(entryNum)


async def setup(bot):
    tf = TwitFix(bot)
    await bot.add_cog(tf)
    bg = BackgroundTimer(tf)
    bot.loop.create_task(bg.run())

class BackgroundTimer:
    def __init__(self, tf):
        self.tf = tf
        self.bot = tf.bot

    async def run(self):
        while True:
            await asyncio.sleep(60)
            await self.tf.log.dump()

