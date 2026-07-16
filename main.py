# main.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

GUILD_ID = int(os.getenv('GUILD_ID', 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members        = True
intents.presences      = True   # ← FIX #2: this is what makes status work

COGS = [
    'cogs.moderation',
    'cogs.utility',
    'cogs.fun',
    'cogs.welcome',
    'cogs.ai_chat',
    'cogs.events',   # ← NEW
]

OCEAN = discord.Color.from_rgb(0, 180, 216)

class CosmosBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='c!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f'✅ Loaded → {cog}')
            except Exception as e:
                print(f'❌ Failed → {cog}: {e}')

        # FIX #1: sync to your specific guild = instant slash commands
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f'✅ Synced {len(synced)} slash command(s) — instant')
        else:
            synced = await self.tree.sync()
            print(f'✅ Synced {len(synced)} slash command(s) — global (up to 1hr)')

    async def on_ready(self):
        print(f'\n🌊 {self.user.name} is online!')
        print(f'📊 Serving {len(self.guilds)} server(s)\n')
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='Creative Cosmos 🌊 | c!help'
            )
        )

bot = CosmosBot()

# ── Owner: Force re-sync slash commands ───────────────────────────────────────
@bot.command(name='sync')
@commands.is_owner()
async def sync_cmd(ctx):
    guild = discord.Object(id=ctx.guild.id)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    await ctx.send(f'✅ Synced **{len(synced)}** slash commands to this server.')

# ── Help ──────────────────────────────────────────────────────────────────────
@bot.command(name='help')
async def help_cmd(ctx):
    embed = discord.Embed(
        title='🌊 CosmosBot',
        description='> **Prefix:** `c!`  ·  **Slash:** type `/`',
        color=OCEAN
    )
    embed.add_field(name='⚖️ Moderation',
        value='`warn` `kick` `ban` `timeout` `unban` `untimeout`\n`warnings` `clearwarnings` `purge` `lock` `unlock`',
        inline=False)
    embed.add_field(name='🔧 Utility',
        value='`av` `banner` `userinfo` `serverinfo` `afk`',
        inline=False)
    embed.add_field(name='🎮 Fun',
        value='`coinflip <heads/tails>`  ·  `8ball <question>`',
        inline=False)
    embed.add_field(name='🤖 CosmosAI',
        value='Chat in **#cosmos-ai** — or use `/chat` there',
        inline=False)
    embed.set_footer(
        text='Creative Cosmos',
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )
    await ctx.send(embed=embed)

# ── Global error handler ──────────────────────────────────────────────────────
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('❌ You don\'t have permission for that.')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send('❌ Member not found.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('❌ Missing an argument — try `c!help`.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('❌ Invalid argument.')
    elif isinstance(error, commands.NotOwner):
        await ctx.send('❌ Owner only.')
    else:
        print(f'Unhandled error: {error}')

bot.run(os.getenv('DISCORD_TOKEN'))