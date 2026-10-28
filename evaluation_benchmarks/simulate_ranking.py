import sqlite3

def simulate():
    conn = sqlite3.connect('vibetrip.db')
    c = conn.cursor()
    c.execute("SELECT destination, nature, adventure, peacefulness, crowd_match, visual_atmosphere FROM vibe_scores")
    rows = c.fetchall()
    
    # user filters from image:
    # Nature: Med, Adventure: High, Peace: Med, Crowd: Med, Visual: High
    target_dims = {
        'nature': 'medium',
        'adventure': 'high',
        'peacefulness': 'medium',
        'crowd_match': 'medium',
        'visual_atmosphere': 'high'
    }
    
    print("--- CURRENT ARITHMETIC MEAN SCORING ---")
    results = []
    for r in rows:
        dest, nat, adv, peace, crowd, vis = r
        scores = {'nature': nat, 'adventure': adv, 'peacefulness': peace, 'crowd_match': crowd, 'visual_atmosphere': vis}
        overall = 0
        for dim, dir_ in target_dims.items():
            val = scores[dim]
            if dir_ == 'high':
                overall += val
            elif dir_ == 'low':
                overall += (100.0 - val)
            elif dir_ == 'medium':
                overall += max(0.0, 100.0 - 2.0 * abs(val - 50.0))
        results.append((dest, overall / 5.0, scores))
        
    results.sort(key=lambda x: x[1], reverse=True)
    for r in results[:10]:
        print(f"  {r[0]:20} | Total: {r[1]:5.1f}% | Adv: {r[2]['adventure']:5.1f} | Nat: {r[2]['nature']:5.1f} | Vis: {r[2]['visual_atmosphere']:5.1f} | Peace: {r[2]['peacefulness']:5.1f} | Crowd: {r[2]['crowd_match']:5.1f}")
        
    conn.close()

if __name__ == '__main__':
    simulate()
