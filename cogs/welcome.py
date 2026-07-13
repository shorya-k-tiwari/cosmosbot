# cogs/welcome.py — Welcome message on member join
import discord
from discord.ext import commands

# ⚠️  CHANGE THESE TWO LINES:
WELCOME_CHANNEL_ID = 1440748203799613491   # Right-click your channel → Copy Channel ID
WELCOME_GIF        = 'https://cdn.discordapp.com/attachments/1412543402255581414/1473605308298301581/standard_13.gif'

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        count  = member.guild.member_count
        suffix = 'th'
        if count % 100 not in (11, 12, 13):
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(count % 10, 'th')

        embed = discord.Embed(
            title='🌌 Welcome to Creative Cosmos!',
            description=(
                f'Hey {member.mention}, we\'re so glad you\'re here! 🎉\n\n'
                f'You are our **{count}{suffix} member!**\n\n'
                f'📖 Read the rules and enjoy your time in the cosmos! ✨'
            ),
            color=discord.Color.from_rgb(114, 137, 218)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=WELCOME_GIF)
        embed.set_footer(
            text=f'✨ Creative Cosmos • {count} members',
            icon_url=member.guild.icon.url if member.guild.icon else None
        )
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))