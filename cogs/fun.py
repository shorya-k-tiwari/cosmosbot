# cogs/fun.py
import discord
from discord.ext import commands
from discord import app_commands
import random

OCEAN   = discord.Color.from_rgb(0, 180, 216)
SUCCESS = discord.Color.from_rgb(26, 188, 156)
DANGER  = discord.Color.from_rgb(231, 76, 60)
PURPLE  = discord.Color.from_rgb(60, 40, 100)

EIGHT_BALL = [
    '✅ It is certain.',     '✅ Without a doubt.',    '✅ Yes, definitely.',
    '✅ You may rely on it.','✅ As I see it, yes.',   '✅ Most likely.',
    '✅ Outlook good.',      '✅ Signs point to yes.',
    '🤔 Reply hazy, try again.','🤔 Ask again later.',
    '🤔 Cannot predict now.','🤔 Better not tell you now.',
    '❌ Don\'t count on it.','❌ My reply is no.',
    '❌ My sources say no.', '❌ Very doubtful.'
]

WIN_LINES  = [
    'Luck is on your side today! 🌊',
    'The cosmos favours you. ✨',
    'Absolute menace. You called it. 👑',
    'Bro predicted it fr fr 🔮',
]
LOSE_LINES = [
    'Rough seas ahead. Better luck next time 🌊',
    'The coin had other plans...',
    'Not your day, bestie 💀',
    'The cosmos is not impressed rn 😭',
]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── 8BALL ─────────────────────────────────────────────────────────────────
    @commands.command(name='8ball')
    async def eightball(self, ctx, *, question: str):
        embed = discord.Embed(title='🎱 Magic 8 Ball', color=PURPLE)
        embed.add_field(name='Question', value=question, inline=False)
        embed.add_field(name='Answer',   value=random.choice(EIGHT_BALL), inline=False)
        embed.set_footer(text=f'Asked by {ctx.author.display_name}',
                         icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='8ball', description='Ask the magic 8 ball')
    @app_commands.describe(question='Your yes/no question')
    async def slash_8ball(self, i: discord.Interaction, question: str):
        embed = discord.Embed(title='🎱 Magic 8 Ball', color=PURPLE)
        embed.add_field(name='Question', value=question, inline=False)
        embed.add_field(name='Answer',   value=random.choice(EIGHT_BALL), inline=False)
        await i.response.send_message(embed=embed)

    # ── COINFLIP — FIX #4: now an actual game ─────────────────────────────────
    @commands.command(name='coinflip')
    async def coinflip(self, ctx, bet: str = None):
        if not bet:
            return await ctx.send(
                '🪙 **Coinflip** — make a bet first!\n'
                'Usage: `c!coinflip heads` or `c!coinflip tails`'
            )
        bet = bet.lower()
        if bet not in ('heads', 'tails'):
            return await ctx.send('❌ Invalid bet! Choose `heads` or `tails`.')

        result = random.choice(['heads', 'tails'])
        won    = (bet == result)
        coin   = '🪙' if result == 'heads' else '🌀'

        embed = discord.Embed(
            title='🎉 You Won!' if won else '💀 You Lost.',
            color=SUCCESS if won else DANGER
        )
        embed.add_field(name='Your Bet', value=bet.title(), inline=True)
        embed.add_field(name=f'{coin} Result', value=result.title(), inline=True)
        embed.add_field(name='—',
            value=f'*{random.choice(WIN_LINES if won else LOSE_LINES)}*',
            inline=False)
        embed.set_footer(text=f'Flipped by {ctx.author.display_name}',
                         icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='coinflip', description='Bet on heads or tails')
    @app_commands.describe(bet='heads or tails')
    async def slash_coinflip(self, i: discord.Interaction, bet: str):
        bet = bet.lower()
        if bet not in ('heads', 'tails'):
            return await i.response.send_message(
                '❌ Invalid bet! Choose `heads` or `tails`.', ephemeral=True)
        result = random.choice(['heads', 'tails'])
        won    = (bet == result)
        coin   = '🪙' if result == 'heads' else '🌀'
        embed  = discord.Embed(
            title='🎉 You Won!' if won else '💀 You Lost.',
            color=SUCCESS if won else DANGER
        )
        embed.add_field(name='Your Bet', value=bet.title(), inline=True)
        embed.add_field(name=f'{coin} Result', value=result.title(), inline=True)
        embed.add_field(name='—',
            value=f'*{random.choice(WIN_LINES if won else LOSE_LINES)}*',
            inline=False)
        await i.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))