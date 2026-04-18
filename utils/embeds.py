import discord
from datetime import datetime

def create_id_embed(user_data: dict) -> discord.Embed:
    embed = discord.Embed(
        title="🚦 DoT — Officer ID Card",
        color=0xFFAA00
    )
    
    embed.add_field(name="👤 Name", value=f"**{user_data['roblox_username']}**", inline=False)
    embed.add_field(name="🎖️ Rank", value=user_data['discord_role'], inline=True)
    embed.add_field(name="🔢 SVC No.", value=f"#{user_data['service_number']}", inline=True)
    
    issued_date = datetime.fromtimestamp(user_data['created_at']).strftime('%B %d, %Y')
    embed.add_field(name="📅 Issued", value=issued_date, inline=True)
    
    if user_data['avatar_url']:
        embed.set_thumbnail(url=user_data['avatar_url'])
        
    embed.set_footer(text="San Aurie Department of Transportation")
    return embed
