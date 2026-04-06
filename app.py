import streamlit as st
import requests
import csv
import io

st.set_page_config(page_title="MLB Fantasy Analyzer", layout="wide")

st.title("⚾ MLB Fantasy Baseball Analyzer")
st.subheader("Baseball Savant Data - Pitcher & Batter Analysis")

# Sidebar for options
st.sidebar.header("Options")
analysis_type = st.sidebar.radio("Select Type:", ["Batter", "Pitcher"])

# FIXED: Better name matching function
def normalize_name(name):
    """Normalize name for better matching"""
    return name.lower().replace(',', '').replace(' ', '').replace('.', '')

# Function to crawl Baseball Savant for batters
def get_batter_data(name, year=2026):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Expected stats
    url = 'https://baseballsavant.mlb.com/leaderboard/expected_statistics'
    params = {'year': year, 'type': 'batter', 'min': '1', 'csv': 'true'}
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        reader = csv.reader(io.StringIO(r.text))
        next(reader)
        
        search_clean = normalize_name(name)
        
        for row in reader:
            if len(row) < 15:
                continue
            player_name = row[0].replace('"', '')
            player_clean = normalize_name(player_name)
            
            # Match if search is in player name OR player name in search
            if search_clean in player_clean or player_clean in search_clean:
                return {
                    'name': player_name,
                    'pa': int(row[4]) if row[4].isdigit() else 0,
                    'ba': float(row[6]) if row[6] else 0,
                    'xba_diff': float(row[7]) if row[7] else 0,
                    'slg': float(row[9]) if row[9] else 0,
                    'xslg_diff': float(row[10]) if row[10] else 0,
                    'woba': float(row[12]) if row[12] else 0,
                    'xwoba_diff': float(row[13]) if row[13] else 0,
                }
        return None
    except Exception as e:
        return {'error': str(e)}

# Function to get exit velocity data
def get_ev_data(name, year=2026):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = 'https://baseballsavant.mlb.com/leaderboard/statcast'
    params = {'year': year, 'type': 'batter', 'min': '1', 'csv': 'true'}
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        reader = csv.reader(io.StringIO(r.text))
        next(reader)
        
        search_clean = normalize_name(name)
        
        for row in reader:
            if len(row) < 18:
                continue
            player_name = row[0].replace('"', '')
            player_clean = normalize_name(player_name)
            
            if search_clean in player_clean or player_clean in search_clean:
                return {
                    'avg_ev': float(row[7]) if row[7] else 0,
                    'max_ev': float(row[6]) if row[6] else 0,
                    'barrel': float(row[17]) if len(row) > 17 and row[17] else 0,
                }
        return None
    except:
        return None

# Function to analyze batter
def analyze_batter(data, ev_data):
    if not data:
        return "❌ Player not found. Try:\n- 'Ohtani' instead of 'Shohei Ohtani'\n- 'Judge' instead of 'Aaron Judge'\n- Or just last name"
    
    if 'error' in data:
        return f"❌ Error: {data['error']}"
    
    pa = data['pa']
    ba = data['ba']
    xba = ba + data['xba_diff']
    woba = data['woba']
    xwoba = woba + data['xwoba_diff']
    slg = data['slg']
    xslg = slg + data['xslg_diff']
    
    barrel = ev_data['barrel'] if ev_data else 0
    avg_ev = ev_data['avg_ev'] if ev_data else 0
    max_ev = ev_data['max_ev'] if ev_data else 0
    
    # Analysis
    results = []
    results.append(f"### 📊 {data['name']}")
    results.append(f"**PA:** {pa}")
    
    # Luck section
    results.append("\n### 🍀 Luck Indicators")
    results.append(f"- **BA:** {ba:.3f} vs xBA: {xba:.3f} (diff: {data['xba_diff']:+.3f})")
    results.append(f"- **SLG:** {slg:.3f} vs xSLG: {xslg:.3f}")
    results.append(f"- **wOBA:** {woba:.3f} vs xwOBA: {xwoba:.3f} (diff: {data['xwoba_diff']:+.3f})")
    
    # Luck verdict
    if pa < 20:
        luck = "⚠️ TOO EARLY - <20 PA, meaningless data"
    elif data['xwoba_diff'] > 0.030:
        luck = "🔥 VERY UNLUCKY - Buy low!"
    elif data['xwoba_diff'] > 0.020:
        luck = "✅ UNLUCKY - Should improve"
    elif data['xwoba_diff'] < -0.030:
        luck = "🎰 VERY LUCKY - Will regress hard"
    elif data['xwoba_diff'] < -0.020:
        luck = "⚠️ LUCKY - Some regression expected"
    else:
        luck = "➡️ Performing to expectation"
    results.append(f"\n**Luck Status:** {luck}")
    
    # Skill section
    if ev_data:
        results.append("\n### ⚾ Skill Metrics")
        results.append(f"- **Barrel%:** {barrel:.1f}%")
        results.append(f"- **Avg Exit Velo:** {avg_ev:.1f} mph")
        results.append(f"- **Max Exit Velo:** {max_ev:.1f} mph")
        
        if barrel >= 12:
            power = "💪 ELITE POWER"
        elif barrel >= 9:
            power = "👍 GOOD POWER"
        elif barrel >= 6:
            power = "➡️ AVERAGE POWER"
        else:
            power = "⚠️ WEAK POWER"
        results.append(f"- **Power:** {power}")
    
    # Final recommendation
    results.append("\n### 🎯 Recommendation")
    
    if pa < 20:
        rec = "⏳ WAIT - Too early to judge"
    elif data['xwoba_diff'] > 0.030 and barrel >= 10:
        rec = "⭐⭐⭐ STRONG BUY - Unlucky + Elite power!"
    elif data['xwoba_diff'] > 0.020 and barrel >= 8:
        rec = "⭐⭐ BUY - Unlucky + Good power"
    elif data['xwoba_diff'] < -0.030 and barrel < 6:
        rec = "🗑️ DROP - Lucky + No power"
    elif data['xwoba_diff'] < -0.020 and barrel < 5:
        rec = "🎰 SELL HIGH - Regression coming"
    elif barrel >= 10:
        rec = "✅ HOLD - Elite power"
    else:
        rec = "➡️ BORDERLINE - Monitor closely"
    
    results.append(rec)
    
    # Drop criteria check
    results.append("\n### 📋 Drop Criteria Check")
    
    checks = []
    if pa > 50 and barrel < 6 and data['xwoba_diff'] < -0.020:
        checks.append("❌ DROP: Lucky + No power + Enough PA")
    if pa < 20:
        checks.append("⚠️ Don't drop yet - Small sample")
    if barrel >= 10:
        checks.append("✅ Keep - Elite barrel%")
    if data['xwoba_diff'] > 0.030:
        checks.append("✅ Buy low - Very unlucky")
    
    if checks:
        results.append("\n".join(checks))
    else:
        results.append("➡️ Monitor situation")
    
    return "\n".join(results)

# Main interface
if analysis_type == "Batter":
    st.header("Batter Analysis")
    
    player_name = st.text_input("Enter player name:", placeholder="e.g., Ohtani, Judge, or Bogaerts")
    
    st.caption("💡 Tip: Try last name only if full name doesn't work")
    
    if st.button("Analyze"):
        if player_name:
            with st.spinner("Fetching data from Baseball Savant..."):
                data = get_batter_data(player_name)
                ev_data = get_ev_data(player_name)
                
                if data:
                    result = analyze_batter(data, ev_data)
                    st.markdown(result)
                else:
                    st.error(f"❌ Could not find '{player_name}'")
                    st.info("💡 Try:\n- Using last name only (e.g., 'Ohtani' instead of 'Shohei Ohtani')\n- Check spelling\n- Player may not have enough PA in 2026")
        else:
            st.warning("Please enter a player name")
    
    st.markdown("---")
    st.markdown("### 📚 How to interpret:")
    st.markdown("""
    **Luck Indicators:**
    - **Unlucky (xBA > BA)**: Hitting well but ball finding gloves → BUY
    - **Lucky (xBA < BA)**: Getting cheap hits → SELL
    
    **Skill Metrics:**
    - **Barrel% > 10%**: Elite power → Hold regardless of luck
    - **Barrel% < 5%**: Weak power → Drop if also lucky
    
    **Sample Size:**
    - **< 20 PA**: Too early, meaningless
    - **> 50 PA**: Reliable data
    """)

else:
    st.header("Pitcher Analysis")
    st.info("Pitcher analysis coming soon! Currently only Batter analysis is available.")
    
    st.markdown("### 📋 Drop Criteria for Pitchers:")
    st.markdown("""
    **DEFINITE DROP:**
    - ERA > xERA by 1.00+ (unlucky) + Barrel% > 10% (getting hit hard)
    - K-BB% < 10% (poor command)
    
    **BUY LOW:**
    - ERA > xERA by 1.00+ but Barrel% < 6% (unlucky not bad)
    """)

st.markdown("---")
st.caption("Data from Baseball Savant | Built with Streamlit | Updated 2026")
