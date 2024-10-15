import discord
from discord.ext import commands
import os

pbws = 0.95
class Osu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_command(name="bwsall", with_app_command=True, description="Get the BWS rank and PBWS rank of an osu! player.")
    async def bwsall(self, ctx, username: str, badges: int, pbadges: int):
        player = getPbws(username, badges, pbadges)
        aa = bytes("aaa", "utf-8")
        type(aa)
        aa.decode()
        if player is None:
            return await ctx.send("Error fetching data, please check username.")
        embed = discord.Embed(title=f"{player.getName()} | #{player.rank} | {player.country}", color=0xFF66AA, description="PBWS is a modified version of BWS for ANZT11S "
                                                                                       "that additionally boosts 'prestigious' badges, "
                                                                                       "which are badges from tournaments where "
                                                                                       "the top 3 players receive badge, such as OWC or Corsace.\n\n"
                                                                                       f"Formula: *rank^(0.9937^(badges^2))^{pbws}^(prestigious badges^2)*\n"
                                                                                       "PBWS is currently a work in progress.\n")
        embed.add_field(name="BWS Rank", value=f"{player.bws}", inline=True)
        embed.add_field(name="PBWS Rank", value=f"{player.pbws}", inline=True)
        embed.add_field(name="Badges", value=f"{player.badges} badges ({player.pbadges} prestigious)", inline=True)
        embed.add_field(name="Rank > BWS", value=f"{round((player.rank - player.bws) / player.rank * 100, 2)}%", inline=True)
        embed.add_field(name="Rank > PBWS", value=f"{round((player.rank - player.pbws) / player.rank * 100, 2)}%", inline=True)
        embed.add_field(name="BWS > PBWS", value=f"{round((player.bws - player.pbws) / player.bws * 100, 2)}%", inline=True)
        embed.set_thumbnail(url=f"https://a.ppy.sh/{player.getId()}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="setpbws", with_app_command=True, description="Set the PBWS rate.")
    async def setpbws(self, ctx, rate: float):
        if ctx.channel.id in [1189065518410387587, 857250159233335306]:
            global pbws
            pbws = rate
            await ctx.send(f"PBWS rate set to {pbws}.")
            return
        await ctx.send("This command must be used in the pbws staff channel.")

from util import osuapi

api = osuapi.OsuApi()

class OsuPlayerPBWS(osuapi.OsuPlayer):
    def __init__(self, data: []):
        super().__init__(data)
        self.bws = 0
        self.pbws = 0

    def setBwsAll(self):
        self.bws = round(self.rank**(0.9937**(self.badges**2)), 0)
        self.pbws = round((self.rank**0.9937**(self.badges**2))**pbws**(self.pbadges**2), 0)

def getPbws(username: str, badges: int, pbadges: int):
    playerdata = api.getPlayer(username)
    player = OsuPlayerPBWS(playerdata)
    if player is None:
        return None
    player.setBadgesAll(badges, pbadges)
    player.setBwsAll()
    return player

async def setup(bot):
    # take name of class, pass in the bot
    await bot.add_cog(Osu(bot))