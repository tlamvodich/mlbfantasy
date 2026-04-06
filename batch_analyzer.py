#!/usr/bin/env python3
"""
Batch Pitcher Analyzer
Nhập list tên pitcher, output phân tích
"""

import sys
from early_season_evaluator import PitcherStats, CareerStats, EarlySeasonEvaluator

def get_pitcher_names():
    """Nhập list tên pitcher từ user"""
    print("⚾ BATCH PITCHER ANALYZER")
    print("=" * 60)
    print("\nNhập tên pitcher (1 dòng 1 tên)")
    print("Gõ 'done' khi xong, hoặc paste list từ clipboard:\n")
    
    pitchers = []
    while True:
        try:
            line = input().strip()
            if line.lower() == 'done':
                break
            if line:
                pitchers.append(line)
        except EOFError:
            break
    
    return pitchers

def create_stat_checklist(pitcher_name):
    """Tạo checklist các stats cần lấy"""
    return f"""
📋 {pitcher_name}
   Lấy từ: baseballsavant.mlb.com/leaderboard/expected_statistics
   
   [ ] Team: ___
   [ ] IP (2025): ___
   [ ] ERA: ___
   [ ] xERA: ___
   [ ] K%: ___
   [ ] BB%: ___
   [ ] Barrel%: ___
   [ ] Hard Hit%: ___
   [ ] Whiff%: ___
   [ ] Chase%: ___
   [ ] Avg Exit Velo: ___
   [ ] BABIP: ___
   [ ] LOB%: ___
   [ ] GB%: ___
   
   Career (2023-24 avg):
   [ ] Career ERA: ___
   [ ] Career xERA: ___
   [ ] Career K%: ___
   [ ] Career BB%: ___
"""

def quick_analysis_template():
    """Template để điền nhanh"""
    template = """
╔════════════════════════════════════════════════════════════╗
║              QUICK INPUT TEMPLATE                          ║
╚════════════════════════════════════════════════════════════╝

Format: Tên | Team | IP | ERA | xERA | K% | BB% | Barrel% | Whiff% | Chase% | BABIP | LOB%

Ví dụ:
Tyler Mahle | TEX | 25.2 | 3.94 | 2.89 | 28.5 | 7.2 | 5.1 | 28.4 | 32.1 | 0.310 | 68.5
Garrett Crochet | BOS | 22.1 | 2.34 | 3.12 | 32.1 | 5.8 | 6.2 | 31.2 | 34.5 | 0.285 | 78.2

Nhập theo format trên (1 dòng 1 pitcher):
"""
    return template

def parse_quick_input(lines):
    """Parse input nhanh từ user"""
    pitchers = []
    
    for line in lines:
        line = line.strip()
        if not line or line.lower() == 'done':
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 10:
            try:
                p = PitcherStats(
                    name=parts[0],
                    team=parts[1],
                    ip_current=float(parts[2]),
                    era_current=float(parts[3]),
                    xera_current=float(parts[4]),
                    k_percent_current=float(parts[5]),
                    bb_percent_current=float(parts[6]),
                    barrel_percent_current=float(parts[7]),
                    hard_hit_percent_current=float(parts[8]) if len(parts) > 8 else 35.0,
                    whiff_percent_current=float(parts[9]),
                    chase_percent_current=float(parts[10]) if len(parts) > 10 else 30.0,
                    avg_exit_velocity_current=float(parts[11]) if len(parts) > 11 else 88.0,
                    babip_current=float(parts[12]) if len(parts) > 12 else 0.290,
                    lob_percent_current=float(parts[13]) if len(parts) > 13 else 72.0,
                    gb_percent_current=float(parts[14]) if len(parts) > 14 else 42.0,
                )
                pitchers.append(p)
                print(f"✅ Đã thêm: {p.name}")
            except (ValueError, IndexError) as e:
                print(f"❌ Lỗi parse: {line} - {e}")
    
    return pitchers

def analyze_list(pitcher_names):
    """Phân tích list pitcher"""
    print("\n" + "=" * 60)
    print("📊 CÁCH NHẬP DATA")
    print("=" * 60)
    print("\n1. QUICK MODE: Paste theo format")
    print("   Tên | Team | IP | ERA | xERA | K% | BB% | Barrel% | Whiff% | Chase% | BABIP | LOB%")
    print("\n2. MANUAL MODE: Nhập từng field")
    print("\nChọn (1/2): ", end="")
    
    choice = input().strip()
    
    evaluator = EarlySeasonEvaluator()
    
    if choice == "1":
        print("\nPaste data (gõ 'done' khi xong):\n")
        lines = []
        while True:
            try:
                line = input()
                if line.strip().lower() == 'done':
                    break
                if line.strip():
                    lines.append(line)
            except EOFError:
                break
        
        pitchers = parse_quick_input(lines)
        for p in pitchers:
            evaluator.add(p)
    
    else:
        # Manual mode
        for name in pitcher_names:
            print(f"\n📊 Nhập data cho {name}:")
            print("-" * 40)
            
            try:
                team = input("Team: ").strip()
                ip = float(input("IP 2025: "))
                era = float(input("ERA: "))
                xera = float(input("xERA: "))
                k = float(input("K%: "))
                bb = float(input("BB%: "))
                barrel = float(input("Barrel%: "))
                hardhit = float(input("Hard Hit%: "))
                whiff = float(input("Whiff%: "))
                chase = float(input("Chase%: "))
                ev = float(input("Avg Exit Velo: "))
                babip = float(input("BABIP: "))
                lob = float(input("LOB%: "))
                gb = float(input("GB%: "))
                
                p = PitcherStats(
                    name=name, team=team, ip_current=ip, era_current=era,
                    xera_current=xera, k_percent_current=k, bb_percent_current=bb,
                    barrel_percent_current=barrel, hard_hit_percent_current=hardhit,
                    whiff_percent_current=whiff, chase_percent_current=chase,
                    avg_exit_velocity_current=ev, babip_current=babip,
                    lob_percent_current=lob, gb_percent_current=gb
                )
                evaluator.add(p)
                print(f"✅ Đã thêm {name}")
                
            except ValueError as e:
                print(f"❌ Lỗi: {e}")
                continue
    
    # Output report
    if evaluator.pitchers:
        print("\n")
        evaluator.print_report()
        
        # Summary actions
        print("\n" + "=" * 60)
        print("🎯 QUICK ACTIONS SUMMARY")
        print("=" * 60)
        
        buy_lows = evaluator.buy_lows()
        sell_highs = evaluator.sell_highs()
        breakouts = evaluator.breakout_candidates()
        
        if buy_lows:
            print("\n💰 BUY LOW (Trade for):")
            for p in buy_lows:
                print(f"   • {p.name} - {p.early_season_verdict()}")
        
        if sell_highs:
            print("\n🎰 SELL HIGH (Trade away):")
            for p in sell_highs:
                print(f"   • {p.name} - {p.early_season_verdict()}")
        
        if breakouts:
            print("\n📈 BREAKOUT WATCH:")
            for p in breakouts:
                print(f"   • {p.name} - Skills improving!")
        
        # Save option
        save = input("\n\n💾 Lưu report? (y/n): ").strip().lower()
        if save == 'y':
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pitcher_analysis_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("MLB PITCHER ANALYSIS REPORT\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                for p in evaluator.pitchers:
                    f.write(p.detailed_analysis())
                    f.write("\n" + "="*60 + "\n")
            
            print(f"✅ Đã lưu: {filename}")

def print_checklist_only(pitcher_names):
    """Chỉ in checklist để user tự điền"""
    print("\n" + "=" * 60)
    print("📋 STAT CHECKLIST")
    print("=" * 60)
    print("Lấy từ: baseballsavant.mlb.com/leaderboard/expected_statistics")
    print("Và: baseballsavant.mlb.com/leaderboard/statcast")
    print()
    
    for name in pitcher_names:
        print(create_stat_checklist(name))
    
    print("\n" + "=" * 60)
    print("💡 TIPS:")
    print("   - xERA quan trọng hơn ERA")
    print("   - BABIP > .320 = unlucky")
    print("   - LOB% > 80% = lucky")
    print("   - Whiff% > 28% = good swing-and-miss")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--checklist":
        # Mode chỉ in checklist
        names = get_pitcher_names()
        if names:
            print_checklist_only(names)
    else:
        # Full analysis mode
        names = get_pitcher_names()
        if names:
            analyze_list(names)
        else:
            print("Không có pitcher nào được nhập.")
