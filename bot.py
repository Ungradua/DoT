import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()

class DoTAssistant(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # Required for on_member_update
        super().__init__(
            command_prefix="!", 
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Load cogs dynamically
        for folder in ['cogs']:
            for filename in os.listdir(folder):
                if filename.endswith('.py') and not filename.startswith('__'):
                    await self.load_extension(f"{folder}.{filename[:-3]}")
                    print(f"[Cogs] Loaded {filename}")

        # Sync application slash commands automatically
        # We sync globally AND to the guild (if set) to clear any 'Ghost' global commands
        try:
            await self.tree.sync()
            print("[Commands] Global sync complete")
            
            guild_id = os.getenv("GUILD_ID")
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"[Commands] Synced to guild {guild_id}")
        except Exception as e:
            print(f"[Commands] Error syncing: {e}")

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token or "your_discord_bot_token" in token:
        print("[Error] DISCORD_TOKEN is not valid in .env")
        return

    bot = DoTAssistant()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    keep_alive() # Start the web server
    asyncio.run(main())
