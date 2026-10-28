import sqlite3

def deduplicate_photos():
    conn = sqlite3.connect('vibetrip.db')
    c = conn.cursor()
    
    # Check total before
    c.execute("SELECT count(*) FROM photos")
    total_before = c.fetchone()[0]
    print(f"Total photos before deduplication: {total_before}")
    
    # We want to keep exactly one entry per (destination, filename).
    # Specifically, keep the minimum id for each (destination, filename).
    c.execute("""
        DELETE FROM photos
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM photos
            GROUP BY destination, filename
        )
    """)
    deleted = c.rowcount
    conn.commit()
    
    c.execute("SELECT count(*) FROM photos")
    total_after = c.fetchone()[0]
    print(f"Deleted {deleted} duplicate photo rows.")
    print(f"Total photos after deduplication: {total_after}")
    
    # Verify no duplicates remain
    c.execute("""
        SELECT destination, filename, count(*) 
        FROM photos 
        GROUP BY destination, filename 
        HAVING count(*) > 1
    """)
    duplicates = c.fetchall()
    if duplicates:
        print(f"WARNING: Still found duplicates: {len(duplicates)}")
    else:
        print("Verification SUCCESS: All destinations have unique photo copies only!")
        
    conn.close()

if __name__ == '__main__':
    deduplicate_photos()
