import os
import discord
from discord.ext import commands
from discord import app_commands

from utils import database, roblox, embeds, roles

class IDCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="id-create", description="Register and generate your DoT Officer ID Card.")
    @app_commands.describe(roblox_username="Your exact Roblox Username")
    async def id_create(self, interaction: discord.Interaction, roblox_username: str):
        await interaction.response.defer(ephemeral=False) # Make public
        
        if not roles.has_required_role(interaction.user, log_func=self.bot.log_to_discord):
            await interaction.followup.send("❌ You do not have the required role to create an ID card.")
            return

        discord_id = str(interaction.user.id)
        existing_user = database.get_user(discord_id)
        if existing_user:
            await interaction.followup.send("⚠️ You already have an ID card! Use `/id-get` to view it.")
            return

        roblox_user = await roblox.get_roblox_user_by_username(roblox_username)
        if not roblox_user:
            await interaction.followup.send(f"❌ Could not find a Roblox account with the username `{roblox_username}`. Make sure you typed it correctly.")
            return

        roblox_id = roblox_user["roblox_id"]
        roblox_username_proper = roblox_user["roblox_username"]

        avatar_url = await roblox.get_roblox_avatar(roblox_id)
        
        service_number = database.generate_service_number()
        if not service_number:
            await interaction.followup.send("❌ Error: All 999 service numbers are currently assigned.")
            return

        discord_role = roles.get_highest_role(interaction.user)

        user_data = {
            "discord_id": discord_id,
            "roblox_id": roblox_id,
            "roblox_username": roblox_username_proper,
            "discord_role": discord_role,
            "service_number": service_number,
            "avatar_url": avatar_url or ""
        }

        database.create_user(user_data)
        await self.bot.log_to_discord(f"✅ Created ID for **{roblox_username_proper}** (Discord: {interaction.user.name})")
        
        # Fetch the dict back just so we have the timestamps
        saved_user = database.get_user(discord_id)
        embed = embeds.create_id_embed(dict(saved_user))
        
        await interaction.followup.send(content="✅ **ID Card Successfully Created**", embed=embed)

    @app_commands.command(name="id-get", description="View a DoT ID card.")
    @app_commands.describe(user="The user to look up (leave blank for yourself)")
    async def id_get(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        discord_id = str(target.id)

        # If checking someone else, check admin perms
        if user and user.id != interaction.user.id:
            admin_roles = os.getenv("ADMIN_ROLE_ID", "").split(",")
            has_admin = any(str(r.id) in admin_roles for r in interaction.user.roles)
            if not has_admin:
                await interaction.response.send_message("❌ You do not have permission to view other users' IDs.", ephemeral=True)
                return

        user_data = database.get_user(discord_id)
        if not user_data:
            msg = "⚠️ You don't have an ID card yet! Use `/id-create` to register." if target.id == interaction.user.id else f"⚠️ {target.display_name} does not have an ID card."
            await interaction.response.send_message(msg, ephemeral=True)
            return

        # Auto-update role on fetch
        current_role = roles.get_highest_role(target)
        if current_role != user_data['discord_role']:
            database.update_user_role(discord_id, current_role)
            user_data = dict(user_data)
            user_data['discord_role'] = current_role

        embed = embeds.create_id_embed(dict(user_data))
        await self.bot.log_to_discord(f"🔍 {interaction.user.name} viewed ID for {target.display_name}")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(IDCommands(bot))
