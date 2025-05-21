from db import *

if __name__ == "__main__":


    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    print("Users:")
    print("ID | Discord ID | Pseudo")
    print("-------------------------")
    for row in rows:
        print(row)
        
    cursor.execute("SELECT * FROM games")
    rows = cursor.fetchall()
    print("\nGames:")
    print("ID | Name | Channel ID")
    print("-------------------------")
    for row in rows:
        print(row)
        
    cursor.execute("SELECT * FROM scores")
    rows = cursor.fetchall()
    conn.close()
    print("\nScores:")
    print("ID | User ID | Game ID | Date | Score")
    print("-------------------------")
    for row in rows:
        print(row)
        
        
        
    

    
