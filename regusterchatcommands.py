import requests


url = "https://discord.com/api/v10/applications/appid/commands"

# This is an example CHAT_INPUT or Slash Command, with a type of 1
json = {
    "name": "register",
    "type": 1,
    "description": "Register your Steam ID with Lobby Bot",
    "options": [
        {
            "name": "Steam ID",
            "description": "Your Steam ID",
            "type": 3,
            "required": True,
        }
    ]
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot token"
}


r = requests.post(url, headers=headers, json=json)
print(r)