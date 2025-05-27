from db import add_game, add_user, add_score, reset_db

def setup_test_db():
    reset_db()
    # Test server channels
    add_game("wordle", "1374794459136655421")
    add_game("timeguessr", "1374794493395599440")
    add_game("framed", "1375155452836315207")
    add_game("angle", "1375157615423655966")
    add_game("worldle", "1375160528837808259")
    add_game("hexle", "1375160592251490315")
    # Add test users
    add_user("123456789", "TestUser")
    add_user("521317397060255744", "Arthur")
    add_user("987654321", "Alice")
    add_user("111111111", "Bob")
    # Add test scores (simulate different days and games)
    add_score("123456789", "TestUser", "wordle", "2025-06-15", 80)
    add_score("123456789", "TestUser", "timeguessr", "2025-06-15", 60)
    add_score("521317397060255744", "Arthur", "wordle", "2025-06-15", 90)
    add_score("521317397060255744", "Arthur", "framed", "2025-06-15", 70)
    add_score("987654321", "Alice", "wordle", "2025-06-15", 100)
    add_score("987654321", "Alice", "angle", "2025-06-15", 95)
    add_score("111111111", "Bob", "worldle", "2025-06-15", 85)
    add_score("111111111", "Bob", "hexle", "2025-06-15", 75)
    # Add scores for another day
    add_score("123456789", "TestUser", "wordle", "2025-06-16", 60)
    add_score("521317397060255744", "Arthur", "timeguessr", "2025-06-16", 80)
    add_score("987654321", "Alice", "framed", "2025-06-16", 90)
    add_score("111111111", "Bob", "angle", "2025-06-16", 70)

if __name__ == "__main__":
    setup_test_db() 