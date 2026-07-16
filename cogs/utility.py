# cogs/utility.py
import discord
from discord.ext import commands
from discord import app_commands
import json, os
from datetime import datetime, timezone

AFK_FILE = 'data/afk.json'

OCEAN   = discord.Color.from_rgb(0, 180, 216)
SUCCESS = discord.Color.from_rgb(26, 188, 156)
MUTED   = discord.Color.from_rgb(140, 148, 160)

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
        embed = discord.Embed(title=f'{member.display_name} — Avatar', color=OCEAN)
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f'Requested by {ctx.author.display_name}',
                         icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='av', description="View a member's avatar")
    @app_commands.describe(member='Leave blank for yourself')
    async def slash_av(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        embed = discord.Embed(title=f'{member.display_name} — Avatar', color=OCEAN)
        embed.set_image(url=member.display_avatar.url)
        await i.response.send_message(embed=embed)

    # ── BANNER ────────────────────────────────────────────────────────────────
    @commands.command(name='banner')
    async def banner(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user = await self.bot.fetch_user(member.id)
        if not user.banner:
            return await ctx.send(f'❌ **{member.display_name}** has no profile banner.')
        embed = discord.Embed(title=f'{member.display_name} — Banner', color=OCEAN)
        embed.set_image(url=user.banner.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='banner', description="View a member's profile banner")
    @app_commands.describe(member='Leave blank for yourself')
    async def slash_banner(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        user = await self.bot.fetch_user(member.id)
        if not user.banner:
            return await i.response.send_message(
                f'❌ **{member.display_name}** has no profile banner.', ephemeral=True)
        embed = discord.Embed(title=f'{member.display_name} — Banner', color=OCEAN)
        embed.set_image(url=user.banner.url)
        await i.response.send_message(embed=embed)

    # ── USERINFO ──────────────────────────────────────────────────────────────
    @commands.command(name='userinfo')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles  = [r.mention for r in reversed(member.roles[1:])]

        # Works correctly now that intents.presences = True is set
        status = {
            discord.Status.online:  '🟢 Online',
            discord.Status.idle:    '🟡 Idle',
            discord.Status.dnd:     '🔴 Do Not Disturb',
            discord.Status.offline: '⚫ Offline',
        }.get(member.status, '⚫ Offline')

        color = member.color if str(member.color) != '#000000' else OCEAN
        embed = discord.Embed(
            title=str(member),
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='User ID',        value=f'`{member.id}`', inline=True)
        embed.add_field(name='Bot?',            value='Yes' if member.bot else 'No', inline=True)
        embed.add_field(name='Status',          value=status, inline=True)
        embed.add_field(name='Account Created',
            value=f"<t:{int(member.created_at.timestamp())}:D> (<t:{int(member.created_at.timestamp())}:R>)",
            inline=False)
        embed.add_field(name='Joined Server',
            value=f"<t:{int(member.joined_at.timestamp())}:D> (<t:{int(member.joined_at.timestamp())}:R>)"
            if member.joined_at else 'Unknown', inline=False)
        embed.add_field(name='Top Role',        value=member.top_role.mention, inline=True)
        embed.add_field(name=f'Roles ({len(roles)})',
            value=' '.join(roles[:12]) if roles else '—', inline=False)
        embed.set_footer(text=f'Requested by {ctx.author.display_name}',
                         icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='userinfo', description='View detailed info about a member')
    @app_commands.describe(member='Leave blank for yourself')
    async def slash_userinfo(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        roles  = [r.mention for r in reversed(member.roles[1:])]
        color  = member.color if str(member.color) != '#000000' else OCEAN
        embed  = discord.Embed(title=str(member), color=color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='User ID',        value=f'`{member.id}`', inline=True)
        embed.add_field(name='Account Created',
            value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
        embed.add_field(name='Joined Server',
            value=f"<t:{int(member.joined_at.timestamp())}:D>" if member.joined_at else 'Unknown',
            inline=True)
        embed.add_field(name='Top Role',        value=member.top_role.mention, inline=True)
        embed.add_field(name=f'Roles ({len(roles)})',
            value=' '.join(roles[:12]) if roles else '—', inline=False)
        await i.response.send_message(embed=embed)

    # ── SERVERINFO ────────────────────────────────────────────────────────────
    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        g = ctx.guild
        embed = discord.Embed(
            title=g.name,
            description=g.description or '*No description set.*',
            color=OCEAN,
            timestamp=datetime.now(timezone.utc)
        )
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name='Server ID',    value=f'`{g.id}`', inline=True)
        embed.add_field(name='Owner',        value=g.owner.mention if g.owner else '—', inline=True)
        embed.add_field(name='Members',      value=f'`{g.member_count}`', inline=True)
        embed.add_field(name='Channels',     value=f'`{len(g.channels)}`', inline=True)
        embed.add_field(name='Roles',        value=f'`{len(g.roles)}`', inline=True)
        embed.add_field(name='Emojis',       value=f'`{len(g.emojis)}`', inline=True)
        embed.add_field(name='Boosts',
            value=f'`{g.premium_subscription_count}` — Level `{g.premium_tier}`', inline=True)
        embed.add_field(name='Verification', value=str(g.verification_level).title(), inline=True)
        embed.add_field(name='Created',      value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
        embed.set_footer(text=f'Requested by {ctx.author.display_name}',
                         icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='serverinfo', description='View server information')
    async def slash_serverinfo(self, i: discord.Interaction):
        g = i.guild
        embed = discord.Embed(title=g.name, description=g.description or '*No description.*', color=OCEAN)
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name='Members',  value=f'`{g.member_count}`', inline=True)
        embed.add_field(name='Channels', value=f'`{len(g.channels)}`', inline=True)
        embed.add_field(name='Roles',    value=f'`{len(g.roles)}`', inline=True)
        embed.add_field(name='Boosts',
            value=f'`{g.premium_subscription_count}` (Level {g.premium_tier})', inline=True)
        embed.add_field(name='Created',  value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
        await i.response.send_message(embed=embed)

    # ── AFK ───────────────────────────────────────────────────────────────────
    @commands.command(name='afk')
    async def afk(self, ctx, *, reason: str = 'AFK'):
        afk = load_afk()
        afk[str(ctx.author.id)] = {
            'reason': reason,
            'time': datetime.now(timezone.utc).isoformat()
        }
        save_afk(afk)
        embed = discord.Embed(
            description=f'💤 {ctx.author.mention} is now AFK — **{reason}**',
            color=MUTED
        )
        await ctx.send(embed=embed)
        try:
            await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
        except:
            pass

    @app_commands.command(name='afk', description='Set your AFK status')
    @app_commands.describe(reason='Why are you going AFK?')
    async def slash_afk(self, i: discord.Interaction, reason: str = 'AFK'):
        afk = load_afk()
        afk[str(i.user.id)] = {
            'reason': reason,
            'time': datetime.now(timezone.utc).isoformat()
        }
        save_afk(afk)
        embed = discord.Embed(
            description=f'💤 {i.user.mention} is now AFK — **{reason}**',
            color=MUTED
        )
        await i.response.send_message(embed=embed)
        try:
            await i.user.edit(nick=f'[AFK] {i.user.display_name}')
        except:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        afk = load_afk()
        uid = str(message.author.id)

        # FIX #3: Only remove AFK if this is a real message, NOT the c!afk command itself
        if uid in afk and not message.content.lower().startswith('c!afk'):
            del afk[uid]
            save_afk(afk)
            # ← No delete_after — message stays permanently
            await message.channel.send(
                f'👋 Welcome back, {message.author.mention}! Your AFK has been removed.'
            )
            try:
                nick = message.author.display_name
                if nick.startswith('[AFK] '):
                    await message.author.edit(nick=nick[6:])
            except:
                pass

        # Notify when someone pings an AFK user
        for mentioned in message.mentions:
            mid = str(mentioned.id)
            if mid in afk:
                embed = discord.Embed(
                    description=f'💤 **{mentioned.display_name}** is AFK\n**Reason:** {afk[mid]["reason"]}',
                    color=MUTED
                )
                # ← No delete_after — message stays permanently
                await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))