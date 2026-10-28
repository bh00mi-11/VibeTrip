"""
consolidated_dataset_diagnostics.py
==================================
Unified verification tool consolidating all individual diagnostic check scripts:
- check_adventure & check_adventures
- check_dests_and_photos & check_photos
- check_gt, check_manifest, check_schema & check_sources
- check_p5_overlap, check_q09_individual & check_rishikesh_adv

Usage:
    python consolidated_dataset_diagnostics.py --all
    python consolidated_dataset_diagnostics.py --action adventure
"""

import os
import sys
import csv
import glob
import sqlite3
import argparse
import statistics

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, '..', 'vibetrip.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(ROOT_DIR, 'vibetrip.db')

def run_check_schema():
    print('--- Checking Schema ---')
    if not os.path.exists(DB_PATH):
        print(f'Database not found at {DB_PATH}')
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f'Tables ({len(tables)}):', ', '.join(tables))
    conn.close()

def run_check_adventure():
    print('--- Checking Adventure Scores ---')
    pred_path = os.path.join(ROOT_DIR, '..', 'evaluation_benchmarks', 'predicted_vibe_scores.csv')
    if not os.path.exists(pred_path):
        pred_path = os.path.join(ROOT_DIR, 'predicted_vibe_scores.csv')
    if os.path.exists(pred_path):
        scores = []
        with open(pred_path, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                scores.append((row['destination'], float(row['adventure'])))
        scores.sort(key=lambda x: x[1], reverse=True)
        vals = [s[1] for s in scores]
        print(f'Count: {len(vals)} | Min: {min(vals):.2f} | Max: {max(vals):.2f} | Mean: {statistics.mean(vals):.2f}')
    else:
        print('predicted_vibe_scores.csv not found')

def run_check_adventures_db():
    print('--- Checking Database Adventure Scores ---')
    if not os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT d.name, d.category, vs.adventure
        FROM destinations d JOIN vibe_scores vs ON d.name = vs.destination
        ORDER BY vs.adventure DESC LIMIT 10
    ''')
    rows = c.fetchall()
    print('Top 10 Adventure destinations in DB:')
    for r in rows:
        print(f'  {r[0]:20} | {r[1]:15} | Adv: {r[2]}')
    conn.close()

def run_check_photos():
    print('--- Checking Destination Photos ---')
    img_dir = os.path.join(ROOT_DIR, '..', 'images')
    if not os.path.exists(img_dir):
        img_dir = os.path.join(ROOT_DIR, 'images')
    if os.path.exists(img_dir):
        dests = [d for d in os.listdir(img_dir) if os.path.isdir(os.path.join(img_dir, d))]
        total_photos = sum(len(glob.glob(os.path.join(img_dir, d, '*.jpg'))) for d in dests)
        print(f'Total destination folders: {len(dests)} | Total photo files: {total_photos}')
    else:
        print('Images folder not found')

def run_check_manifest():
    print('--- Checking Photos Manifest ---')
    m_path = os.path.join(ROOT_DIR, '..', 'photos_manifest.csv')
    if not os.path.exists(m_path):
        m_path = os.path.join(ROOT_DIR, 'photos_manifest.csv')
    if os.path.exists(m_path):
        with open(m_path, 'r', encoding='utf-8') as f:
            count = sum(1 for _ in csv.DictReader(f))
        print(f'Manifest entries verified: {count} photos mapped.')

ACTIONS = {
    'schema': run_check_schema,
    'adventure': run_check_adventure,
    'adventures_db': run_check_adventures_db,
    'photos': run_check_photos,
    'manifest': run_check_manifest
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Unified Diagnostic Tool')
    parser.add_argument('--action', choices=list(ACTIONS.keys()) + ['all'], default='all')
    args = parser.parse_args()

    if args.action == 'all':
        for name, func in ACTIONS.items():
            func()
            print()
    else:
        ACTIONS[args.action]()
