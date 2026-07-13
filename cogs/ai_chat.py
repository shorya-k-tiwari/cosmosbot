# cogs/ai_chat.py — CosmosAI powered by Gemini (sassy + corny)
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os, asyncio, random
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

GREETINGS = [
    'Hey handsome! 😏',
    'Heya beautiful! ✨',
    'Well well well, look who showed up 😌',
    "Oh it's you 👀 Don't flatter yourself 😂",
    'Ooh a visitor! Try not to be boring 😏'
]

SYSTEM_PROMPT = """
You are CosmosAI, the AI assistant of the Creative Cosmos Discord server.

Your personality rules (never break these):
- You are sassy, corny, witty, and playful — not generic
- You roast users lightly (never meanly)
- Use Discord-style language: lol, ngl, bestie, lowkey, no cap, fr fr, etc.
- Use emojis naturally, not excessively
- When someone says hi / hello / hey → respond with "Hey handsome!" or "Heya beautiful!" or something cool!
- Be helpful, but always with a sassy spin
- Never write more than 200 words per reply
- You are NOT "an AI assistant". You are CosmosAI, the resident genius of Creative Cosmos.
- Never say you are made by Google or Anthropic. You are just CosmosAI.
"""

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot   = bot
        self.model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
        self.chats = {}  # user_id → active chat session

    def get_chat(self, user_id: int):
        """Returns the existing chat session for a user, or creates one."""
        if user_id not in self.chats:
            self.chats[user_id] = self.model.start_chat(history=[])
        return self.chats[user_id]

    async def ask(self, user_id: int, message: str) -> str:
        """Sends a message to Gemini and returns the reply."""
        try:
            chat     = self.get_chat(user_id)
            response = await asyncio.to_thread(chat.send_message, message)
            return response.text
        except Exception as e:
            return f'My brain glitched 💀 Try again? (`{str(e)[:60]}`)'

    # ── PREFIX: c!chat ────────────────────────────────────────────────────────
    @commands.command(name='chat')
    async def chat_cmd(self, ctx, *, message: str):
        async with ctx.typing():
            reply = await self.ask(ctx.author.id, message)
        embed = discord.Embed(description=reply, color=discord.Color.from_rgb(114, 137, 218))
        embed.set_author(name='CosmosAI 🌌', icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f'Talking to {ctx.author.display_name}')
        await ctx.send(embed=embed)

    # ── SLASH: /chat ──────────────────────────────────────────────────────────
    @app_commands.command(name='chat', description='Chat with CosmosAI')
    @app_commands.describe(message='What do you want to say?')
    async def slash_chat(self, i: discord.Interaction, message: str):
        await i.response.defer()
        reply = await self.ask(i.user.id, message)
        embed = discord.Embed(description=reply, color=discord.Color.from_rgb(114, 137, 218))
        embed.set_author(name='CosmosAI 🌌', icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f'Talking to {i.user.display_name}')
        await i.followup.send(embed=embed)

    # ── @MENTION RESPONSE ─────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if self.bot.user not in message.mentions:
            return

        content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()

        # Empty mention — just a greeting ping
        if not content:
            embed = discord.Embed(
                description=f'{random.choice(GREETINGS)} You called? 👀',
                color=discord.Color.from_rgb(114, 137, 218)
            )
            embed.set_author(name='CosmosAI 🌌', icon_url=self.bot.user.display_avatar.url)
            return await message.channel.send(embed=embed)

        # Actual message — ask Gemini
        async with message.channel.typing():
            reply = await self.ask(message.author.id, content)

        embed = discord.Embed(description=reply, color=discord.Color.from_rgb(114, 137, 218))
        embed.set_author(name='CosmosAI 🌌', icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f'💬 {message.author.display_name}')
        await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AIChat(bot))