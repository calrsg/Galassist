import asyncio
import discord
from discord.ext import commands
import re
from util.twitlog import TwitLog

class TwitFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status = True
        self.log = TwitLog()
        self.bot.loop.create_task(self.init_log())

    async def init_log(self):
        await self.log.load()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore if function turned off or message author is a bot
        if message.author.bot or not self.status:
            return

        # Intuitive replies
        if message.reference and message.reference.resolved:
            parent = message.reference.resolved
            if parent.author == self.bot.user:
                parent_ref = await message.channel.fetch_message(parent.reference.message_id)
                if parent.reference and parent_ref:
                    parent_author = parent_ref.author
                    if parent_author != message.author:
                        if await self.log.get_ignored(parent_author.id) is not True:
                            await parent_author.send(f"{message.author.display_name} replied to a fixed Tweet you posted in {message.guild.name}: "
                                                     f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\n"
                                                     f"If you want to disable these reminders, use the command /tfremind.")

        # URL Replacements
        replace = ["twitter.com", "x.com"]
        ignore = ["fxtwitter.com", "vxtwitter.com"]

        # Ignore if message contains pre-fixed URLs
        for i in ignore:
            if i in message.content:
                return
        # Check if URLs contain replacements before Regex searching
        count = 0
        for r in replace:
            if r in message.content:
                new_content = ""
                url_regex = r"(https?:\/\/)(www\.)?(twitter\.com|x\.com)(\/[-a-zA-Z0-9()@:%_\+.~#?&=]*)*(\/status\/[0-9]*\/)(photo\/[0-9])"
                urls = re.findall(url_regex, message.content)
                log_count = 0
                for url in urls:
                    spoiler = await spoiler_check(message.content)
                    url = url[0] + url[1] + url[2] + url[3] + url[4]
                    for r in replace:
                        if r in url and "fxtwitter.com" not in url and "vxtwitter.com" not in url:
                            url = url.replace(r, "fxtwitter.com")
                            if spoiler:
                                url = "||" + url + "||"
                            new_content += f"{url}\n"
                            log_count += 1

                if len(urls) > 0:
                    await self.log.update(message.guild.id, message.author.id, log_count, )
                    prefix = f"Fixing Tweet for {message.author.display_name}\n"
                    if spoiler:
                        prefix = f"Fixing Tweet for {message.author.display_name} with hidden content\n"
                    new_content = prefix + new_content
                    await message.reply(new_content, mention_author=False)
                    return

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

    @commands.hybrid_command(name="tfremind", with_app_command=True, description="Toggle ignoring reply reminders.")
    async def tfremind(self, ctx):
        cur = await self.log.get_ignored(ctx.author.id)
        if cur is False:
            await self.log.add_ignored(ctx.author.id)
            await ctx.author.send("You will no longer receive reply reminders.")
        else:
            await self.log.rem_ignored(ctx.author.id)
            await ctx.author.send("You will now receive reply reminders.")
async def spoiler_check(message):
    split = message.split("||")
    if len(split) >= 2:
        return True
    return False

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

