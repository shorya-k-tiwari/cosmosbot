# cogs/utility.py — Avatar, Banner, UserInfo, ServerInfo, AFK
import discord
from discord.ext import commands
from discord import app_commands
import json, os
from datetime import datetime, timezone

AFK_FILE = 'data/afk.json'

def load_afk():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(AFK_FILE):
        with open(AFK_FILE, 'w') as f:
            json.dump({}, f)
    with open(AFK_FILE) as f:
        return json.load(f)

def save_afk(data):
    with open(AFK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── AVATAR ────────────────────────────────────────────────────────────────
    @commands.command(name='av')
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"🖼️ {member.display_name}'s Avatar", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f'Requested by {ctx.author}')
        await ctx.send(embed=embed)

    @app_commands.command(name='av', description="View a member's avatar")
    @app_commands.describe(member='Leave empty for yourself')
    async def slash_av(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        embed = discord.Embed(title=f"🖼️ {member.display_name}'s Avatar", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await i.response.send_message(embed=embed)

    # ── BANNER ────────────────────────────────────────────────────────────────
    @commands.command(name='banner')
    async def banner(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user = await self.bot.fetch_user(member.id)
        if not user.banner:
            return await ctx.send(f"❌ {member.display_name} doesn't have a profile banner!")
        embed = discord.Embed(title=f"🎨 {member.display_name}'s Banner", color=discord.Color.blurple())
        embed.set_image(url=user.banner.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='banner', description="View a member's profile banner")
    @app_commands.describe(member='Leave empty for yourself')
    async def slash_banner(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        user = await self.bot.fetch_user(member.id)
        if not user.banner:
            return await i.response.send_message(f"❌ {member.display_name} doesn't have a banner!", ephemeral=True)
        embed = discord.Embed(title=f"🎨 {member.display_name}'s Banner", color=discord.Color.blurple())
        embed.set_image(url=user.banner.url)
        await i.response.send_message(embed=embed)

    # ── USERINFO ──────────────────────────────────────────────────────────────
    @commands.command(name='userinfo')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles  = [r.mention for r in reversed(member.roles[1:])]
        status = {
            discord.Status.online:  '🟢 Online',
            discord.Status.idle:    '🟡 Idle',
            discord.Status.dnd:     '🔴 Do Not Disturb',
            discord.Status.offline: '⚫ Offline'
        }.get(member.status, 'Unknown')

        embed = discord.Embed(title=f'👤 {member}', color=member.color, timestamp=datetime.now(timezone.utc))
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='🪪 User ID',         value=member.id, inline=True)
        embed.add_field(name='🤖 Bot?',             value='Yes' if member.bot else 'No', inline=True)
        embed.add_field(name='📡 Status',            value=status, inline=True)
        embed.add_field(name='📅 Account Created',   value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
        embed.add_field(name='📥 Joined Server',     value=f"<t:{int(member.joined_at.timestamp())}:D>" if member.joined_at else 'Unknown', inline=True)
        embed.add_field(name='🎨 Top Role',          value=member.top_role.mention, inline=True)
        embed.add_field(name=f'📛 Roles [{len(roles)}]', value=' '.join(roles[:10]) or 'None', inline=False)
        embed.set_footer(text=f'Requested by {ctx.author}')
        await ctx.send(embed=embed)

    @app_commands.command(name='userinfo', description='View detailed info about a user')
    @app_commands.describe(member='Leave empty for yourself')
    async def slash_userinfo(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        roles  = [r.mention for r in reversed(member.roles[1:])]
        embed  = discord.Embed(title=f'👤 {member}', color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='🪪 User ID',       value=member.id, inline=True)
        embed.add_field(name='📅 Account Created', value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
        embed.add_field(name='📥 Joined Server',  value=f"<t:{int(member.joined_at.timestamp())}:D>" if member.joined_at else 'Unknown', inline=True)
        embed.add_field(name='🎨 Top Role',       value=member.top_role.mention, inline=True)
        embed.add_field(name=f'📛 Roles [{len(roles)}]', value=' '.join(roles[:10]) or 'None', inline=False)
        await i.response.send_message(embed=embed)

    # ── SERVERINFO ────────────────────────────────────────────────────────────
    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        g = ctx.guild
        embed = discord.Embed(
            title=f'🌌 {g.name}',
            description=g.description or 'No description set.',
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc)
        )
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name='🆔 Server ID',    value=g.id, inline=True)
        embed.add_field(name='👑 Owner',         value=g.owner.mention if g.owner else 'Unknown', inline=True)
        embed.add_field(name='👥 Members',       value=g.member_count, inline=True)
        embed.add_field(name='💬 Channels',      value=len(g.channels), inline=True)
        embed.add_field(name='🎭 Roles',         value=len(g.roles), inline=True)
        embed.add_field(name='😀 Emojis',        value=len(g.emojis), inline=True)
        embed.add_field(name='🚀 Boosts',        value=f'{g.premium_subscription_count} (Level {g.premium_tier})', inline=True)
        embed.add_field(name='🔒 Verification',  value=str(g.verification_level).title(), inline=True)
        embed.add_field(name='📅 Created',       value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
        embed.set_footer(text=f'Requested by {ctx.author}')
        await ctx.send(embed=embed)

    @app_commands.command(name='serverinfo', description='View server information')
    async def slash_serverinfo(self, i: discord.Interaction):
        g = i.guild
        embed = discord.Embed(title=f'🌌 {g.name}', description=g.description or 'No description.', color=discord.Color.blurple())
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name='👥 Members',  value=g.member_count, inline=True)
        embed.add_field(name='💬 Channels', value=len(g.channels), inline=True)
        embed.add_field(name='🎭 Roles',    value=len(g.roles), inline=True)
        embed.add_field(name='🚀 Boosts',   value=f'{g.premium_subscription_count} (Level {g.premium_tier})', inline=True)
        embed.add_field(name='📅 Created',  value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
        await i.response.send_message(embed=embed)

    # ── AFK ───────────────────────────────────────────────────────────────────
    @commands.command(name='afk')
    async def afk(self, ctx, *, reason: str = 'AFK'):
        afk = load_afk()
        afk[str(ctx.author.id)] = {'reason': reason, 'time': datetime.now(timezone.utc).isoformat()}
        save_afk(afk)
        embed = discord.Embed(
            title='💤 AFK Set',
            description=f'{ctx.author.mention} is now AFK!\n**Reason:** {reason}',
            color=discord.Color.light_grey()
        )
        await ctx.send(embed=embed)
        try:
            await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
        except: pass

    @app_commands.command(name='afk', description='Set your AFK status')
    @app_commands.describe(reason='Why you are going AFK')
    async def slash_afk(self, i: discord.Interaction, reason: str = 'AFK'):
        afk = load_afk()
        afk[str(i.user.id)] = {'reason': reason, 'time': datetime.now(timezone.utc).isoformat()}
        save_afk(afk)
        embed = discord.Embed(
            title='💤 AFK Set',
            description=f'{i.user.mention} is now AFK!\n**Reason:** {reason}',
            color=discord.Color.light_grey()
        )
        await i.response.send_message(embed=embed)
        try:
            await i.user.edit(nick=f'[AFK] {i.user.display_name}')
        except: pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        afk = load_afk()
        uid = str(message.author.id)

        # Remove AFK when the user talks
        if uid in afk:
            del afk[uid]
            save_afk(afk)
            await message.channel.send(
                f'👋 Welcome back, {message.author.mention}! Your AFK has been removed.',
                delete_after=5
            )
            try:
                nick = message.author.display_name
                if nick.startswith('[AFK] '):
                    await message.author.edit(nick=nick[6:])
            except: pass

        # Notify if a mentioned user is AFK
        for mentioned in message.mentions:
            mid = str(mentioned.id)
            if mid in afk:
                embed = discord.Embed(
                    description=f'💤 {mentioned.mention} is AFK!\n**Reason:** {afk[mid]["reason"]}',
                    color=discord.Color.light_grey()
                )
                await message.channel.send(embed=embed, delete_after=8)

async def setup(bot):
    await bot.add_cog(Utility(bot))