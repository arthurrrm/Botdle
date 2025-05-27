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
    # For test server and Nuit de nympho server setup, see test_db_setup.py and nympho_db_setup.py
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

# Récupérer ID d'un utilisateur
def get_user_id(discord_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE discord_id = ?", (discord_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Récupérer ID d'un jeu
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


# Récupérer les scores d'un jeu pour une date
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

def get_user_highscore(discord_id, game_name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(score)
        FROM scores
        JOIN users ON users.id = scores.user_id
        JOIN games ON games.id = scores.game_id
        WHERE users.discord_id = ? AND games.name = ?
    ''', (discord_id, game_name))
    result = cursor.fetchone()[0]
    conn.close()
    return result


def get_game_highscore(game_name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.pseudo, scores.score, scores.date
        FROM scores
        JOIN users ON users.id = scores.user_id
        JOIN games ON games.id = scores.game_id
        WHERE games.name = ?
        ORDER BY scores.score DESC, scores.date ASC
        LIMIT 1
    ''', (game_name,))
    result = cursor.fetchone()
    conn.close()
    return result  # (pseudo, score, date)


def get_all_time_global_highscore():
    conn = get_conn()
    cursor = conn.cursor()
    # Get all game ids
    cursor.execute('SELECT id FROM games')
    games = cursor.fetchall()
    game_ids = [gid for gid, in games]
    total_games = len(game_ids)
    # Get all users
    cursor.execute('SELECT id, pseudo FROM users')
    users = cursor.fetchall()
    # Get all dates
    cursor.execute('SELECT DISTINCT date FROM scores')
    dates = [row[0] for row in cursor.fetchall()]
    best = {'pseudo': None, 'date': None, 'score': -1}
    for date in dates:
        for user_id, pseudo in users:
            cursor.execute('SELECT game_id, score FROM scores WHERE user_id = ? AND date = ?', (user_id, date))
            scores = cursor.fetchall()
            score_dict = {gid:0 for gid in game_ids}
            for gid, score in scores:
                score_dict[gid] = score
            total = sum(score_dict.values())
            avg = round(total / total_games, 1) if total_games else 0
            if avg > best['score']:
                best = {'pseudo': pseudo, 'date': date, 'score': avg}
    conn.close()
    return best['pseudo'], best['date'], best['score']

def get_user_all_time_global_highscore(discord_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM games')
    games = cursor.fetchall()
    game_ids = [gid for gid, in games]
    total_games = len(game_ids)
    cursor.execute('SELECT id, pseudo FROM users WHERE discord_id = ?', (discord_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None, None, None
    user_id, pseudo = user
    cursor.execute('SELECT DISTINCT date FROM scores WHERE user_id = ?', (user_id,))
    dates = [row[0] for row in cursor.fetchall()]
    best = {'date': None, 'score': -1}
    for date in dates:
        cursor.execute('SELECT game_id, score FROM scores WHERE user_id = ? AND date = ?', (user_id, date))
        scores = cursor.fetchall()
        score_dict = {gid:0 for gid in game_ids}
        for gid, score in scores:
            score_dict[gid] = score
        total = sum(score_dict.values())
        avg = round(total / total_games, 1) if total_games else 0
        if avg > best['score']:
            best = {'date': date, 'score': avg}
    conn.close()
    if best['score'] == -1:
        return pseudo, None, None
    return pseudo, best['date'], best['score']

def get_user_game_highscore(discord_id, game_name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT scores.score, scores.date
        FROM scores
        JOIN users ON users.id = scores.user_id
        JOIN games ON games.id = scores.game_id
        WHERE users.discord_id = ? AND games.name = ?
        ORDER BY scores.score DESC, scores.date ASC
        LIMIT 1
    ''', (discord_id, game_name))
    result = cursor.fetchone()
    conn.close()
    return result  # (score, date)

# Ne s'exécute que si tu fais : python db.py
if __name__ == "__main__":
    reset_db()