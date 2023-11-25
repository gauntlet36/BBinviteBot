import requests


url = "https://discord.com/api/v10/applications/1177179830551322634/commands"

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
    "Authorization": "Bot MTE3NzE3OTgzMDU1MTMyMjYzNA.GAxlzJ.XGIo-eFXP9bO88RQRcLnEgsYk0dsz7aOd6B_MA"
}


r = requests.post(url, headers=headers, json=json)
print(r)