#!/usr/bin/env python3
"""
Crawl Baseball Savant data for pitcher analysis
"""

import requests
import csv
import io
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PitcherData:
    name: str
    team: str
    ip: float
    pa: int
    era: float
    xera: float
    babip: float
    # From statcast
    k_percent: float = 0
    bb_percent: float = 0
    barrel_percent: float = 0
    hardhit_percent: float = 0
    whiff_percent: float = 0
    chase_percent: float = 0
    gb_percent: float = 0

def crawl_pitcher_data(year=2025, min_pa=1):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 1. Expected Stats (ERA, xERA, BABIP)
    url1 = 'https://baseballsavant.mlb.com/leaderboard/expected_statistics'
    r1 = requests.get(url1, params={'year': year, 'type': 'pitcher', 'min': min_pa, 'csv': 'true'}, headers=headers, timeout=30)
    
    expected_data = {}
    reader1 = csv.DictReader(io.StringIO(r1.text))
    for row in reader1:
        name = row.get('last_name, first_name', '').replace('"', '')
        expected_data[name] = {
            'team': row.get('team', ''),
            'ip': float(row.get('ip', 0) or 0),
            'pa': int(row.get('pa', 0) or 0),
            'era': float(row.get('era', 0) or 0),
            'xera': float(row.get('xera', 0) or 0),
            'babip': float(row.get('babip', 0) or 0),
        }
    
    # 2. Statcast Search for K%, BB%, etc
    url2 = 'https://baseballsavant.mlb.com/leaderboard/statcast'
    r2 = requests.get(url2, params={'year': year, 'type': 'pitcher', 'min': min_pa, 'csv': 'true'}, headers=headers, timeout=30)
    
    reader2 = csv.DictReader(io.StringIO(r2.text))
    for row in reader2:
        name = row.get('last_name, first_name', '').replace('"', '')
        if name in expected_data:
            expected_data[name].update({
                'barrel_percent': float(row.get('brl_percent', 0) or 0),
            })
    
    # 3. Get pitch-level stats (K%, BB%, Whiff%, Chase%)
    url3 = 'https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats'
    r3 = requests.get(url3, params={'year': year, 'type': 'pitcher', 'min': min_pa, 'csv': 'true'}, headers=headers, timeout=30)
    
    if r3.status_code == 200:
        reader3 = csv.DictReader(io.StringIO(r3.text))
        for row in reader3:
            name = row.get('last_name, first_name', '').replace('"', '')
            if name in expected_data:
                expected_data[name].update({
                    'k_percent': float(row.get('k_percent', 0) or 0) * 100,  # Convert to percentage
                    'bb_percent': float(row.get('bb_percent', 0) or 0) * 100,
                    'whiff_percent': float(row.get('whiff_percent', 0) or 0) * 100,
                    'chase_percent': float(row.get('chase_percent', 0) or 0) * 100,
                })
    
    return expected_data

def find_pitchers(data, targets):
    """Find target pitchers in data"""
    results = []
    for full_name, stats in data.items():
        for target in targets:
            if target.lower() in full_name.lower():
                results.append({
                    'name': full_name,
                    **stats
                })
                break
    return results

if __name__ == '__main__':
    targets = ['Poulin', 'Pallante', 'Fedde', 'Marquez', 'Civale', 'Suarez', 'Williamson', 'Junk', 'Feltner']
    
    print("Crawling Baseball Savant data...")
    data = crawl_pitcher_data()
    
    print(f"\nFound {len(data)} total pitchers")
    
    found = find_pitchers(data, targets)
    print(f"Found {len(found)} target pitchers:\n")
    
    for p in sorted(found, key=lambda x: x['pa'], reverse=True):
        print(f"{p['name']} | {p.get('team', 'N/A')} | PA: {p['pa']} | IP: {p.get('ip', 0):.1f} | ERA: {p.get('era', 0):.2f} | xERA: {p.get('xera', 0):.2f} | K%: {p.get('k_percent', 0):.1f} | BB%: {p.get('bb_percent', 0):.1f} | Barrel%: {p.get('barrel_percent', 0):.1f} | Whiff%: {p.get('whiff_percent', 0):.1f}")
