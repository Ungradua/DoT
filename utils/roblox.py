import aiohttp

async def get_roblox_user_by_username(roblox_username: str) -> dict | None:
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [roblox_username], "excludeBannedUsers": False}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        user = data["data"][0]
                        return {
                            "roblox_id": str(user["id"]),
                            "roblox_username": user["name"] # proper capitalization
                        }
                return None
    except Exception as e:
        print(f"[Roblox] Error fetching user by username: {e}")
        return None
async def get_roblox_username(roblox_id: str) -> str | None:
    url = f"https://users.roblox.com/v1/users/{roblox_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('name')
                return None
    except Exception as e:
        print(f"[Roblox] Error fetching username: {e}")
        return None

async def get_roblox_avatar(roblox_id: str) -> str | None:
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={roblox_id}&size=420x420&format=Png&isCircular=false"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and len(data['data']) > 0:
                        return data['data'][0].get('imageUrl')
                return None
    except Exception as e:
        print(f"[Roblox] Error fetching avatar: {e}")
        return None
