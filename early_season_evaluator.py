#!/usr/bin/env python3
"""
MLB Early Season Pitcher Evaluator
Xử lý sample size nhỏ đầu mùa với career baseline
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from enum import Enum

class SampleReliability(Enum):
    HIGH = "✅ High"        # > 30 IP
    MEDIUM = "⚠️ Medium"    # 15-30 IP  
    LOW = "❌ Low"          # < 15 IP - mostly noise

@dataclass
class CareerStats:
    """Career baseline để so sánh"""
    era: float
    xera: float
    k_percent: float
    bb_percent: float
    barrel_percent: float
    whiff_percent: float
    ip_per_season: float

@dataclass
class PitcherStats:
    name: str
    team: str
    ip_current: float  # IP this season
    era_current: float
    xera_current: float
    k_percent_current: float
    bb_percent_current: float
    barrel_percent_current: float
    hard_hit_percent_current: float
    whiff_percent_current: float
    chase_percent_current: float
    avg_exit_velocity_current: float
    babip_current: float
    lob_percent_current: float  # Left on base %
    gb_percent_current: float   # Ground ball %
    
    # Career baseline (2023-2024)
    career: Optional[CareerStats] = None
    
    def sample_reliability(self) -> SampleReliability:
        """Đánh giá độ tin cậy của sample"""
        if self.ip_current >= 30:
            return SampleReliability.HIGH
        elif self.ip_current >= 15:
            return SampleReliability.MEDIUM
        else:
            return SampleReliability.LOW
    
    def k_bb_ratio(self) -> float:
        return self.k_percent_current - self.bb_percent_current
    
    def era_luck(self) -> float:
        """ERA vs xERA diff - positive = unlucky"""
        return self.era_current - self.xera_current
    
    def babip_luck(self) -> float:
        """
        BABIP luck indicator
        League avg ~.290, pitchers usually regress to .280-.300 range
        """
        league_avg_babip = 0.290
        return self.babip_current - league_avg_babip
    
    def lob_luck(self) -> float:
        """
        LOB% luck indicator
        League avg ~72%, sustainable range 70-75%
        """
        league_avg_lob = 72.0
        return self.lob_percent_current - league_avg_lob
    
    def is_lucky(self) -> bool:
        """Check nếu đang may mắn nhiều"""
        return (self.era_luck() < -1.0 and 
                self.babip_luck() < -0.020 and 
                self.lob_luck() > 5.0)
    
    def is_unlucky(self) -> bool:
        """Check nếu đang xui xẻo nhiều"""
        return (self.era_luck() > 1.0 and 
                self.babip_luck() > 0.020 and 
                self.lob_luck() < -5.0)
    
    def skill_change_vs_career(self) -> Dict[str, float]:
        """So sánh với career baseline"""
        if not self.career:
            return {}
        
        return {
            'k_delta': self.k_percent_current - self.career.k_percent,
            'bb_delta': self.bb_percent_current - self.career.bb_percent,
            'barrel_delta': self.barrel_percent_current - self.career.barrel_percent,
            'whiff_delta': self.whiff_percent_current - self.career.whiff_percent,
        }
    
    def breakout_indicators(self) -> List[str]:
        """Signals cho legitimate breakout (không phải luck)"""
        indicators = []
        changes = self.skill_change_vs_career()
        
        if not changes:
            return ["⚠️ No career data for comparison"]
        
        # Positive skill changes
        if changes.get('k_delta', 0) > 3:
            indicators.append("✅ K% up >3% - real stuff improvement")
        if changes.get('bb_delta', 0) < -2:
            indicators.append("✅ BB% down >2% - better command")
        if changes.get('whiff_delta', 0) > 3:
            indicators.append("✅ Whiff% up - new pitch/more velo?")
        if changes.get('barrel_delta', 0) < -2:
            indicators.append("✅ Barrel% down - better contact management")
        
        # Velocity increase (cần data riêng)
        
        return indicators if indicators else ["➡️ No major skill changes vs career"]
    
    def decline_indicators(self) -> List[str]:
        """Signals cho decline thật"""
        indicators = []
        changes = self.skill_change_vs_career()
        
        if not changes:
            return []
        
        if changes.get('k_delta', 0) < -3:
            indicators.append("❌ K% down >3% - velo drop?")
        if changes.get('bb_delta', 0) > 2:
            indicators.append("❌ BB% up >2% - command issues")
        if changes.get('barrel_delta', 0) > 2:
            indicators.append("❌ Barrel% up - getting hit harder")
        
        return indicators
    
    def early_season_verdict(self) -> str:
        """Verdict tổng hợp cho early season"""
        reliability = self.sample_reliability()
        
        if reliability == SampleReliability.LOW:
            return "⏳ TOO EARLY - <15 IP, mostly noise"
        
        # Check luck extremes
        if self.is_lucky():
            return "🎰 LUCKY - Sell high candidate"
        if self.is_unlucky():
            return "🎯 UNLUCKY - Buy low candidate"
        
        # Check skill changes
        breakouts = self.breakout_indicators()
        declines = self.decline_indicators()
        
        if len(breakouts) >= 2 and not declines:
            return "📈 BREAKOUT? - Skills improved, legit?"
        if len(declines) >= 2 and not breakouts:
            return "📉 DECLINE - Skills down, concerning"
        
        return "➡️ STEADY - Performing to expectations"
    
    def detailed_analysis(self) -> str:
        """Phân tích chi tiết cho early season"""
        lines = []
        lines.append(f"📊 {self.name} ({self.team}) - {self.ip_current:.1f} IP")
        lines.append(f"   Verdict: {self.early_season_verdict()}")
        lines.append(f"   Sample: {self.sample_reliability().value}")
        lines.append("")
        
        # Current vs Expected
        lines.append(f"📈 LUCK INDICATORS:")
        lines.append(f"   ERA: {self.era_current:.2f} vs xERA: {self.xera_current:.2f}")
        
        era_diff = self.era_luck()
        if abs(era_diff) > 1.0:
            direction = "UNLUCKY" if era_diff > 0 else "LUCKY"
            lines.append(f"   → {direction} by {abs(era_diff):.2f} runs")
        
        lines.append(f"   BABIP: {self.babip_current:.3f} (league avg ~.290)")
        babip_luck = self.babip_luck()
        if abs(babip_luck) > 0.020:
            direction = "high" if babip_luck > 0 else "low"
            lines.append(f"   → {direction} BABIP = {direction} luck")
        
        lines.append(f"   LOB%: {self.lob_percent_current:.1f}% (league avg ~72%)")
        lob_luck = self.lob_luck()
        if abs(lob_luck) > 5:
            direction = "stranding more" if lob_luck > 0 else "stranding fewer"
            lines.append(f"   → {direction} runners than avg")
        
        # Skill metrics
        lines.append("")
        lines.append(f"⚾ SKILL METRICS:")
        lines.append(f"   K%: {self.k_percent_current:.1f}% | BB%: {self.bb_percent_current:.1f}%")
        lines.append(f"   K-BB%: {self.k_bb_ratio():.1f}%")
        lines.append(f"   Whiff%: {self.whiff_percent_current:.1f}% | Chase%: {self.chase_percent_current:.1f}%")
        lines.append(f"   Barrel%: {self.barrel_percent_current:.1f}% | Hard Hit%: {self.hard_hit_percent_current:.1f}%")
        
        # Career comparison
        if self.career:
            lines.append("")
            lines.append(f"🔄 vs CAREER:")
            changes = self.skill_change_vs_career()
            for metric, delta in changes.items():
                arrow = "↑" if delta > 0 else "↓"
                lines.append(f"   {metric.replace('_delta', '')}: {arrow} {delta:+.1f}")
            
            breakouts = self.breakout_indicators()
            if breakouts:
                lines.append("")
                lines.append("🔥 BREAKOUT SIGNALS:")
                for sig in breakouts:
                    lines.append(f"   {sig}")
            
            declines = self.decline_indicators()
            if declines:
                lines.append("")
                lines.append("⚠️ DECLINE SIGNALS:")
                for sig in declines:
                    lines.append(f"   {sig}")
        
        # Action recommendation
        lines.append("")
        lines.append(f"🎯 RECOMMENDATION:")
        verdict = self.early_season_verdict()
        
        if "TOO EARLY" in verdict:
            lines.append("   Wait 2-3 more starts trước khi kết luận")
        elif "LUCKY" in verdict:
            lines.append("   SELL HIGH - ERA sẽ regression lên")
        elif "UNLUCKY" in verdict:
            lines.append("   BUY LOW - xERA thấp hơn ERA thực")
        elif "BREAKOUT" in verdict:
            lines.append("   HOLD/BUY - Skills thực sự cải thiện")
        elif "DECLINE" in verdict:
            lines.append("   SELL/DROP - Skills xuống, không phải bad luck")
        else:
            lines.append("   HOLD - Performing as expected")
        
        lines.append("")
        return "\n".join(lines)


class EarlySeasonEvaluator:
    def __init__(self):
        self.pitchers: List[PitcherStats] = []
    
    def add(self, p: PitcherStats):
        self.pitchers.append(p)
    
    def buy_lows(self) -> List[PitcherStats]:
        """Find unlucky pitchers with good skills"""
        candidates = [p for p in self.pitchers if p.is_unlucky()]
        return sorted(candidates, key=lambda p: p.era_luck(), reverse=True)
    
    def sell_highs(self) -> List[PitcherStats]:
        """Find lucky pitchers"""
        candidates = [p for p in self.pitchers if p.is_lucky()]
        return sorted(candidates, key=lambda p: p.era_luck())
    
    def breakout_candidates(self) -> List[PitcherStats]:
        """Find pitchers with real skill improvement"""
        candidates = []
        for p in self.pitchers:
            if p.sample_reliability() == SampleReliability.LOW:
                continue
            breakouts = p.breakout_indicators()
            if len(breakouts) >= 2 and not p.is_lucky():
                candidates.append(p)
        return candidates
    
    def print_report(self):
        print("=" * 70)
        print("⚾ EARLY SEASON PITCHER REPORT (2025)")
        print("=" * 70)
        print("\n🎯 BUY LOW (Unlucky but skilled):")
        print("-" * 50)
        for p in self.buy_lows()[:5]:
            print(f"   • {p.name} ({p.team}): ERA {p.era_current:.2f} vs xERA {p.xera_current:.2f}")
        
        print("\n🎰 SELL HIGH (Lucky):")
        print("-" * 50)
        for p in self.sell_highs()[:5]:
            print(f"   • {p.name} ({p.team}): ERA {p.era_current:.2f} vs xERA {p.xera_current:.2f}")
        
        print("\n📈 BREAKOUT? (Skills improved):")
        print("-" * 50)
        for p in self.breakout_candidates()[:5]:
            print(f"   • {p.name} ({p.team}): {len(p.breakout_indicators())} positive indicators")
        
        print("\n" + "=" * 70)
        print("📋 DETAILED ANALYSIS")
        print("=" * 70)
        for p in self.pitchers:
            print(p.detailed_analysis())


# Example usage with early season data
if __name__ == "__main__":
    evaluator = EarlySeasonEvaluator()
    
    # Example: Add your pitchers here
    # evaluator.add(PitcherStats(...))
    
    evaluator.print_report()
