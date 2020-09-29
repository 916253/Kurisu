import datetime
import discord
import inspect
import os
import random
import re
import string
import sys

from utils.checks import is_staff
from discord.ext import commands
from discord import TextChannel, __version__ as discordpy_version

python_version = sys.version.split()[0]


class Extras(commands.Cog):
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        self.nick_pattern = re.compile("^[a-z]{2,}.*$", re.RegexFlag.IGNORECASE)

    prune_key = "nokey"

    def check_nickname(self, nickname):
        if match := self.nick_pattern.fullmatch(nickname):
            return len(nickname) <= 32
        else:
            return match

    @is_staff("SuperOP")
    @commands.command(hidden=True)
    async def env(self, ctx):
        msg = f'''
        Python {python_version}
        discord.py {discordpy_version}
        Is Docker: {bool(self.bot.IS_DOCKER)}
        Commit: {self.bot.commit}
        Branch: {self.bot.branch}
        '''
        await ctx.send(inspect.cleandoc(msg))

    @commands.command(aliases=['about'])
    async def kurisu(self, ctx):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="Maintained by Nintendo Homebrew helpers and staff")
        embed.set_thumbnail(url="http://i.imgur.com/hjVY4Et.jpg")
        embed.url = "https://github.com/nh-server/Kurisu"
        embed.description = "Kurisu, the Nintendo Homebrew Discord bot!"
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def membercount(self, ctx):
        """Prints the member count of the server."""
        await ctx.send(f"{ctx.guild.name} has {ctx.guild.member_count:,} members!")

    @commands.command()
    async def uptime(self, ctx):
        """Print total uptime of the bot."""
        await ctx.send(f"Uptime: {datetime.datetime.now() - self.bot.startup}")

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command(hidden=True)
    async def copyrole(self, ctx, role: discord.Role, src_channel: discord.TextChannel, des_channels: commands.Greedy[discord.TextChannel]):
        """Copy role permission from a channel to channels"""
        perms = src_channel.overwrites_for(role)
        for c in des_channels:
            await c.set_permissions(role, overwrite=perms)
        await ctx.send("Changed permissions successfully")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def userroles(self, ctx, u: discord.Member = None):
        """Gets user roles and their id. Staff only."""
        if not u:
            u = ctx.author
        msg = f"{u}'s Roles:\n\n"
        for role in u.roles:
            if role.is_default():
                continue
            msg += f"{role} = {role.id}\n"
        await ctx.author.send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def serverroles(self, ctx, exp: str):
        """Gets the server roles and their id by regex. Staff only."""
        msg = f"Server roles matching `{exp}`:\n\n"
        for role in ctx.guild.roles:
            if bool(re.search(exp, role.name, re.IGNORECASE)):
                msg += f"{role.name} = {role.id}\n"
        await ctx.author.send(msg)

    @is_staff("OP")
    @commands.command(hidden=True)
    async def embedtext(self, ctx, *, text):
        """Embed content."""
        await ctx.send(embed=discord.Embed(description=text))

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def estprune(self, ctx, days=30):
        """Estimate count of members that would be pruned based on the amount of days. Staff only."""
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return

        msg = await ctx.send("I'm figuring this out!")
        async with ctx.channel.typing():
            count = await ctx.guild.estimate_pruned_members(days=days)
            await msg.edit(content=f"{count:,} members inactive for {days} day(s) would be kicked from {ctx.guild.name}!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def activecount(self, ctx, days=30):
        """Shows the number of members active in the past amount of days. Staff only."""
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return
        msg = await ctx.send("I'm figuring this out!")
        async with ctx.channel.typing():
            count = await ctx.guild.estimate_pruned_members(days=days)
            if days == 1:
                await msg.edit(content=f"{ctx.guild.member_count - count:,} members were active today in {ctx.guild.name}!")
            else:
                await msg.edit(content=f"{ctx.guild.member_count - count:,} members were active in the past {days} days in {ctx.guild.name}!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def prune30(self, ctx, key=""):
        """Prune members that are inactive for 30 days. Staff only."""
        if self.bot.pruning > 0:
            await ctx.send("Pruning is already in progress.")
            return
        if key != self.prune_key:
            if key != "":
                await ctx.send("That's not the correct key.")
            self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
            await ctx.send(
                f"Are you sure you want to prune members inactive for 30 days?\nTo see how many members get kicked, use `.estprune`.\nTo confirm the prune, use the command `.prune30 {self.prune_key}`.")
            return
        self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
        await ctx.send("Starting pruning!")
        count = await ctx.guild.prune_members(days=30)
        self.bot.pruning = count
        await self.bot.channels['mods'].send(f"{count:,} are currently being kicked from {ctx.guild.name}!")
        msg = f"👢 **Prune**: {ctx.author.mention} pruned {count:,} members"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def disableleavelogs(self, ctx):
        """DEBUG COMMAND"""
        self.bot.pruning = True
        await ctx.send("disable")

    @is_staff("HalfOP")
    @commands.command()
    async def enableleavelogs(self, ctx):
        """DEBUG COMMAND"""
        self.bot.pruning = False
        await ctx.send("enable")

    @commands.command(name="32c3")
    async def _32c3(self, ctx):
        """Console Hacking 2015"""
        await ctx.send("https://www.youtube.com/watch?v=bZczf57HSag")

    @commands.command(name="33c3")
    async def _33c3(self, ctx):
        """Nintendo Hacking 2016"""
        await ctx.send("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @commands.command(name="34c3")
    async def _34c3(self, ctx):
        """Console Security - Switch"""
        await ctx.send("https://www.youtube.com/watch?v=Ec4NgWRE8ik")

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def dumpchannel(self, ctx, channel: TextChannel, limit=100):
        """Dump 100 messages from a channel to a file."""
        await ctx.send(f"Dumping {limit} messages from {channel.mention}")
        os.makedirs(f"#{channel.name}-{channel.id}", exist_ok=True)
        async for message in channel.history(limit=limit):
            with open(f"#{channel.name}-{channel.id}/{message.id}.txt", "w") as f:
                f.write(message.content)
        await ctx.send("Done!")
        
    @commands.guild_only()
    @commands.command(hidden=True)
    async def togglechannel(self, ctx, channelname):
        """Enable or disable access to specific channels."""
        await ctx.message.delete()
        author = ctx.author
        if ctx.channel != self.bot.channels['bot-cmds']:
            return await ctx.send(f"{ctx.author.mention}: .togglechannel can only be used in <#261581918653513729>.", delete_after=10)
        try:
            if channelname == "elsewhere":
                if self.bot.roles['#elsewhere'] in author.roles:
                    await author.remove_roles(self.bot.roles['#elsewhere'])
                    await author.send("Access to #elsewhere removed.")
                elif self.bot.roles['No-elsewhere'] not in author.roles:
                    await author.add_roles(self.bot.roles['#elsewhere'])
                    await author.send("Access to #elsewhere granted.")
                else:
                    await author.send("Your access to elsewhere is restricted, contact staff to remove it.")
            elif channelname == "artswhere":
                if self.bot.roles['#art-discussion'] in author.roles:
                    await author.remove_roles(self.bot.roles['#art-discussion'])
                    await author.send("Access to #art-discussion removed.")
                elif self.bot.roles['No-art'] not in author.roles:
                    await author.add_roles(self.bot.roles['#art-discussion'])
                    await author.send("Access to #art-discussion granted.")
                else:
                    await author.send("Your access to #art-discussion is restricted, contact staff to remove it.")
            else:
                await author.send(f"{channelname} is not a valid toggleable channel.")
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @commands.dm_only()
    @commands.cooldown(rate=1, per=21600.0, type=commands.BucketType.member)
    @commands.command()
    async def nickme(self, ctx, *, nickname):
        """Change your nickname. Nitro Booster and crc only. Works only in DMs. 6 Hours Cooldown."""
        member = self.bot.guild.get_member(ctx.author.id)
        if self.bot.roles['crc'] not in member.roles and self.bot.roles['Nitro Booster'] not in member.roles:
            return await ctx.send("This command can only be used by Nitro Boosters and members of crc!")
        if self.check_nickname(nickname):
            try:
                await member.edit(nick=nickname)
                await ctx.send(f"Your nickname is now `{nickname}`!")
            except discord.errors.Forbidden:
                await ctx.send("💢  I can't change your nickname! (Permission Error)")
        else:
            await ctx.send("The nickname doesn't comply with our nickname policy or it's too long!")
            ctx.command.reset_cooldown(ctx)


def setup(bot):
    bot.add_cog(Extras(bot))
