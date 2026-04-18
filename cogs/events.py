import discord
from discord.ext import commands, tasks
import itertools

from utils import database, roles

STATUS_MESSAGES = itertools.cycle([
    "🚦 Monitoring San Aurie Traffic | DoT",
    "🛣️ Patrolling the Highways | /id-get",
    "🚌 Department of Transportation | San Aurie",
    "📋 Use /id-create to register | DoT"
])

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")
        if not self.status_rotation.is_running():
            self.status_rotation.start()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles == after.roles:
            return

        discord_id = str(after.id)
        user_data = database.get_user(discord_id)
        if not user_data:
            return

        # Determine highest role using shared logic
        new_role = roles.get_highest_role(after)

        if new_role != user_data['discord_role']:
            database.update_user_role(discord_id, new_role)
            print(f"[Role Sync] Updated {after.display_name} locally to {new_role}")

    @tasks.loop(seconds=60)
    async def status_rotation(self):
        status = next(STATUS_MESSAGES)
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=status
        ))

    @status_rotation.before_loop
    async def before_status_rotation(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))


