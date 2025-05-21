import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import re
from datetime import datetime
from db import * 
DEBUG = True
# List of supported games:
# wordle, timeguessr


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Bot connected: {bot.user}')

@bot.event
async def on_message(message): 
    if message.author.bot:
        return

    await bot.process_commands(message)

    channel_id = str(message.channel.id)
    game_name = get_game_name(channel_id)
    score = parse_score(message.content, game_name)
    
    if score is not None:
        username = message.author.display_name
        discord_id = str(message.author.id)
        date = datetime.now().strftime("%Y-%m-%d")

        try:
            add_score(discord_id, username, game_name, date, score)
            await message.add_reaction("✅")
            print(f"[{game_name}] {username} → {score}%")
        except Exception as e:
            print(f"⚠️ Error saving score: {e}")
     

@bot.command()
async def leaderboard(ctx, game_name: str = None):
    conn = get_conn()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    if game_name:
        # Get game ID
        cursor.execute("SELECT id FROM games WHERE name = ?", (game_name,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            await ctx.send(f"❌ Unknown game: `{game_name}`")
            return

        game_id = result[0]

        # Get today's scores for that game
        cursor.execute("""
            SELECT users.pseudo, scores.score
            FROM scores
            JOIN users ON users.id = scores.user_id
            WHERE scores.game_id = ? AND scores.date = ?
            ORDER BY scores.score DESC
        """, (game_id, today))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await ctx.send(f"No scores for `{game_name}` today.")
            return

        msg = f"📅 **Today's Leaderboard – {game_name}**\n"
        msg += "\n".join(f"{i+1}. {pseudo} — {score}%" for i, (pseudo, score) in enumerate(rows))
        await ctx.send(msg)

    else:
        # Global daily leaderboard: sum all today's scores across games (0 if not played)
        cursor.execute("SELECT id, name FROM games")
        games = cursor.fetchall()
        game_ids = [gid for gid, _ in games]
        total_games = len(game_ids)

        # Get all today's scores
        cursor.execute("""
            SELECT users.pseudo, scores.game_id, scores.score
            FROM scores
            JOIN users ON users.id = scores.user_id
            WHERE scores.date = ?
        """, (today,))
        raw_scores = cursor.fetchall()

        # Organize by user
        user_scores = {}
        for pseudo, game_id, score in raw_scores:
            if pseudo not in user_scores:
                user_scores[pseudo] = {}
            user_scores[pseudo][game_id] = score

        # Compute total for each user, missing games = 0
        leaderboard = []
        for pseudo, game_dict in user_scores.items():
            total = 0
            for gid in game_ids:
                total += game_dict.get(gid, 0)
            avg = round(total / total_games, 1)
            leaderboard.append((pseudo, avg))

        conn.close()

        if not leaderboard:
            await ctx.send("No scores recorded today.")
            return

        leaderboard.sort(key=lambda x: x[1], reverse=True)
        msg = "📅 **Today's Global Leaderboard**\n"
        for i, (pseudo, avg) in enumerate(leaderboard[:10]):
            msg += f"{i+1}. {pseudo} — {avg}% ({len(user_scores[pseudo])}/{total_games} games played)\n"
        await ctx.send(msg)


@bot.command()
async def score(ctx, game_name: str = None):
    if DEBUG:
        print(f"Command !score received: {ctx.author.display_name} ({ctx.author.id})")
    
    discord_id = str(ctx.author.id)

    if game_name is None:
        await ctx.send("❌ You must specify a game. Example: `!score wordle`")
        return

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM games WHERE name = ?", (game_name,))
    result = cursor.fetchone()

    if not result:
        await ctx.send(f"❌ Unknown game: {game_name}")
        conn.close()
        return

    game_id = result[0]

    cursor.execute("""
        SELECT ROUND(AVG(score), 1)
        FROM scores
        JOIN users ON users.id = scores.user_id
        WHERE users.discord_id = ? AND scores.game_id = ?
    """, (discord_id, game_id))

    avg = cursor.fetchone()[0]
    conn.close()

    if avg is None:
        await ctx.send("No scores found for you in this game.")
    else:
        await ctx.send(f"🎯 Your average score in **{game_name}**: **{avg}%**")
        
@bot.command(name="help")
async def custom_help(ctx):
    help_text = """
📚 **Available Commands**:

`!score <game>` – View your average score for a game  
`!leaderboard [game]` – View leaderboard of the day for a game (or global if no game specified)
`!help` – Show this help message
"""
    await ctx.send(help_text)


def parse_score(content: str, game: str) -> int | None:
    content = content.strip()

    if game == "wordle":
        # Example: Wordle 725 4/6
        match = re.search(r"Wordle \d+ (\d|X)/6", content)
        if match:
            raw = match.group(1)
            if raw == "X":
                return 0  # Fail = 0
            else:
                score = int(raw)
                return int((6 - score + 1) * (100 / 6)) 

    elif game == "timeguessr":
        # Example: TimeGuessr #720 38,317/50,000
        match = re.search(r"TimeGuessr #\d+ ([\d,]+)/([\d,]+)", content)
        if match:
            score = int(match.group(1).replace(",", ""))
            max_score = int(match.group(2).replace(",", ""))
            return int((score / max_score) * 100)
    
    return None

bot.run(TOKEN)