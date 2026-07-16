# cogs/events.py — Ping reactions for server owners
import discord
from discord.ext import commands

# ╔═══════════════════════════════════════════════════════════════════╗
# ║  FILL THIS IN before running                                     ║
# ║                                                                  ║
# ║  How to get a User ID:                                          ║
# ║    Discord Settings → Advanced → Developer Mode ON              ║
# ║    Right-click a user → Copy User ID                           ║
# ║                                                                  ║
# ║  How to get an emoji name:                                      ║
# ║    In Discord, type  \:your_emoji:  and send it               ║
# ║    It shows something like  <:wavey:123456789>                 ║
# ║    The name is the part between colons → wavey                 ║
# ╚═══════════════════════════════════════════════════════════════════╝

OWNER_REACTIONS = {
    '943510541794672723':  'happy_dance',   # e.g. '123456789012345678': 'shorya_crown'
    '1279396950638071840':    'bear_heart',   # e.g. '987654321098765432': 'cora_sparkle'
}


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.mentions:
            return

        mentioned_ids = {str(m.id) for m in message.mentions}

        for user_id, emoji_name in OWNER_REACTIONS.items():
            if user_id in mentioned_ids:
                emoji = discord.utils.get(message.guild.emojis, name=emoji_name)
                if emoji:
                    try:
                        await message.add_reaction(emoji)
                    except discord.Forbidden:
                        print(f'Missing permission to react in #{message.channel.name}')
                    except Exception as e:
                        print(f'Reaction error: {e}')


async def setup(bot):
    await bot.add_cog(Events(bot))