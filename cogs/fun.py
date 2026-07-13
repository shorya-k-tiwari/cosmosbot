# cogs/fun.py — 8ball and Coinflip
import discord
from discord.ext import commands
from discord import app_commands
import random

RESPONSES = [
    '✅ It is certain!',    '✅ Without a doubt!',     '✅ Yes, definitely!',
    '✅ You may rely on it.','✅ As I see it, yes.',    '✅ Most likely.',
    '✅ Outlook good.',      '✅ Signs point to yes.',
    '🤔 Reply hazy, try again.', '🤔 Ask again later.',
    '🤔 Cannot predict now.','🤔 Concentrate and ask again.',
    "❌ Don't count on it.", '❌ My reply is no.',
    '❌ My sources say no.', '❌ Very doubtful.'
]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='8ball')
    async def eightball(self, ctx, *, question: str):
        embed = discord.Embed(title='🎱 Magic 8 Ball', color=discord.Color.dark_purple())
        embed.add_field(name='❓ Question', value=question, inline=False)
        embed.add_field(name='🔮 Answer',   value=random.choice(RESPONSES), inline=False)
        embed.set_footer(text=f'Asked by {ctx.author}')
        await ctx.send(embed=embed)

    @app_commands.command(name='8ball', description='Ask the magic 8 ball')
    @app_commands.describe(question='Your yes/no question')
    async def slash_8ball(self, i: discord.Interaction, question: str):
        embed = discord.Embed(title='🎱 Magic 8 Ball', color=discord.Color.dark_purple())
        embed.add_field(name='❓ Question', value=question, inline=False)
        embed.add_field(name='🔮 Answer',   value=random.choice(RESPONSES), inline=False)
        await i.response.send_message(embed=embed)

    @commands.command(name='coinflip')
    async def coinflip(self, ctx):
        result = random.choice(['🪙 Heads', '🌀 Tails'])
        embed = discord.Embed(title='🪙 Coin Flip!', description=f'The coin landed on **{result}**!', color=discord.Color.gold())
        embed.set_footer(text=f'Flipped by {ctx.author}')
        await ctx.send(embed=embed)

    @app_commands.command(name='coinflip', description='Flip a coin')
    async def slash_coinflip(self, i: discord.Interaction):
        result = random.choice(['🪙 Heads', '🌀 Tails'])
        embed = discord.Embed(title='🪙 Coin Flip!', description=f'The coin landed on **{result}**!', color=discord.Color.gold())
        await i.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))