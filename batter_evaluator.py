#!/usr/bin/env python3
"""
MLB Batter Evaluator - Baseball Savant
Phân tích hitters để tìm buy low/sell high và upside
"""

import requests
import csv
import io
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class BatterStats:
    name: str
    team: str
    pa: int
    avg: float
    xavg: float  # Expected BA
    slg: float
    xslg: float  # Expected SLG
    woba: float
    xwoba: float  # Expected wOBA
    barrel_percent: float
    hardhit_percent: float
    avg_exit_velocity: float
    max_exit_velocity: float
    sprint_speed: float  # For SB upside
    chase_percent: float  # Plate discipline
    whiff_percent: float
    bb_percent: float
    k_percent: float
    
    def avg_luck(self) -> float:
        """xBA - BA, positive = unlucky (buy low)"""
        return self.xavg - self.avg
    
    def slg_luck(self) -> float:
        """xSLG - SLG, positive = unlucky (power buy low)"""
        return self.xslg - self.slg
    
    def woba_luck(self) -> float:
        """xwOBA - wOBA, positive = unlucky (buy low)"""
        return self.xwoba - self.woba
    
    def is_unlucky(self) -> bool:
        """Check if batter is underperforming (buy low)"""
        return self.woba_luck() > 0.020  # 20+ points
    
    def is_lucky(self) -> bool:
        """Check if batter is overperforming (sell high)"""
        return self.woba_luck() < -0.020  # 20+ points
    
    def power_upside(self) -> str:
        """Evaluate power upside"""
        if self.barrel_percent >= 12:
            return "ELITE POWER"
        elif self.barrel_percent >= 9:
            return "GOOD POWER"
        elif self.barrel_percent >= 6:
            return "AVERAGE POWER"
        else:
            return "WEAK POWER"
    
    def speed_upside(self) -> str:
        """Evaluate speed/SB upside"""
        if self.sprint_speed >= 29:
            return "ELITE SPEED"
        elif self.sprint_speed >= 28:
            return "GOOD SPEED"
        elif self.sprint_speed >= 27:
            return "AVERAGE SPEED"
        else:
            return "SLOW"
    
    def plate_discipline(self) -> str:
        """Evaluate plate discipline"""
        if self.chase_percent <= 25 and self.whiff_percent <= 20:
            return "EXCELLENT"
        elif self.chase_percent <= 28 and self.whiff_percent <= 25:
            return "GOOD"
        elif self.chase_percent <= 32:
            return "AVERAGE"
        else:
            return "POOR"
    
    def overall_upside(self) -> str:
        """Overall upside assessment"""
        scores = []
        
        # Power (Barrel%)
        if self.barrel_percent >= 12:
            scores.append(3)
        elif self.barrel_percent >= 9:
            scores.append(2)
        elif self.barrel_percent >= 6:
            scores.append(1)
        else:
            scores.append(0)
        
        # Speed
        if self.sprint_speed >= 29:
            scores.append(3)
        elif self.sprint_speed >= 28:
            scores.append(2)
        elif self.sprint_speed >= 27:
            scores.append(1)
        else:
            scores.append(0)
        
        # Plate discipline
        if self.chase_percent <= 25:
            scores.append(2)
        elif self.chase_percent <= 30:
            scores.append(1)
        else:
            scores.append(0)
        
        # Hard hit
        if self.hardhit_percent >= 45:
            scores.append(2)
        elif self.hardhit_percent >= 40:
            scores.append(1)
        else:
            scores.append(0)
        
        total = sum(scores)
        
        if total >= 8:
            return "HIGH UPSIDE"
        elif total >= 5:
            return "MODERATE UPSIDE"
        elif total >= 3:
            return "LIMITED UPSIDE"
        else:
            return "LOW UPSIDE"
    
    def analysis(self) -> str:
        """Full analysis report"""
        lines = []
        lines.append(f"📊 {self.name} ({self.team}) - {self.pa} PA")
        lines.append("")
        
        # Luck indicators
        avg_luck = self.avg_luck()
        slg_luck = self.slg_luck()
        woba_luck = self.woba_luck()
        
        lines.append("🍀 LUCK INDICATORS:")
        lines.append(f"   BA: {self.avg:.3f} vs xBA: {self.xavg:.3f} ({avg_luck:+.3f})")
        lines.append(f"   SLG: {self.slg:.3f} vs xSLG: {self.xslg:.3f} ({slg_luck:+.3f})")
        lines.append(f"   wOBA: {self.woba:.3f} vs xwOBA: {self.xwoba:.3f} ({woba_luck:+.3f})")
        
        if self.is_unlucky():
            lines.append("   ✅ BUY LOW - Underperforming expected stats!")
        elif self.is_lucky():
            lines.append("   🎰 SELL HIGH - Overperforming, will regress!")
        else:
            lines.append("   ➡️ Performing to expected")
        
        lines.append("")
        lines.append("⚾ SKILL METRICS:")
        lines.append(f"   Barrel%: {self.barrel_percent:.1f}% ({self.power_upside()})")
        lines.append(f"   Hard Hit%: {self.hardhit_percent:.1f}%")
        lines.append(f"   Exit Velo: {self.avg_exit_velocity:.1f} mph (max: {self.max_exit_velocity:.1f})")
        lines.append(f"   Sprint Speed: {self.sprint_speed:.1f} ft/s ({self.speed_upside()})")
        lines.append(f"   Chase%: {self.chase_percent:.1f}% | Whiff%: {self.whiff_percent:.1f}%")
        lines.append(f"   BB%: {self.bb_percent:.1f}% | K%: {self.k_percent:.1f}%")
        lines.append(f"   Plate Discipline: {self.plate_discipline()}")
        
        lines.append("")
        lines.append(f"📈 UPSIDE: {self.overall_upside()}")
        
        # Recommendation
        lines.append("")
        lines.append("🎯 RECOMMENDATION:")
        
        if self.is_unlucky() and self.overall_upside() in ["HIGH UPSIDE", "MODERATE UPSIDE"]:
            lines.append("   ⭐⭐⭐ STRONG BUY - Unlucky + High upside!")
        elif self.is_unlucky():
            lines.append("   ⭐⭐ BUY LOW - Underperforming")
        elif self.is_lucky() and self.overall_upside() == "LOW UPSIDE":
            lines.append("   🗑️ DROP - Lucky + No upside")
        elif self.is_lucky():
            lines.append("   🎰 SELL HIGH - Overperforming")
        elif self.overall_upside() == "HIGH UPSIDE":
            lines.append("   ✅ HOLD - High upside potential")
        else:
            lines.append("   ➡️ HOLD - Replace if better option available")
        
        lines.append("")
        return "\n".join(lines)


def crawl_batter_data(year=2026, min_pa=1):
    """Crawl Baseball Savant batter data"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Expected stats
    url = 'https://baseballsavant.mlb.com/leaderboard/expected_statistics'
    params = {'year': year, 'type': 'batter', 'min': min_pa, 'csv': 'true'}
    
    r = requests.get(url, params=params, headers=headers, timeout=30)
    reader = csv.reader(io.StringIO(r.text))
    header = next(reader)
    
    # Index mapping
    # Expected columns: name, pa, bip, ba, est_ba, slg, est_slg, woba, est_woba, ...
    
    batters = {}
    for row in reader:
        if len(row) < 18:
            continue
        
        name = row[0].replace('"', '')
        try:
            batters[name] = {
                'team': row[2] if len(row) > 2 else 'N/A',
                'pa': int(row[3]) if row[3].isdigit() else 0,
                'ba': float(row[5]) if row[5] else 0,
                'xba': float(row[6]) if row[6] else 0,
                'slg': float(row[8]) if row[8] else 0,
                'xslg': float(row[9]) if row[9] else 0,
                'woba': float(row[11]) if row[11] else 0,
                'xwoba': float(row[12]) if row[12] else 0,
            }
        except (ValueError, IndexError):
            continue
    
    # Get exit velocity data
    url2 = 'https://baseballsavant.mlb.com/leaderboard/statcast'
    params2 = {'year': year, 'type': 'batter', 'min': min_pa, 'csv': 'true'}
    
    r2 = requests.get(url2, params=params2, headers=headers, timeout=30)
    reader2 = csv.reader(io.StringIO(r2.text))
    next(reader2)  # Skip header
    
    for row in reader2:
        if len(row) < 10:
            continue
        
        name = row[0].replace('"', '')
        if name in batters:
            try:
                batters[name].update({
                    'avg_ev': float(row[7]) if row[7] else 0,  # avg_hit_speed
                    'max_ev': float(row[6]) if row[6] else 0,  # max_hit_speed
                    'barrel': float(row[17]) if len(row) > 17 and row[17] else 0,
                })
            except (ValueError, IndexError):
                pass
    
    return batters


def quick_batter_analysis(names: List[str]):
    """Quick analysis for list of batter names"""
    data = crawl_batter_data()
    
    found = {}
    for full_name, stats in data.items():
        for target in names:
            if target.lower() in full_name.lower():
                found[full_name] = stats
                break
    
    print(f"Found {len(found)} batters:\n")
    
    for name, s in sorted(found.items(), key=lambda x: x[1]['pa'], reverse=True):
        ba = s.get('ba', 0)
        xba = s.get('xba', 0)
        slg = s.get('slg', 0)
        xslg = s.get('xslg', 0)
        woba = s.get('woba', 0)
        xwoba = s.get('xwoba', 0)
        barrel = s.get('barrel', 0)
        
        xba_diff = xba - ba
        xwoba_diff = xwoba - woba
        
        status = []
        if xwoba_diff > 0.020:
            status.append("🟢 UNLUCKY (Buy)")
        elif xwoba_diff < -0.020:
            status.append("🔴 LUCKY (Sell)")
        
        if barrel >= 12:
            status.append("💪 ELITE POWER")
        elif barrel >= 9:
            status.append("👍 GOOD POWER")
        
        print(f"{name} ({s.get('team', 'N/A')}) - {s['pa']} PA")
        print(f"   BA: {ba:.3f} vs xBA: {xba:.3f} ({xba_diff:+.3f})")
        print(f"   wOBA: {woba:.3f} vs xwOBA: {xwoba:.3f} ({xwoba_diff:+.3f})")
        print(f"   Barrel%: {barrel:.1f}%")
        if status:
            print(f"   {' | '.join(status)}")
        print()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        names = sys.argv[1:]
        quick_batter_analysis(names)
    else:
        print("Usage: python3 batter_evaluator.py 'Player1' 'Player2' ...")
