# cogs/moderation.py — Full moderation suite
import discord
from discord.ext import commands
from discord import app_commands
import json, os, re
from datetime import datetime, timezone, timedelta

# Add below imports:
WARN    = discord.Color.from_rgb(230, 175, 50)
KICK    = discord.Color.from_rgb(220, 115, 45)
BAN     = discord.Color.from_rgb(210, 55, 55)
SUCCESS = discord.Color.from_rgb(26, 188, 156)
MUTED   = discord.Color.from_rgb(100, 110, 125)

WARNINGS_FILE = 'data/warnings.json'

# ── Data helpers ──────────────────────────────────────────────────────────────

def load_warnings():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, 'w') as f:
            json.dump({}, f)
    with open(WARNINGS_FILE) as f:
        return json.load(f)

def save_warnings(data):
    with open(WARNINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_duration(s: str):
    """Converts 10s / 10m / 10h / 10d into a timedelta."""
    match = re.match(r'^(\d+)([smhd])$', s.lower())
    if not match:
        return None
    n, u = int(match.group(1)), match.group(2)
    return {'s': timedelta(seconds=n), 'm': timedelta(minutes=n),
            'h': timedelta(hours=n),   'd': timedelta(days=n)}[u]

def mod_embed(title, mod, target, reason, color, duration=None):
    e = discord.Embed(
        title=f'⚖️ {title}',
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name='👤 User',      value=f'{target.mention} (`{target.id}`)', inline=True)
    e.add_field(name='🔨 Moderator', value=mod.mention, inline=True)
    if duration:
        e.add_field(name='⏱️ Duration', value=duration, inline=True)
    e.add_field(name='📝 Reason', value=reason, inline=False)
    e.set_thumbnail(url=target.display_avatar.url)
    return e

# ── Cog ───────────────────────────────────────────────────────────────────────

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def can_act(self, actor: discord.Member, target: discord.Member) -> bool:
        """Returns True if actor outranks target (or is the owner)."""
        if target == target.guild.owner:
            return False  # nobody can act on the owner
        return actor == actor.guild.owner or actor.top_role > target.top_role

    # ── WARN ──────────────────────────────────────────────────────────────────
    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason='No reason provided'):
        if not self.can_act(ctx.author, member):
            return await ctx.send('❌ You cannot warn someone with an equal or higher role!')
        data = load_warnings()
        uid  = str(member.id)
        data.setdefault(uid, []).append({
            'reason': reason, 'mod': str(ctx.author),
            'time': datetime.now(timezone.utc).isoformat()
        })
        save_warnings(data)
        embed = mod_embed('User Warned', ctx.author, member, reason, WARN)
        embed.add_field(name='⚠️ Total Warnings', value=str(len(data[uid])))
        await ctx.send(embed=embed)
        try:
            dm = discord.Embed(title='⚠️ You received a warning',
                               description=f'Server: **{ctx.guild.name}**',
                               color=WARN)
            dm.add_field(name='Reason', value=reason)
            dm.add_field(name='Total Warnings', value=str(len(data[uid])))
            await member.send(embed=dm)
        except: pass

    @app_commands.command(name='warn', description='Warn a member')
    @app_commands.describe(member='Member to warn', reason='Reason for the warning')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_warn(self, i: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
        if not self.can_act(i.user, member):
            return await i.response.send_message('❌ You cannot warn someone with an equal or higher role!', ephemeral=True)
        data = load_warnings()
        uid  = str(member.id)
        data.setdefault(uid, []).append({
            'reason': reason, 'mod': str(i.user),
            'time': datetime.now(timezone.utc).isoformat()
        })
        save_warnings(data)
        embed = mod_embed('User Warned', i.user, member, reason, WARN)
        embed.add_field(name='⚠️ Total Warnings', value=str(len(data[uid])))
        await i.response.send_message(embed=embed)

    # ── KICK ──────────────────────────────────────────────────────────────────
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason='No reason provided'):
        if not self.can_act(ctx.author, member):
            return await ctx.send('❌ You cannot kick someone with an equal or higher role!')
        try:
            dm = discord.Embed(title='👢 You were kicked',
                               description=f'From: **{ctx.guild.name}**',
                               color=discord.Color.orange())
            dm.add_field(name='Reason', value=reason)
            await member.send(embed=dm)
        except: pass
        await member.kick(reason=reason)
        await ctx.send(embed=mod_embed('Member Kicked', ctx.author, member, reason, discord.Color.orange()))

    @app_commands.command(name='kick', description='Kick a member')
    @app_commands.describe(member='Member to kick', reason='Reason')
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, i: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
        if not self.can_act(i.user, member):
            return await i.response.send_message('❌ You cannot kick someone with an equal or higher role!', ephemeral=True)
        try:
            dm = discord.Embed(title='👢 You were kicked',
                               description=f'From: **{i.guild.name}**',
                               color=discord.Color.orange())
            dm.add_field(name='Reason', value=reason)
            await member.send(embed=dm)
        except: pass
        await member.kick(reason=reason)
        await i.response.send_message(embed=mod_embed('Member Kicked', i.user, member, reason, discord.Color.orange()))

    # ── BAN ───────────────────────────────────────────────────────────────────
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason='No reason provided'):
        if not self.can_act(ctx.author, member):
            return await ctx.send('❌ You cannot ban someone with an equal or higher role!')
        try:
            dm = discord.Embed(title='🔨 You were banned',
                               description=f'From: **{ctx.guild.name}**',
                               color=discord.Color.red())
            dm.add_field(name='Reason', value=reason)
            await member.send(embed=dm)
        except: pass
        await member.ban(reason=reason)
        await ctx.send(embed=mod_embed('Member Banned', ctx.author, member, reason, discord.Color.red()))

    @app_commands.command(name='ban', description='Ban a member')
    @app_commands.describe(member='Member to ban', reason='Reason')
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_ban(self, i: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
        if not self.can_act(i.user, member):
            return await i.response.send_message('❌ You cannot ban someone with an equal or higher role!', ephemeral=True)
        try:
            dm = discord.Embed(title='🔨 You were banned',
                               description=f'From: **{i.guild.name}**',
                               color=discord.Color.red())
            dm.add_field(name='Reason', value=reason)
            await member.send(embed=dm)
        except: pass
        await member.ban(reason=reason)
        await i.response.send_message(embed=mod_embed('Member Banned', i.user, member, reason, discord.Color.red()))

    # ── TIMEOUT ───────────────────────────────────────────────────────────────
    @commands.command(name='timeout')
    @commands.has_permissions(moderate_members=True)
    async def timeout_cmd(self, ctx, member: discord.Member, duration: str, *, reason='No reason provided'):
        delta = parse_duration(duration)
        if not delta:
            return await ctx.send('❌ Invalid duration! Use: `10s` `10m` `10h` `10d`')
        if delta.total_seconds() > 28 * 86400:
            return await ctx.send('❌ Maximum timeout is 28 days!')
        if not self.can_act(ctx.author, member):
            return await ctx.send('❌ You cannot timeout someone with an equal or higher role!')
        await member.timeout(discord.utils.utcnow() + delta, reason=reason)
        await ctx.send(embed=mod_embed('Member Timed Out', ctx.author, member, reason, discord.Color.dark_orange(), duration=duration))
        try:
            dm = discord.Embed(title='⏰ You were timed out', color=discord.Color.dark_orange())
            dm.add_field(name='Duration', value=duration)
            dm.add_field(name='Reason', value=reason)
            await member.send(embed=dm)
        except: pass

    @app_commands.command(name='timeout', description='Timeout a member')
    @app_commands.describe(member='Member to timeout', duration='Duration (10s / 10m / 10h / 10d)', reason='Reason')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def slash_timeout(self, i: discord.Interaction, member: discord.Member, duration: str, reason: str = 'No reason provided'):
        delta = parse_duration(duration)
        if not delta:
            return await i.response.send_message('❌ Invalid duration! Use: `10s` `10m` `10h` `10d`', ephemeral=True)
        if delta.total_seconds() > 28 * 86400:
            return await i.response.send_message('❌ Maximum timeout is 28 days!', ephemeral=True)
        if not self.can_act(i.user, member):
            return await i.response.send_message('❌ You cannot timeout someone with an equal or higher role!', ephemeral=True)
        await member.timeout(discord.utils.utcnow() + delta, reason=reason)
        await i.response.send_message(embed=mod_embed('Member Timed Out', i.user, member, reason, discord.Color.dark_orange(), duration=duration))

    # ── UNTIMEOUT ─────────────────────────────────────────────────────────────
    @commands.command(name='untimeout')
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(embed=discord.Embed(
            title='✅ Timeout Removed',
            description=f"{member.mention}'s timeout has been removed.",
            color=discord.Color.green()
        ))

    @app_commands.command(name='untimeout', description='Remove a timeout from a member')
    @app_commands.describe(member='Member to un-timeout')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def slash_untimeout(self, i: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await i.response.send_message(embed=discord.Embed(
            title='✅ Timeout Removed',
            description=f"{member.mention}'s timeout has been removed.",
            color=discord.Color.green()
        ))

    # ── UNBAN ─────────────────────────────────────────────────────────────────
    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(embed=discord.Embed(
                title='✅ User Unbanned',
                description=f'**{user}** has been unbanned.',
                color=discord.Color.green()
            ))
        except discord.NotFound:
            await ctx.send('❌ User not found or is not banned!')

    @app_commands.command(name='unban', description='Unban a user by their ID')
    @app_commands.describe(user_id='The User ID to unban')
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_unban(self, i: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await i.guild.unban(user)
            await i.response.send_message(embed=discord.Embed(
                title='✅ User Unbanned',
                description=f'**{user}** has been unbanned.',
                color=discord.Color.green()
            ))
        except:
            await i.response.send_message('❌ User not found or not banned!', ephemeral=True)

    # ── WARNINGS ──────────────────────────────────────────────────────────────
    @commands.command(name='warnings')
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        warns = load_warnings().get(str(member.id), [])
        if not warns:
            return await ctx.send(f'✅ {member.mention} has no warnings.')
        embed = discord.Embed(title=f'⚠️ Warnings — {member.display_name}', color=WARN)
        embed.set_thumbnail(url=member.display_avatar.url)
        for idx, w in enumerate(warns, 1):
            embed.add_field(name=f'Warning #{idx}',
                value=f"**Reason:** {w['reason']}\n**By:** {w['mod']}\n**Date:** {w['time'][:10]}",
                inline=False)
        embed.set_footer(text=f'Total: {len(warns)} warning(s)')
        await ctx.send(embed=embed)

    @app_commands.command(name='warnings', description='View warnings for a member')
    @app_commands.describe(member='Member to check')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_warnings(self, i: discord.Interaction, member: discord.Member):
        warns = load_warnings().get(str(member.id), [])
        if not warns:
            return await i.response.send_message(f'✅ {member.mention} has no warnings.', ephemeral=True)
        embed = discord.Embed(title=f'⚠️ Warnings — {member.display_name}', color=WARN)
        for idx, w in enumerate(warns, 1):
            embed.add_field(name=f'Warning #{idx}',
                value=f"**Reason:** {w['reason']}\n**By:** {w['mod']}\n**Date:** {w['time'][:10]}",
                inline=False)
        embed.set_footer(text=f'Total: {len(warns)} warning(s)')
        await i.response.send_message(embed=embed, ephemeral=True)

    # ── CLEARWARNINGS ─────────────────────────────────────────────────────────
    @commands.command(name='clearwarnings')
    @commands.has_permissions(manage_guild=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        data = load_warnings()
        data[str(member.id)] = []
        save_warnings(data)
        await ctx.send(embed=discord.Embed(
            title='✅ Warnings Cleared',
            description=f'All warnings for {member.mention} have been cleared.',
            color=discord.Color.green()
        ))

    @app_commands.command(name='clearwarnings', description='Clear all warnings for a member')
    @app_commands.describe(member='Member to clear')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_clearwarnings(self, i: discord.Interaction, member: discord.Member):
        data = load_warnings()
        data[str(member.id)] = []
        save_warnings(data)
        await i.response.send_message(embed=discord.Embed(
            title='✅ Warnings Cleared',
            description=f'All warnings for {member.mention} have been cleared.',
            color=discord.Color.green()
        ))

    # ── PURGE ─────────────────────────────────────────────────────────────────
    @commands.command(name='purge')
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if not 1 <= amount <= 100:
            return await ctx.send('❌ Amount must be between 1 and 100!')
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'✅ Deleted **{len(deleted) - 1}** messages!', delete_after=4)

    @app_commands.command(name='purge', description='Bulk delete messages (1–100)')
    @app_commands.describe(amount='Number of messages to delete')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_purge(self, i: discord.Interaction, amount: int):
        if not 1 <= amount <= 100:
            return await i.response.send_message('❌ Amount must be between 1 and 100!', ephemeral=True)
        await i.response.send_message('🗑️ Purging...', ephemeral=True)
        deleted = await i.channel.purge(limit=amount)
        await i.edit_original_response(content=f'✅ Deleted **{len(deleted)}** messages!')

    # ── LOCK ──────────────────────────────────────────────────────────────────
    @commands.command(name='lock')
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        ow = ctx.channel.overwrites_for(ctx.guild.default_role)
        ow.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=ow)
        await ctx.send(embed=discord.Embed(
            title='🔒 Channel Locked',
            description=f'{ctx.channel.mention} has been locked.',
            color=discord.Color.red()
        ))

    @app_commands.command(name='lock', description='Lock the current channel')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_lock(self, i: discord.Interaction):
        ow = i.channel.overwrites_for(i.guild.default_role)
        ow.send_messages = False
        await i.channel.set_permissions(i.guild.default_role, overwrite=ow)
        await i.response.send_message(embed=discord.Embed(
            title='🔒 Channel Locked',
            description=f'{i.channel.mention} has been locked.',
            color=discord.Color.red()
        ))

    # ── UNLOCK ────────────────────────────────────────────────────────────────
    @commands.command(name='unlock')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        ow = ctx.channel.overwrites_for(ctx.guild.default_role)
        ow.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=ow)
        await ctx.send(embed=discord.Embed(
            title='🔓 Channel Unlocked',
            description=f'{ctx.channel.mention} has been unlocked.',
            color=discord.Color.green()
        ))

    @app_commands.command(name='unlock', description='Unlock the current channel')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_unlock(self, i: discord.Interaction):
        ow = i.channel.overwrites_for(i.guild.default_role)
        ow.send_messages = True
        await i.channel.set_permissions(i.guild.default_role, overwrite=ow)
        await i.response.send_message(embed=discord.Embed(
            title='🔓 Channel Unlocked',
            description=f'{i.channel.mention} has been unlocked.',
            color=discord.Color.green()
        ))

async def setup(bot):
    await bot.add_cog(Moderation(bot))