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

    async def log_to_discord(self, message: str):
        """Sends a simple text log to the designated logging channel."""
        log_channel_id = os.getenv("LOG_CHANNEL_ID")
        if not log_channel_id:
            # Fallback to console if no channel is set
            print(f"[Log Search] {message}")
            return

        try:
            channel = self.get_channel(int(log_channel_id))
            if not channel:
                # If not in cache, try to fetch it
                channel = await self.fetch_channel(int(log_channel_id))
            
            if channel:
                await channel.send(f"📋 **System Log**: {message}")
            else:
                print(f"[Log Error] Could not find channel {log_channel_id}")
        except Exception as e:
            print(f"[Log Error] Failed to send log to Discord: {e}")
            print(f"Original Log: {message}")

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
