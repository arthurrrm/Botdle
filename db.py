import sqlite3
import os

DB_PATH = "scores.db"


def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT UNIQUE,
        pseudo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        channel_id TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_id INTEGER,
        date TEXT,
        score INTEGER,
        UNIQUE(user_id, game_id, date),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (game_id) REFERENCES games(id)
    )
    """)
    """
    tes serv:
    add_game("wordle", "1374794459136655421")
    add_game("timeguessr", "1374794493395599440")
    add_game("framed", "1375155452836315207")
    add_game("angle", "1375157615423655966")
    add_game("worldle", "1375160528837808259")
    add_game("hexle", "1375160592251490315")
    """
    
    # Nuit de nympho
    add_game("wordle", "1373389382551080992")
    add_game("timeguessr", "1373285606976917618")
    add_game("framed", "1373622523027259457")
    add_game("angle", "1373626933392179260")
    add_game("worldle", "1374710356424785962")
    add_game("hexle", "1374712040643498045")
    
    
    """
    add_user("123456789", "TestUser")
    add_score("123456789", "TestUser", "wordle", "2025-05-22", 80)
    add_score("521317397060255744", "Arthur", "wordle", "2025-05-21", 60)
    """
    conn.commit()
    conn.close()
    print("✅ Base de données réinitialisée.")

# Connexion unique
def get_conn():
    return sqlite3.connect("scores.db")

# Ajouter un utilisateur
def add_user(discord_id, pseudo):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (discord_id, pseudo) VALUES (?, ?)", (discord_id, pseudo))
    conn.commit()
    conn.close()

# Ajouter un jeu
def add_game(name, channel_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO games (name, channel_id) VALUES (?, ?)", (name, channel_id))
    conn.commit()
    conn.close()
    
def get_game_name(channel_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM games WHERE channel_id = ?", (channel_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Récupérer ID d’un utilisateur
def get_user_id(discord_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE discord_id = ?", (discord_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Récupérer ID d’un jeu
def get_game_id(name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM games WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Ajouter un score
def add_score(discord_id, pseudo, game_name, date, score):
    add_user(discord_id, pseudo)
    user_id = get_user_id(discord_id)

    game_id = get_game_id(game_name)
    if game_id is None:
        raise ValueError(f"Le jeu '{game_name}' n'existe pas encore dans la base de données.")

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO scores (user_id, game_id, date, score)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, game_id, date, score)
        )
        conn.commit()
    finally:
        conn.close()


# R\u00e9cup\u00e9rer les scores d’un jeu pour une date
def get_scores_by_game_and_date(game_name, date):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT users.pseudo, scores.score
        FROM scores
        JOIN users ON scores.user_id = users.id
        JOIN games ON scores.game_id = games.id
        WHERE games.name = ? AND scores.date = ?
        ORDER BY scores.score DESC
        """,
        (game_name, date)
    )
    results = cursor.fetchall()
    conn.close()
    return results

# Ne s’exécute que si tu fais : python db.py
if __name__ == "__main__":
    reset_db()