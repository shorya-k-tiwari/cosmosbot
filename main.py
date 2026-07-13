# main.py — Entry point for CosmosBot
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

COGS = [
    'cogs.moderation',
    'cogs.utility',
    'cogs.fun',
    'cogs.welcome',
    'cogs.ai_chat'
]

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
        try:
            synced = await self.tree.sync()
            print(f'✅ Synced {len(synced)} slash command(s)')
        except Exception as e:
            print(f'❌ Slash sync failed: {e}')

    async def on_ready(self):
        print(f'\n🌌 {self.user.name} is online!')
        print(f'📊 Serving {len(self.guilds)} server(s)\n')
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='Creative Cosmos 🌌 | c!help'
            )
        )

bot = CosmosBot()

# ── Help Command ──────────────────────────────────────────────────────────────
@bot.command(name='help')
async def help_cmd(ctx):
    embed = discord.Embed(
        title='🌌 CosmosBot — Commands',
        description='Prefix: `c!` | Also supports `/` slash commands',
        color=discord.Color.from_rgb(114, 137, 218)
    )
    embed.add_field(name='⚖️ Moderation',
        value='`warn` `kick` `ban` `timeout` `unban` `untimeout`\n`warnings` `clearwarnings` `purge` `lock` `unlock`',
        inline=False)
    embed.add_field(name='🔧 Utility',
        value='`av` `banner` `userinfo` `serverinfo` `afk`',
        inline=False)
    embed.add_field(name='🎮 Fun',
        value='`8ball <question>` `coinflip`',
        inline=False)
    embed.add_field(name='🤖 CosmosAI',
        value='`chat <message>` or just @mention me!',
        inline=False)
    embed.set_footer(text='Made for Creative Cosmos ✨')
    await ctx.send(embed=embed)

# ── Global Error Handler ──────────────────────────────────────────────────────
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('❌ You don\'t have permission for that!')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send('❌ Member not found!')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('❌ Missing an argument! Try `c!help`.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('❌ Invalid argument provided!')
    else:
        print(f'Unhandled error: {error}')

bot.run(os.getenv('DISCORD_TOKEN'))