import sqlite3
import re

def sanitize_photos():
    conn = sqlite3.connect('vibetrip.db')
    c = conn.cursor()
    c.execute("SELECT id, author FROM photos WHERE author LIKE '%<%'")
    rows = c.fetchall()
    print(f"Photos with HTML in author: {len(rows)}")

    fixed = 0
    for pid, auth in rows:
        clean = re.sub(r'<[^>]+>', '', auth)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if not clean:
            clean = 'Wikimedia Commons Contributor'
        c.execute("UPDATE photos SET author = ? WHERE id = ?", (clean, pid))
        fixed += 1

    conn.commit()
    print(f"Successfully sanitized {fixed} photo author strings in vibetrip.db!")

    c.execute("SELECT id, author FROM photos WHERE author LIKE '%<%'")
    remaining = len(c.fetchall())
    print(f"Remaining with HTML: {remaining}")
    conn.close()

if __name__ == '__main__':
    sanitize_photos()
