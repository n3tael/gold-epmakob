import sqlite3
from datetime import datetime, timezone

db = sqlite3.connect("instance/main.db")
cursor = db.cursor()

def main():
    cleared = 0

    print('Clearing expired tokens...')
    tokens = db.execute('SELECT * FROM tokens').fetchmany();

    for token in tokens:
        print(token)
        if datetime.now(timezone.utc) > datetime.strptime(token[1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc):
            db.execute("DELETE FROM tokens WHERE token = ?", (token[0],))
            db.commit()
            cleared += 1

    print(f'Done! Cleared {cleared} tokens.')

if __name__ == "__main__":
    main()