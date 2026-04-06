#!/usr/bin/env python3
"""
Baseball Savant Pitcher Crawler
Lấy data pitching từ Baseball Savant
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from pitcher_evaluator import PitcherStats, PitcherEvaluator

class BaseballSavantCrawler:
    BASE_URL = "https://baseballsavant.mlb.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_expected_stats(self, year: int = 2025, min_pa: int = 100) -> List[Dict]:
        """
        Lấy expected stats từ Baseball Savant API
        """
        url = f"{self.BASE_URL}/leaderboard/expected_statistics"
        
        # URL parameters cho pitcher data
        params = {
            'year': year,
            'type': 'pitcher',  # or 'batter'
            'min': min_pa,
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse HTML table hoặc tìm JSON data
            # Baseball Savant có thể trả về HTML hoặc có API endpoint
            return self._parse_leaderboard(response.text)
            
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
    
    def _parse_leaderboard(self, html: str) -> List[Dict]:
        """
        Parse HTML từ leaderboard để lấy data
        Note: Có thể cần dùng BeautifulSoup hoặc tìm API endpoint thật
        """
        # TODO: Implement proper parsing
        # Baseball Savant có thể có hidden API hoặc cần browser automation
        return []
    
    def get_statcast_search(self, query_params: Dict) -> List[Dict]:
        """
        Sử dụng Statcast Search để lấy custom data
        """
        url = f"{self.BASE_URL}/statcast_search"
        
        try:
            response = self.session.get(url, params=query_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return []


def manual_input_evaluator():
    """
    Dùng khi chưa có crawler - nhập tay data từ Baseball Savant
    """
    print("🏟️ MLB PITCHER EVALUATOR")
    print("=" * 60)
    print("\nNhập thông tin pitcher (hoặc 'done' để kết thúc):\n")
    
    evaluator = PitcherEvaluator()
    
    while True:
        name = input("Tên pitcher (hoặc 'done'): ").strip()
        if name.lower() == 'done':
            break
        
        try:
            print(f"\n📊 Nhập stats cho {name}:")
            print("(Lấy từ: baseballsavant.mlb.com/leaderboard/expected_statistics)\n")
            
            team = input("Team: ").strip()
            ip = float(input("Innings Pitched (IP): "))
            era = float(input("ERA: "))
            xera = float(input("xERA: "))
            k_pct = float(input("K%: "))
            bb_pct = float(input("BB%: "))
            barrel_pct = float(input("Barrel%: "))
            hard_hit_pct = float(input("Hard Hit%: "))
            whiff_pct = float(input("Whiff%: "))
            chase_pct = float(input("Chase%: "))
            avg_ev = float(input("Avg Exit Velocity (mph): "))
            
            pitcher = PitcherStats(
                name=name, team=team, ip=ip, era=era, xera=xera,
                k_percent=k_pct, bb_percent=bb_pct, barrel_percent=barrel_pct,
                hard_hit_percent=hard_hit_pct, whiff_percent=whiff_pct,
                chase_percent=chase_pct, avg_exit_velocity=avg_ev
            )
            
            evaluator.add_pitcher(pitcher)
            print(f"\n✅ Đã thêm {name} - Tier: {pitcher.get_tier().value}\n")
            
        except ValueError as e:
            print(f"❌ Lỗi nhập liệu: {e}")
            continue
    
    if evaluator.pitchers:
        print("\n")
        evaluator.print_report()
        
        # Save to file
        save = input("\n\n💾 Lưu report? (y/n): ").strip().lower()
        if save == 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pitcher_eval_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("MLB PITCHER EVALUATION REPORT\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write("=" * 60 + "\n\n")
                
                for p in evaluator.rank_by_skill():
                    f.write(p.analysis())
                    f.write("\n")
            
            print(f"✅ Đã lưu: {filename}")
    else:
        print("Không có pitcher nào được thêm.")


def quick_evaluate(pitcher_name: str, stats_dict: Dict) -> str:
    """
    Quick evaluate 1 pitcher từ dict
    """
    p = PitcherStats(**stats_dict)
    return p.analysis()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        manual_input_evaluator()
    else:
        print("Usage:")
        print("  python3 pitcher_crawler.py --manual    # Nhập data tay")
        print("\nĐể crawl tự động, cần:")
        print("1. Baseball Savant API key (nếu có)")
        print("2. Hoặc dùng browser automation (selenium/playwright)")
