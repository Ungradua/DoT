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

def has_required_role(member: discord.Member | discord.User) -> bool:
    """
    Checks if the member has the required role(s) to create an ID.
    Handles multiple comma-separated IDs and trims whitespace.
    """
    required_ids_str = os.getenv("REQUIRED_ROLE_ID", "").strip()
    if not required_ids_str:
        return True # If no requirement set, allow all
        
    # Split by comma and clean up whitespace
    required_ids = [rid.strip() for rid in required_ids_str.split(",") if rid.strip()]
    
    # Defensive check: if it's not a Member object, it doesn't have roles
    if not hasattr(member, "roles"):
        return False

    # Check if any of the member's roles match any of the required IDs
    member_role_ids = [str(r.id) for r in member.roles]
    
    # SYSTEM DEBUG: Printing to console to help resolve the 'error still exist' issue
    print(f"[DEBUG] Checking roles for {member.name} ({member.id})")
    print(f"        Member Roles: {member_role_ids}")
    print(f"        Required IDs: {required_ids}")
    
    success = any(rid in member_role_ids for rid in required_ids)
    print(f"        Check Result: {success}")
    
    return success
