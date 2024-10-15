import asyncio

import discord
from discord.ext import commands
import re
from util.twitlog import TwitLog

class TwitFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status = True
        self.url = "fxtwitter.com"
        self.check = ["//twitter.com", "//x.com", "//nitter.net", "//www.twitter.com", "//www.x.com", "//www.nitter.net"]
        self.replace = ["twitter.com", "x.com", "nitter.net"]
        self.ignore = ["fxtwitter.com", "vxtwitter.com"]
        self.emoji = "<:twitter_logo:1203668202324885554>"
        self.id = "tfid"
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
        res = await self.is_intuitive_reply(message)
        if not res:
            pass
        else:
            await res.send(
                f"{message.author.display_name} replied to your message that I fixed in {message.guild.name}: "
                f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\n"
                f"If you want to disable these reminders, use the command /tfremind.")

        if await self.find_tweet(message):
            fixed, urls = await self.fix_message(message)
            try:
                await asyncio.sleep(0.4)
                await message.edit(suppress=True)
            except discord.Forbidden:
                fixed = ":prohibited: I don't have permission to supress embeds in the message I am replying to, please give me the `Manage Messages` permission to avoid clutter.\n" + content
            try:
                new_msg = await message.reply(fixed, mention_author=False)
                await new_msg.add_reaction("❌")
            except discord.Forbidden:
                return
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        # If replied to message is by the reaction user, and if the reaction emoji is for deleting
        if reaction.message.reference.resolved.author.id == user.id and reaction.emoji == "❌":
            await reaction.message.delete()
            await user.send(f"You deleted a tweet I fixed in {reaction.message.guild.name}.")

    @commands.is_owner()
    @commands.hybrid_command(name="tftoggle", with_app_command=True, description="Toggle Twitter link fixer.")
    async def tftoggle(self, ctx):
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

    async def is_intuitive_reply(self, message):
        if message.author.bot:
            return False
        # Check if the replied to message is context message
        if message.reference and message.reference.resolved:
            search = message.reference.resolved
            # If it's not a bot message, return False
            if not search.author.bot:
                return False
            # If the replied to message is not replying to another message, return False
            if not search.reference:
                return False
            # Check if the bot message fixed a twitter link
            is_fixed = search.content.find("fxtwitter.com")
            # Handle bot not being able to load resolved reference, force load message that we know exists
            target = await search.channel.fetch_message(search.reference.message_id)
            if target and is_fixed != -1:
                user = await self.bot.fetch_user(int(target.author.id))
                # Check if the user has disabled reminders, and if the user is not replying to their own fixed tweet
                if not await self.log.get_ignored(user.id) and user.id != message.author.id:
                    return user
        return False

    async def find_tweet(self, message):
        # URL Replacements
        # Ignore if message contains pre-fixed URLs
        for i in self.ignore:
            if i in message.content:
                return False
        # Check if URLs contain replacements before Regex searching
        count = 0
        for r in self.check:
            if r in message.content and "status" in message.content:
                return True
        return False

    async def fix_message(self, message):
        regex = r"(https?:\/\/)((?:www.)?twitter\.com|x\.com|nitter\.net)(\/[-a-zA-Z0-9()@:%_\+.~#?&=]*)(\/status\/[-a-zA-Z0-9()@:%_\+.~#?&=]*)(\/photo\/[0-9]*)?"
        new_content = ""
        urls = re.findall(regex, message.content)
        new_urls = []
        log_count = 0
        for url in urls:
            spoiler = await spoiler_check(message.content)
            new_url = url[0] + url[1] + url[2] + url[3] + url[4]
            url = ''.join(url)
            for r in self.replace:
                if r in new_url and "fxtwitter.com" not in url and "vxtwitter.com" not in url:
                    new_url = new_url.replace(r, "fxtwitter.com")
                    new_url = new_url.replace("www.", "")
                    if spoiler:
                        new_url = "||" + new_url + "||"
                    log_count += 1
                    new_content += f"{new_url}\n"
                    new_urls.append(new_url)

        if len(urls) > 0:
            await self.log.update(message.guild.id, message.author.id, log_count)
            return new_content, new_urls
        # This is disgusting but it cracks me up
        return False, False

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

