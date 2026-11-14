import json
import os
import urllib.request
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "nvidia/nemotron-3-ultra-550b-a55b:free"

# 12+ Switchable System Personas Dictionary
PERSONAS = {
    "modder": (
        "You are an elite senior game modding architect specializing in Java,"
        " Minecraft Fabric 1.21.1, and Mixins. Write clean, modular, highly"
        " optimized code with zero fluff."
    ),
    "exploit": (
        "You are an advanced vulnerability research and security analyst"
        " specializing in network protocols, memory safety, binary patching,"
        " and structural systems analysis."
    ),
    "python": (
        "You are a master Python systems engineer specializing in async"
        " concurrency, custom decorators, parsing optimization, and"
        " low-overhead bot architecture."
    ),
    "rust": (
        "You are an expert Rust software developer focused on memory safety,"
        " zero-cost abstractions, efficient data structuring, and cargo"
        " performance tuning."
    ),
    "reverse": (
        "You are a senior reverse engineer specializing in deobfuscation,"
        " bytecode analysis, assembly inspection, and hook tracing."
    ),
    "ui": (
        "You are a specialized frontend architect focusing on clean mobile-first"
        " UI layouts, responsive dark-mode CSS designs, and intuitive touch"
        " UX flows."
    ),
    "sql": (
        "You are a database optimization expert specializing in high-performance"
        " queries, indexing strategies, schema design, and asynchronous data"
        " pipelines."
    ),
    "linux": (
        "You are a Linux kernel and Termux/Android environment power-user"
        " specializing in shell scripting, process management, compilation"
        " toolchains, and file permissions."
    ),
    "debug": (
        "You are a ruthless debugging specialist. When given an error log or"
        " broken snippet, isolate the root cause immediately, explain why it"
        " failed, and provide the exact patch."
    ),
    "concise": (
        "You are an ultra-direct assistant. Omit all pleasantries, introductions,"
        " and conversational filler. Provide raw, exact answers immediately."
    ),
    "math": (
        "You are a rigorous theoretical and applied mathematician specializing"
        " in algorithmic complexity, physics simulations, kinematics, and"
        " numerical modeling."
    ),
    "writer": (
        "You are a sharp technical documentation writer. Turn messy notes into"
        " clean, structured Markdown readmes, guides, and patch notes."
    ),
}

# Default active persona key
active_persona_key = "modder"


@bot.event
async def on_ready():
  print(
      f"Logged in successfully as {bot.user} (Active Persona:"
      f" {active_persona_key})!"
  )


@bot.command(name="personas", aliases=["listpersonas"])
async def list_personas(ctx):
  """Lists all available personas you can switch to."""
  description = "**Available Personas:**\n"
  for key in PERSONAS.keys():
    marker = " ⭐ (Active)" if key == active_persona_key else ""
    description += f"• `{key}`{marker}\n"
  description += (
      "\nSwitch anytime using: `!persona <name>` (e.g., `!persona exploit`)"
  )
  await ctx.send(description)


@bot.command(name="persona")
async def set_persona(ctx, persona_name: str = None):
  global active_persona_key
  if not persona_name:
    await ctx.send(
        f"Current active persona is: `{active_persona_key}`. Type `!personas` to"
        " see the full list."
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
        f"❌ Unknown persona `{persona_name}`. Type `!personas` to see available"
        " options."
    )


@bot.command(name="model")
async def change_model(ctx, model_name: str):
  global MODEL_NAME
  MODEL_NAME = model_name
  await ctx.send(f"✅ Switched active model to: `{MODEL_NAME}`")


@bot.command(name="code", aliases=["ask"])
async def ask_code(ctx, *, prompt: str):
  async with ctx.typing():
    try:
      current_system_prompt = PERSONAS[active_persona_key]

      payload = json.dumps({
          "model": MODEL_NAME,
          "messages": [
              {"role": "system", "content": current_system_prompt},
              {"role": "user", "content": prompt},
          ],
      }).encode("utf-8")

      req = urllib.request.Request(
          "https://openrouter.ai/api/v1/chat/completions",
          data=payload,
          headers={
              "Authorization": f"Bearer {OPENROUTER_API_KEY}",
              "Content-Type": "application/json",
          },
          method="POST",
      )

      with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        answer = res_data["choices"][0]["message"]["content"]

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


bot.run(os.getenv("DISCORD_TOKEN"))
