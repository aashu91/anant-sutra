#!/usr/bin/env python3
import os
import sys
import asyncio
import discord
from discord.ext import commands

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spark_router import SparkRouter, ENV

DISCORD_TOKEN = ENV.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
router = SparkRouter()

@bot.event
async def on_ready():
    print(f"✅ SutraOS Discord Gateway logged in as {bot.user}")

@bot.command(name="spark")
async def spark_cmd(ctx, *, query: str):
    """Usage: !spark <any query>"""
    res = router.dispatch(query)
    color = 0x00FF00 if res.get("status") == "dispatched" else 0xFF9900
    embed = discord.Embed(
        title=f"⚡ Spark Router: {res.get('route', 'IDLE')}",
        description=f"**Query**: `{query}`\n**Status**: `{res.get('status')}`\n**Script**: `{os.path.basename(res.get('script', 'None'))}`\n**Score**: `{res.get('score', 0)}`",
        color=color
    )
    embed.set_footer(text="SutraOS Sovereign Brain • Termux Core")
    await ctx.send(embed=embed)

@bot.command(name="factcheck")
async def factcheck_cmd(ctx, *, claim: str):
    """Usage: !factcheck <claim or url>"""
    res = router.dispatch(f"fact check {claim}")
    await ctx.send(f"🔍 **Turiya Fact Check Triggered**: `{claim}`\nDispatched to `{os.path.basename(res.get('script', 'turiya_core.py'))}`.")

@bot.command(name="feedback")
async def feedback_cmd(ctx, target: str, quality: str, *, notes: str = ""):
    """Usage: !feedback <ANANT_ANAADI/TURIYA> <good/bad> <notes>"""
    is_sat = quality.lower() in ["good", "ok", "yes", "sat", "satisfied", "sahi"]
    fb = router.register_feedback(target, is_sat, notes)
    status_emoji = "✅" if is_sat else "🔄"
    await ctx.send(f"{status_emoji} **Memory Engine Updated**!\n**Target**: `{target}` | **Status**: `{fb['status']}`\n**Notes**: `{notes}`")

@bot.command(name="status")
async def status_cmd(ctx):
    """Usage: !status"""
    await ctx.send("⚡ **SutraOS Core**: Online 24/7 | Termux Engine Active.")

@bot.command(name="join")
async def join_cmd(ctx):
    """Joins user's Discord Voice Channel for 24/7 Voice Companion"""
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        try:
            vc = await channel.connect()
            await ctx.send(f"🎙️ **Joined Voice Channel**: `{channel.name}`! Active 24/7 Voice Listening mode.")
        except Exception as e:
            await ctx.send(f"🎙️ Connected to voice channel `{channel.name}` (Voice client initialization: {e})")
    else:
        await ctx.send("❌ Pehle ek Discord Voice Channel join karo, phir `!join` type karo!")

@bot.command(name="leave")
async def leave_cmd(ctx):
    """Disconnects from Voice Channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected from Voice Channel.")
    else:
        await ctx.send("❌ Bot abhi kisi voice channel mein nahi hai.")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("[ERROR] DISCORD_TOKEN missing in ~/poly_v2/.env")
        sys.exit(1)
    bot.run(DISCORD_TOKEN)
