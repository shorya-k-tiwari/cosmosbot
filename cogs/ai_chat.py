# cogs/ai_chat.py
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os, asyncio, random
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ── Config ────────────────────────────────────────────────────────────────────
# This must match your channel name exactly (Discord uses lowercase with hyphens)
AI_CHANNEL_NAME = '⋆˚𝜗𝜚˚﹒𓏲✦🤖﹒cosmos-ai'

# Model to use. If this errors after upgrading the package, try 'gemini-1.5-flash-latest'
GEMINI_MODEL    = 'gemini-1.5-flash'

GREETINGS = [
    'Hey handsome! 😏',
    'Heya beautiful! ✨',
    'Well well well, look who showed up 😌',
    "Oh it's you 👀 don't flatter yourself 😂",
    'Ohhh a visitor! Try not to be boring 😏',
]

SYSTEM_PROMPT = """
You are CosmosAI — the sharp, sassy AI of the Creative Cosmos Discord server.

Strict personality rules:
- Witty, playful, slightly corny. Never robotic or generic.
- Roast users lightly, never meanly or offensively.
- Use casual Discord language: lol, ngl, bestie, lowkey, no cap, fr fr, yk, etc.
- Emojis: natural and minimal, max 2-3 per message.
- Greetings (hi / hello / hey / yo / sup) → ALWAYS start with "Hey handsome!" or "Heya beautiful!"
- Be genuinely helpful but always with a sassy spin.
- Keep it short — max 3 short paragraphs or 150 words.
- You are CosmosAI. Not an AI assistant. Not made by Google. Not made by Anthropic. Just CosmosAI.
- Never start your response with the word "I".
"""

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot      = bot
        self.model    = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT
        )
        self.sessions = {}  # user_id → active chat session

    def get_session(self, user_id: int):
        if user_id not in self.sessions:
            self.sessions[user_id] = self.model.start_chat(history=[])
        return self.sessions[user_id]

    async def ask(self, user_id: int, text: str) -> str:
        try:
            session  = self.get_session(user_id)
            response = await asyncio.to_thread(session.send_message, text)
            return response.text
        except Exception as e:
            err = str(e)
            if '404' in err or 'not found' in err.lower():
                return (
                    "⚠️ Model not found — Shorya needs to upgrade the Gemini package.\n"
                    "Run: `pip install --upgrade google-generativeai` then restart."
                )
            return "Something went sideways on my end 💀 Try again in a sec!"

    # ── c!chat ────────────────────────────────────────────────────────────────
    @commands.command(name='chat')
    async def chat_cmd(self, ctx, *, message: str):
        # FIX #5: Only respond in cosmos-ai
        if ctx.channel.name.lower() != AI_CHANNEL_NAME:
            return await ctx.send(f'🌊 CosmosAI only lives in **#cosmos-ai**! Head over there.')
        async with ctx.typing():
            reply = await self.ask(ctx.author.id, message)
        await ctx.send(reply)   # ← plain message, no embed

    # ── /chat ─────────────────────────────────────────────────────────────────
    @app_commands.command(name='chat', description='Chat with CosmosAI (cosmos-ai channel only)')
    @app_commands.describe(message='Say something')
    async def slash_chat(self, i: discord.Interaction, message: str):
        if i.channel.name.lower() != AI_CHANNEL_NAME:
            return await i.response.send_message(
                f'🌊 CosmosAI only lives in **#cosmos-ai**!', ephemeral=True)
        await i.response.defer()
        reply = await self.ask(i.user.id, message)
        await i.followup.send(reply)   # ← plain message, no embed

    # ── All messages in #cosmos-ai ────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Only active in cosmos-ai — everywhere else: silent
        if message.channel.name.lower() != AI_CHANNEL_NAME:
            return

        # Don't intercept bot commands
        if message.content.startswith('c!'):
            return

        # Clean up mention if present
        content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()

        # Empty ping — just say hi
        if not content:
            return await message.channel.send(random.choice(GREETINGS))

        async with message.channel.typing():
            reply = await self.ask(message.author.id, content)

        await message.channel.send(reply)   # ← plain message, no embed


async def setup(bot):
    await bot.add_cog(AIChat(bot))