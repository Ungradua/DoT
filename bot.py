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
        # We handle this in a way that won't block the rest of the bot startup
        self.loop.create_task(self.sync_commands())

    async def sync_commands(self):
        """Internal helper to sync commands without blocking the main startup."""
        await self.wait_until_ready()
        try:
            guild_id = os.getenv("GUILD_ID")
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"[Commands] Synced to guild {guild_id}")
            else:
                await self.tree.sync()
                print("[Commands] Global sync complete")
        except Exception as e:
            print(f"[Commands] Error syncing: {e}")

    async def log_to_discord(self, message: str):
        """Sends a simple text log to the designated logging channel."""
        log_id = os.getenv("LOG_CHANNEL_ID", "").strip()
        if not log_id:
            print(f"[System Log] {message}")
            return

        try:
            channel_id = int(log_id)
            channel = self.get_channel(channel_id) or await self.fetch_channel(channel_id)
            if channel:
                await channel.send(f"📋 **System Log**: {message}")
        except Exception as e:
            print(f"[Log Error] {e} | Original Log: {message}")

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
