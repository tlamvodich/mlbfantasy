#!/usr/bin/env python3
"""
MLB Pitcher Evaluator
Crawl và evaluate pitchers dựa trên Baseball Savant metrics
"""

import json
import csv
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum

class PitcherTier(Enum):
    ACE = "Ace"
    SP2 = "SP2"
    SP3 = "SP3"
    STREAMER = "Streamer"
    AVOID = "Avoid"

@dataclass
class PitcherStats:
    name: str
    team: str
    ip: float
    era: float
    xera: float
    k_percent: float
    bb_percent: float
    barrel_percent: float
    hard_hit_percent: float
    whiff_percent: float
    chase_percent: float
    avg_exit_velocity: float
    
    def k_bb_ratio(self) -> float:
        """K-BB% - one of the best predictors"""
        return self.k_percent - self.bb_percent
    
    def skill_score(self) -> float:
        """Tổng hợp điểm skill (0-100)"""
        score = 0
        
        # K-BB% (weight cao nhất)
        k_bb = self.k_bb_ratio()
        if k_bb >= 20: score += 30
        elif k_bb >= 15: score += 25
        elif k_bb >= 10: score += 20
        elif k_bb >= 5: score += 15
        else: score += max(0, k_bb)
        
        # xERA vs ERA (luck indicator)
        era_diff = self.era - self.xera
        if era_diff > 1.0: score += 15  # Unlucky
        elif era_diff > 0.5: score += 10
        elif era_diff > -0.5: score += 5
        else: score += 0  # Lucky or bad
        
        # Barrel% (hard contact allowed)
        if self.barrel_percent <= 5: score += 20
        elif self.barrel_percent <= 7: score += 15
        elif self.barrel_percent <= 9: score += 10
        else: score += max(0, 20 - self.barrel_percent)
        
        # Whiff% (swing and miss ability)
        if self.whiff_percent >= 30: score += 20
        elif self.whiff_percent >= 25: score += 15
        elif self.whiff_percent >= 20: score += 10
        else: score += max(0, self.whiff_percent / 2)
        
        # Chase% (stuff outside zone)
        if self.chase_percent >= 35: score += 15
        elif self.chase_percent >= 30: score += 10
        elif self.chase_percent >= 25: score += 5
        else: score += max(0, self.chase_percent / 5)
        
        return min(100, score)
    
    def get_tier(self) -> PitcherTier:
        score = self.skill_score()
        if score >= 80: return PitcherTier.ACE
        elif score >= 65: return PitcherTier.SP2
        elif score >= 50: return PitcherTier.SP3
        elif score >= 35: return PitcherTier.STREAMER
        else: return PitcherTier.AVOID
    
    def analysis(self) -> str:
        """Phân tích chi tiết"""
        lines = []
        lines.append(f"📊 {self.name} ({self.team})")
        lines.append(f"   Tier: {self.get_tier().value} | Score: {self.skill_score():.1f}/100")
        lines.append("")
        
        # ERA vs xERA
        era_diff = self.era - self.xera
        if era_diff > 0.5:
            lines.append(f"   ✅ Đang xui: ERA {self.era:.2f} > xERA {self.xera:.2f}")
        elif era_diff < -0.5:
            lines.append(f"   ⚠️ Đang may: ERA {self.era:.2f} < xERA {self.xera:.2f}")
        else:
            lines.append(f"   ➡️ ERA xấp xỉ xERA ({self.era:.2f})")
        
        # K-BB
        k_bb = self.k_bb_ratio()
        if k_bb >= 15:
            lines.append(f"   ✅ Elite K-BB%: {k_bb:.1f}%")
        elif k_bb >= 10:
            lines.append(f"   ➡️ Good K-BB%: {k_bb:.1f}%")
        elif k_bb >= 5:
            lines.append(f"   ⚠️ Average K-BB%: {k_bb:.1f}%")
        else:
            lines.append(f"   ❌ Poor K-BB%: {k_bb:.1f}%")
        
        # Barrel
        if self.barrel_percent <= 6:
            lines.append(f"   ✅ Great barrel%: {self.barrel_percent:.1f}%")
        elif self.barrel_percent <= 9:
            lines.append(f"   ➡️ OK barrel%: {self.barrel_percent:.1f}%")
        else:
            lines.append(f"   ❌ High barrel%: {self.barrel_percent:.1f}%")
        
        # Whiff
        if self.whiff_percent >= 28:
            lines.append(f"   ✅ Swing & miss: {self.whiff_percent:.1f}% whiff")
        elif self.whiff_percent >= 22:
            lines.append(f"   ➡️ Decent whiff: {self.whiff_percent:.1f}%")
        else:
            lines.append(f"   ⚠️ Low whiff: {self.whiff_percent:.1f}%")
        
        lines.append("")
        return "\n".join(lines)


class PitcherEvaluator:
    def __init__(self):
        self.pitchers: List[PitcherStats] = []
    
    def add_pitcher(self, stats: PitcherStats):
        self.pitchers.append(stats)
    
    def rank_by_skill(self) -> List[PitcherStats]:
        return sorted(self.pitchers, key=lambda p: p.skill_score(), reverse=True)
    
    def find_buy_low(self) -> List[PitcherStats]:
        """Tìm pitcher đang xui (ERA > xERA nhiều) nhưng skill tốt"""
        candidates = []
        for p in self.pitchers:
            if p.era - p.xera > 1.0 and p.skill_score() >= 50:
                candidates.append(p)
        return sorted(candidates, key=lambda p: p.era - p.xera, reverse=True)
    
    def find_sell_high(self) -> List[PitcherStats]:
        """Tìm pitcher đang may (ERA < xERA nhiều)"""
        candidates = []
        for p in self.pitchers:
            if p.xera - p.era > 1.0 and p.era < 3.5:
                candidates.append(p)
        return sorted(candidates, key=lambda p: p.xera - p.era, reverse=True)
    
    def find_streamers(self) -> List[PitcherStats]:
        """Tìm waiver wire pickups tiềm năng"""
        return [p for p in self.pitchers if p.get_tier() == PitcherTier.SP3 and p.skill_score() >= 55]
    
    def print_report(self):
        print("=" * 60)
        print("🏆 TOP PITCHERS BY SKILL")
        print("=" * 60)
        for i, p in enumerate(self.rank_by_skill()[:10], 1):
            print(f"{i}. {p.name} ({p.team}) - {p.get_tier().value} - {p.skill_score():.1f}")
        
        print("\n" + "=" * 60)
        print("💰 BUY LOW (Unlucky but Skilled)")
        print("=" * 60)
        buy_lows = self.find_buy_low()
        if buy_lows:
            for p in buy_lows[:5]:
                print(f"• {p.name}: ERA {p.era:.2f} vs xERA {p.xera:.2f} | Score: {p.skill_score():.1f}")
        else:
            print("Không tìm thấy buy low candidates")
        
        print("\n" + "=" * 60)
        print("⚠️ SELL HIGH (Lucky)")
        print("=" * 60)
        sell_highs = self.find_sell_high()
        if sell_highs:
            for p in sell_highs[:5]:
                print(f"• {p.name}: ERA {p.era:.2f} vs xERA {p.xera:.2f}")
        else:
            print("Không tìm thấy sell high candidates")
        
        print("\n" + "=" * 60)
        print("🎯 WAIVER WIRE TARGETS")
        print("=" * 60)
        streamers = self.find_streamers()
        if streamers:
            for p in streamers[:5]:
                print(f"• {p.name} ({p.team}) - Score: {p.skill_score():.1f}")
        else:
            print("Không tìm thấy streamer targets")


# Sample data - thay bằng real data từ crawl
SAMPLE_PITCHERS = [
    PitcherStats("Tyler Mahle", "TEX", 45.2, 3.94, 2.89, 28.5, 7.2, 5.1, 35.2, 28.4, 32.1, 87.5),
    PitcherStats("Garrett Crochet", "BOS", 42.1, 2.34, 3.12, 32.1, 5.8, 6.2, 38.5, 31.2, 34.5, 88.2),
    PitcherStats("Pablo Lopez", "MIN", 48.0, 3.75, 3.45, 26.8, 4.5, 7.8, 32.1, 25.4, 30.8, 89.1),
]

if __name__ == "__main__":
    evaluator = PitcherEvaluator()
    
    # Add sample data
    for p in SAMPLE_PITCHERS:
        evaluator.add_pitcher(p)
    
    evaluator.print_report()
    
    # Print detailed analysis
    print("\n" + "=" * 60)
    print("📋 DETAILED ANALYSIS")
    print("=" * 60)
    for p in evaluator.rank_by_skill()[:5]:
        print(p.analysis())
