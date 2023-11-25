# BBinviteBot

Steam Lobby invite bot.


## Usage with Docker

Edit `src/.env` to include your Discord bot secrets, then it should be as 
simple as running `docker-compose up`. Specifically, you probably want
`docker-compose up -d`.


## Usage without Docker (not recommended)

Make sure you have Python 3.12 or above and Postgres installed. Edit `src/.env`
to include your Discord bot secrets and Postgres details, then run 
`pip install -r src/requirements.txt` to install the Python dependencies.
Finally run `python3 src/LobbyBot.py` and it will launch the bot.
