import os
import discord

def get_highest_role(member: discord.Member) -> str:
    """
    Calculates the highest role name for a member, 
    filtering out roles above the ADMIN_ROLE_ID threshold.
    """
    admin_role_id = os.getenv("ADMIN_ROLE_ID")
    
    # Get all roles except @everyone
    roles = [r for r in member.roles if r.name != "@everyone"]
    if not roles:
        return "Citizen"

    # Find the position threshold (highest allowed role)
    # If ADMIN_ROLE_ID is not set or role not found, we don't filter by position
    threshold_position = 999999 # Default to very high
    if admin_role_id:
        try:
            # Try to find the threshold role in the member's guild
            threshold_role = member.guild.get_role(int(admin_role_id))
            if threshold_role:
                threshold_position = threshold_role.position
        except (ValueError, TypeError):
            pass # Use default high position if ID is invalid

    # Filter out roles ABOVE the threshold
    # Note: We keep the threshold role itself and anything below it
    allowed_roles = [r for r in roles if r.position <= threshold_position]
    
    if not allowed_roles:
        return "Citizen"

    # Sort by position descending
    allowed_roles.sort(key=lambda r: r.position, reverse=True)
    
    return allowed_roles[0].name

def has_required_role(member: discord.Member | discord.User, log_func=None) -> bool:
    """
    Checks if the member has the required role(s) to create an ID.
    Handles multiple comma-separated IDs and trims whitespace.
    """
    required_ids_str = os.getenv("REQUIRED_ROLE_ID", "").strip()
    if not required_ids_str:
        return True 
        
    # Split by comma and clean up whitespace
    required_ids = [rid.strip() for rid in required_ids_str.split(",") if rid.strip()]
    
    # Defensive check: if it's not a Member object, it doesn't have roles
    if not hasattr(member, "roles"):
        if log_func:
            debug_msg = f"Object for {member.name} has no 'roles' attribute. (Not a Member object? Type: {type(member)})"
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(log_func(f"❌ {debug_msg}"))
        return False

    # Check if any of the member's roles match any of the required IDs
    member_role_ids = [str(r.id) for r in member.roles]
    success = any(rid in member_role_ids for rid in required_ids)
    
    if log_func:
        status = "✅ PASS" if success else "❌ FAIL"
        debug_info = f"User: {member.name} | Has Roles: {member_role_ids} | Required: {required_ids}"
        # Use bot's loop or member's guild bot loop to schedule the log
        # In discord.py commands, interaction.client is the bot
        # But we'll try to use member.guild.me.guild.client if possible, or just assume log_func is a bound method
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(log_func(f"{status} Role Check | {debug_info}"))
    
    return success
