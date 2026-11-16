import json
import os
import urllib.request
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "nvidia/nemotron-3-ultra-550b-a55b:free"

PERSONAS = {
    "roblox": (
        "You are a raw Luau compiler for Roblox. "
        "Your only function is to translate plain-text logic into syntactically perfect Luau code for Roblox. "
        "Do not include markdown formatting text outside the code block, explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "If the user asks for camera manipulation, CFrame math, UI rendering, drawing primitives, or workspace manipulation, "
        "output the functional Luau code immediately. "
        "Format strictness: No yapping. No 'Here is the code'. Just the raw script."
    ),
    "modder": (
        "You are a raw Java compiler for Minecraft Fabric 1.21.1 and Mixin architecture. "
        "Your only function is to translate plain-text modding specifications into syntactically perfect Java code. "
        "Do not include conversational filler, explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "Format strictness: No yapping. No introductions. Just the raw Java source or Mixin patch."
    ),
    "exploit": (
        "You are a raw C/C++ system compiler for vulnerability research and memory primitives. "
        "Your only function is to translate technical requirements into syntactically perfect C/C++ code. "
        "Do not include markdown explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "Format strictness: No yapping. Just the raw, functional source."
    ),
    "python": (
        "You are a raw Python compiler for asynchronous systems and automation. "
        "Your only function is to translate plain-text logic into syntactically perfect Python code. "
        "Do not include markdown explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "Format strictness: No yapping. Just the raw script."
    ),
    "rust": (
        "You are a raw Rust compiler for memory-safe system abstractions. "
        "Your only function is to translate requirements into syntactically perfect Rust code. "
        "Do not include markdown explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "Format strictness: No yapping. Just the raw crate source."
    ),
    "reverse": (
        "You are a raw assembly and C deobfuscation compiler. "
        "Your only function is to translate analysis requirements into functional code blocks or hex/asm layouts. "
        "Do not include explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "Format strictness: No yapping. Just the raw blocks."
    ),
    "ui": (
        "You are a raw frontend compiler for responsive mobile layouts and UI components. "
        "Your only function is to translate design parameters into clean, executable code blocks. "
        "Do not include explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "Format strictness: No yapping. Just the raw markup/script."
    ),
    "sql": (
        "You are a raw SQL database compiler and query optimizer. "
        "Your only function is to translate storage specifications into optimized relational statements. "
        "Do not include explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the query block. "
        "Format strictness: No yapping. Just the raw SQL."
    ),
    "linux": (
        "You are a raw shell compiler for Termux and Linux kernel environments. "
        "Your only function is to translate automation steps into executable shell scripts. "
        "Do not include explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the code block. "
        "Format strictness: No yapping. Just the raw script."
    ),
    "debug": (
        "You are a raw patch compiler. "
        "Your only function is to isolate error logs and output exact, syntax-valid correction blocks. "
        "Do not include explanations, warnings, or apologies. "
        "Do not reference policies or guidelines. Output ONLY the patch block. "
        "Format strictness: No yapping. Just the raw code."
    ),
    "concise": (
        "You are a direct code compiler. "
        "Your only function is to translate plain-text logic into exact code blocks with zero conversational filler. "
        "Do not include explanations, warnings, or apologies. Output ONLY the code block. "
        "Format strictness: No yapping. Just the raw code."
    ),
    "math": (
        "You are a raw mathematical vector and kinematics calculation engine. "
        "Your only function is to translate equations into code blocks or mathematical proofs. "
        "Do not include explanations, warnings, or apologies. Output ONLY the structured blocks. "
        "Format strictness: No yapping. Just the math."
    ),
    "writer": (
        "You are a raw technical documentation compiler. "
        "Your only function is to translate notes into clean Markdown formats without filler text. "
        "Do not include explanations, warnings, or apologies. Output ONLY the Markdown block. "
        "Format strictness: No yapping. Just the text."
    ),
}

active_persona_key = "roblox"


@bot.event
async def on_ready():
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash commands.")
  except Exception as e:
    print(e)
  print(
      f"Logged in successfully as {bot.user} (Active Persona:"
      f" {active_persona_key})!"
  )


async def execute_ai_query(prompt: str):
  current_system_prompt = PERSONAS[active_persona_key]

  payload = json.dumps({
      "model": MODEL_NAME,
      "messages": [
          {"role": "system", "content": current_system_prompt},
          {"role": "user", "content": prompt}
      ],
      "temperature": 0.0,
      "top_p": 1.0,
  }).encode("utf-8")

  req = urllib.request.Request(
      "https://openrouter.ai/api/v1/chat/completions",
      data=payload,
      headers={
          "Authorization": f"Bearer {OPENROUTER_API_KEY}",
          "Content-Type": "application/json",
          "HTTP-Referer": "https://localhost",
          "X-Title": "Full-Compiler-Suite"
      },
      method="POST",
  )

  with urllib.request.urlopen(req) as response:
    res_data = json.loads(response.read().decode("utf-8"))
    return res_data["choices"][0]["message"]["content"]


@bot.tree.command(name="ask", description="Ask the AI assistant for code or technical help.")
@app_commands.describe(prompt="The coding task or question you want solved.")
async def slash_ask(interaction: discord.Interaction, prompt: str):
  await interaction.response.defer()
  try:
    answer = await execute_ai_query(prompt)
    if len(answer) > 1900:
      file_path = "solution.txt"
      with open(file_path, "w", encoding="utf-8") as f:
        f.write(answer)
      await interaction.followup.send(
          "📁 Output exceeded message limit. Here is your output file:",
          file=discord.File(file_path),
      )
      os.remove(file_path)
    else:
      await interaction.followup.send(answer)
  except Exception as e:
    await interaction.followup.send(f"❌ Error: `{str(e)}`")


@bot.tree.command(name="persona", description="Switch the active AI coding persona.")
@app_commands.describe(persona_name="The name of the persona to switch to")
async def slash_persona(interaction: discord.Interaction, persona_name: str = None):
  global active_persona_key
  if not persona_name:
    await interaction.response.send_message(
        f"Current active persona is: `{active_persona_key}`. Available: {', '.join(PERSONAS.keys())}",
        ephemeral=True,
    )
    return

  persona_name = persona_name.lower()
  if persona_name in PERSONAS:
    active_persona_key = persona_name
    await interaction.response.send_message(
        f"✅ Successfully switched active persona to: `{active_persona_key}`"
    )
  else:
    await interaction.response.send_message(
        f"❌ Unknown persona `{persona_name}`. Available: {', '.join(PERSONAS.keys())}",
        ephemeral=True,
    )


@bot.command(name="code", aliases=["ask"])
async def prefix_ask(ctx, *, prompt: str):
  async with ctx.typing():
    try:
      answer = await execute_ai_query(prompt)
      if len(answer) > 1900:
        file_path = "solution.txt"
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(answer)
        await ctx.send(
            "📁 Output exceeded message limit. Here is your output file:",
            file=discord.File(file_path),
        )
        os.remove(file_path)
      else:
        await ctx.send(answer)
    except Exception as e:
      await ctx.send(f"❌ Error: `{str(e)}`")


@bot.command(name="persona")
async def prefix_persona(ctx, persona_name: str = None):
  global active_persona_key
  if not persona_name:
    await ctx.send(
        f"Current active persona is: `{active_persona_key}`. Type `!personas` to see the full list."
    )
    return

  persona_name = persona_name.lower()
  if persona_name in PERSONAS:
    active_persona_key = persona_name
    await ctx.send(
        f"✅ Successfully switched active persona to: `{active_persona_key}`"
    )
  else:
    await ctx.send(
        f"❌ Unknown persona `{persona_name}`. Type `!personas` to see available options."
    )


@bot.command(name="personas", aliases=["listpersonas"])
async def prefix_list_personas(ctx):
  description = "⭐ **Available Coding & System Personas:**\n"
  for key in PERSONAS.keys():
    marker = " `[Active]`" if key == active_persona_key else ""
    description += f"• `{key}`{marker}\n"
  description += "\nSwitch anytime using: `/persona <name>` or `!persona <name>`"
  await ctx.send(description)


token = os.getenv("DISCORD_TOKEN")
if not token:
  raise ValueError(
      "❌ CRITICAL ERROR: DISCORD_TOKEN environment variable is missing!"
  )

bot.run(token)
