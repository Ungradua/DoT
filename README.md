# 🚦 DoT Assistant — Discord Bot

**Department of Transportation** bot for the **San Aurie** Roblox roleplay server.

---

## Features
- 🔄 **Activity Rotation** — Cycles through DoT-themed status messages.
- 🪪 **Officer ID System** — `/id-create` and `/id-get` with photo integration.
- 🚔 **Violation Filing** — Persistent panel for filing and reviewing fines.
- 🔍 **Background Checks** — `/check-background` to view a citizen's violation history.
- 🔃 **Auto Role Sync** — Keeps ranks updated with Discord roles automatically.
- 💾 **SQLite Database** — Built-in native Python SQLite database storage.

---

## Prerequisites

| Tool | Version |
|---|---|
| [Python](https://www.python.org/) | 3.10+ |
| A Discord Bot Token | [discord.dev/applications](https://discord.com/developers/applications) |

---

## Setup

### 1. Configure Environment
Rename `.env.example` to `.env` and fill in your details:
```env
DISCORD_TOKEN=your_token
CLIENT_ID=your_id
GUILD_ID=your_server_id
# ... (see .env.example for all fields)
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Start the Bot
```bash
python bot.py
```

---

## Project Structure
```
DoT Assistant/
├── bot.py               # Bot entry point
├── requirements.txt     # Python deps
├── cogs/                # Bot modules
│   ├── commands.py      # ID commands
│   ├── events.py        # Event handlers
│   └── fines.py         # Violation system
├── utils/               # Helpers
│   ├── database.py      # SQLite manager
│   ├── roblox.py        # Roblox API
│   └── embeds.py        # Embed templates
└── data/
    └── dot.db           # SQLite database
```

---

---

## 24/7 Hosting (Render)
This bot includes a `keep_alive.py` script to stay online 24/7 on free services like **Render**.

1.  **Deploy to Render**: Create a new **Web Service** on Render and link this GitHub repo.
2.  **Command**: Set the start command to `python bot.py`.
3.  **Keep Alive**: Once deployed, copy your Render URL (e.g., `https://dot-bot.onrender.com`).
4.  **UptimeRobot**: Create a free account on [UptimeRobot](https://uptimerobot.com/), add a "HTTP Monitor," and paste your Render URL. 
    *   Set it to ping every **5 minutes**.
    *   This will prevent the bot from going to sleep!

