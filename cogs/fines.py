import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import time
from utils import database, embeds

class ViolationReportModal(ui.Modal, title='File Violation Report'):
    violation_type = ui.TextInput(label='Type of Violation', placeholder='e.g., Illegal Parking, Speeding...', required=True)
    proof_link = ui.TextInput(label='Proof Link (Media Link)', placeholder='Link to image/video proof', required=True)
    citizen_name = ui.TextInput(label='Citizen Roblox Username', placeholder='Name of the player', required=True)

    def __init__(self, officer_data):
        super().__init__()
        self.officer_data = officer_data

    async def on_submit(self, interaction: discord.Interaction):
        # Notify staff
        staff_channel_id = os.getenv('STAFF_CHANNEL_ID')
        staff_channel = interaction.guild.get_channel(int(staff_channel_id))
        
        if not staff_channel:
            await interaction.response.send_message("❌ Error: Staff channel not found. Please contact an admin.", ephemeral=True)
            return

        embed = discord.Embed(title="🚨 New Fine Request", color=discord.Color.orange())
        embed.add_field(name="👮 Officer", value=interaction.user.mention, inline=True)
        embed.add_field(name="🔢 SVC No.", value=f"#{self.officer_data['service_number']}", inline=True)
        embed.add_field(name="👤 Violator (Roblox)", value=self.citizen_name.value, inline=False)
        embed.add_field(name="🚦 Violation", value=self.violation_type.value, inline=False)
        embed.add_field(name="📷 Proof", value=self.proof_link.value, inline=False)
        embed.set_footer(text="If you have any issue feel free to contact the management using management ticket")

        # Buttons for staff
        view = StaffReviewView(self.citizen_name.value, self.violation_type.value, self.proof_link.value, self.officer_data)
        await staff_channel.send(embed=embed, view=view)
        
        await interaction.response.send_message("✅ Your violation report has been sent to staff for review.", ephemeral=True)

class StaffApprovalModal(ui.Modal, title='Finalize Punishment'):
    target_user = ui.TextInput(label='Violator Discord User ID', placeholder='Paste Discord ID here', required=True, min_length=17, max_length=20)
    punishment = ui.TextInput(label='Final Punishment', placeholder='e.g., $500 Fine, 5min Jail', required=True)
    reason = ui.TextInput(label='Final Reason', style=discord.TextStyle.paragraph, required=True)

    def __init__(self, roblox_name, violation_type, proof_link, officer_data):
        super().__init__()
        self.roblox_name = roblox_name
        self.violation_type = violation_type
        self.proof_link = proof_link
        self.officer_data = officer_data

    async def on_submit(self, interaction: discord.Interaction):
        # Log to DB
        data = {
            'officer_id': str(self.officer_data['discord_id']),
            'officer_svc': self.officer_data['service_number'],
            'violator_id': self.target_user.value,
            'violation_type': self.violation_type,
            'proof_link': self.proof_link,
            'punishment': self.punishment.value,
            'staff_id': str(interaction.user.id)
        }
        database.add_violation(data)

        # Update message
        embed = interaction.message.embeds[0]
        embed.title = "✅ Fine Approved"
        embed.color = discord.Color.green()
        embed.add_field(name="⚖️ Decision By", value=interaction.user.mention, inline=True)
        embed.add_field(name="🔨 Punishment", value=self.punishment.value, inline=True)
        embed.add_field(name="🆔 Target Discord ID", value=self.target_user.value, inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Try to DM user
        try:
            target = await interaction.client.fetch_user(int(self.target_user.value))
            dm_embed = discord.Embed(title="🚧 DoT Violation Notice", description="An official violation has been logged against your record.", color=discord.Color.red())
            dm_embed.add_field(name="🚦 Violation", value=self.violation_type)
            dm_embed.add_field(name="🔨 Punishment", value=self.punishment.value)
            dm_embed.add_field(name="📝 Reason", value=self.reason.value)
            dm_embed.set_footer(text="If you have any issue feel free to contact the management using management ticket")
            await target.send(embed=dm_embed)
        except:
            pass

class StaffReviewView(ui.View):
    def __init__(self, roblox_name, violation_type, proof_link, officer_data):
        super().__init__(timeout=None)
        self.roblox_name = roblox_name
        self.violation_type = violation_type
        self.proof_link = proof_link
        self.officer_data = officer_data

    @ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve_fine")
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        # Check roles
        staff_roles = os.getenv('STAFF_ROLE_IDS', '').split()
        if not any(str(role.id) in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ You are not authorized to approve fines.", ephemeral=True)
            return
            
        modal = StaffApprovalModal(self.roblox_name, self.violation_type, self.proof_link, self.officer_data)
        await interaction.response.send_modal(modal)

    @ui.button(label="Reject", style=discord.ButtonStyle.red, custom_id="reject_fine")
    async def reject(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = os.getenv('STAFF_ROLE_IDS', '').split()
        if not any(str(role.id) in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ You are not authorized to reject fines.", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.title = "❌ Fine Rejected"
        embed.color = discord.Color.red()
        embed.add_field(name="⚖️ Rejected By", value=interaction.user.mention, inline=True)
        await interaction.response.edit_message(embed=embed, view=None)

class FinePanelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="📝 File Fine Request", style=discord.ButtonStyle.primary, custom_id="file_fine_btn")
    async def file_fine(self, interaction: discord.Interaction, button: ui.Button):
        # Check role
        allowed_role_id = os.getenv('OFFICER_PANEL_ROLE_ID')
        if not any(str(role.id) == allowed_role_id for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to use this panel.", ephemeral=True)
            return

        # Check if they have an ID and get their SVC No.
        user_data = database.get_user(str(interaction.user.id))
        if not user_data:
            await interaction.response.send_message("⚠️ You must have an ID card to file fines! Use `/id-create` first.", ephemeral=True)
            return

        await interaction.response.send_modal(ViolationReportModal(user_data))

class Fines(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup-fine-panel", description="Spawn the persistent Fine Filing panel.")
    @app_commands.default_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        # Check if in right channel
        target_channel_id = os.getenv('PD_CHANNEL_ID')
        if str(interaction.channel_id) != target_channel_id:
            await interaction.response.send_message(f"❌ This command must be run in the designated PD Channel (<#{target_channel_id}>).", ephemeral=True)
            return

        embed = discord.Embed(
            title="🚔 DoT Official Fine Filing",
            description=(
                "Click the button below to file a formal violation report against a citizen.\n\n"
                "**Requirements:**\n"
                "- Must have a valid DoT ID.\n"
                "- Must provide valid media proof (link).\n\n"
                "*All reports are reviewed by DoT Management.*"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="If you have any issue feel free to contact the management using management ticket")
        
        await interaction.channel.send(embed=embed, view=FinePanelView())
        await interaction.response.send_message("✅ Panel spawned.", ephemeral=True)

    @app_commands.command(name="check-background", description="Retrieve all past violations for a user.")
    @app_commands.describe(user="The user to check (mention or ID)")
    async def check_bg(self, interaction: discord.Interaction, user: discord.Member):
        # Check roles
        staff_roles = os.getenv('STAFF_ROLE_IDS', '').split()
        if not any(str(role.id) in staff_roles for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You are not authorized to run background checks.", ephemeral=True)
            return

        violations = database.get_violations(str(user.id))
        if not violations:
            await interaction.response.send_message(f"✅ User {user.display_name} has a clean record.", ephemeral=False)
            return

        embed = discord.Embed(title=f"📋 Background Check: {user.display_name}", color=discord.Color.red())
        
        for idx, v in enumerate(violations, 1):
            date_str = time.strftime('%Y-%m-%d', time.localtime(v['created_at']))
            val = (
                f"**Violation:** {v['violation_type']}\n"
                f"**Punishment:** {v['punishment']}\n"
                f"**Officer:** #{v['officer_svc']}\n"
                f"**Staff:** <@{v['staff_id']}>\n"
                f"**Date:** {date_str}\n"
                f"[Proof Link]({v['proof_link']})"
            )
            embed.add_field(name=f"Case #{idx}", value=val, inline=False)

        embed.set_footer(text="San Aurie Department of Transportation")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    cog = Fines(bot)
    await bot.add_cog(cog)
    bot.add_view(FinePanelView())
