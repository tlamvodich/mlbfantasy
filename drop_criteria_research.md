# BATTER DROP CRITERIA - Baseball Savant Analysis
# Nghiên cứu các ngưỡng stats để drop batter

## I. SAMPLE SIZE RULES (Quan trọng nhất)

### Đừng drop khi:
- **< 20 PA**: Hoàn toàn meaningless, noise > signal
- **20-50 PA**: Cẩn thận, chỉ drop nếu playing time bị cắt/injured
- **> 50 PA**: Bắt đầu đánh giá được

### Exception (Drop ngay dù ít PA):
- Prospect bị send xuống minors
- Mất starting job (platoon/bench)
- Injury dài hạn không có IL spot

---

## II. LUCK INDICATORS (Buy Low vs Sell High vs Drop)

### 2.1 xwOBA Differential (quan trọng nhất)
- **xwOBA - wOBA > +0.030**: Very unlucky → BUY/HOLD
- **xwOBA - wOBA > +0.020**: Unlucky → BUY/HOLD  
- **xwOBA - wOBA < -0.020**: Lucky → SELL HIGH
- **xwOBA - wOBA < -0.030**: Very lucky → DROP nếu kết hợp skill tệ

### 2.2 xBA Differential
- **xBA - BA > +0.050**: Very unlucky
- **xBA - BA > +0.030**: Unlucky
- **xBA - BA < -0.030**: Lucky, regression sắp đến

### 2.3 xSLG Differential  
- **xSLG - SLG > +0.080**: Power unlucky
- **xSLG - SLG < -0.080**: Power lucky, home run fluky

---

## III. SKILL INDICATORS (Drop nếu kém)

### 3.1 Barrel% (Power)
- **≥ 12%**: Elite power - giữ dù unlucky
- **9-12%**: Good power - giữ
- **6-9%**: Average - xem xét context
- **< 6%**: Weak power - **DROP nếu không có speed/discipline**
- **< 4%**: No power - **DEFINITE DROP** (trừ khi elite speed + defense)

### 3.2 Hard Hit%
- **≥ 45%**: Elite contact quality
- **40-45%**: Good
- **35-40%**: Average  
- **< 35%**: Poor - **DROP nếu kết hợp low barrel**

### 3.3 Exit Velocity
- **≥ 92 mph**: Elite
- **90-92 mph**: Good
- **88-90 mph**: Average
- **< 88 mph**: Weak - **DROP nếu không có other tools**

---

## IV. PLATE DISCIPLINE (Drop nếu tệ)

### 4.1 Chase% (ngoài zone)
- **< 25%**: Excellent discipline - giữ
- **25-30%**: Good
- **30-35%**: Average
- **> 35%**: Poor - **DROP nếu K% cao**
- **> 40%**: Terrible - **DEFINITE DROP**

### 4.2 Whiff% (swing and miss)
- **< 20%**: Excellent contact
- **20-25%**: Good
- **25-30%**: Average
- **> 30%**: Poor - **DROP nếu không có elite power**
- **> 35%**: Terrible - **DEFINITE DROP**

### 4.3 K% / BB%
- **K% > 30%**: Warning, **DROP nếu không có elite power**
- **K% > 35%**: Definite drop (unless Ohtani/Acuna tier)
- **BB% < 5% + K% > 25%**: **DROP** - không kiểm soát zone

---

## V. SPEED UPSIDE (Giữ nếu tốt)

### Sprint Speed (ft/s)
- **≥ 29.0**: Elite - giữ dù hitting tệ (SB upside)
- **28.0-29.0**: Good speed - xem xét
- **27.0-28.0**: Average
- **< 27.0**: Slow - **DROP nếu không có power**

---

## VI. DROP DECISION MATRIX

### VI.1 DEFINITE DROP (Drop ngay):
1. **> 50 PA** + **Barrel% < 4%** + **xwOBA < wOBA** (lucky + no power)
2. **> 50 PA** + **Chase% > 40%** + **K% > 30%** (no discipline)
3. **> 50 PA** + **xBA < .200** + **Barrel% < 5%** + **Speed < 27**
4. Prospect bị send minors
5. Mất starting job (platoon chính)

### VI.2 BORDERLINE (Drop nếu cần spot):
1. **30-50 PA** + **Barrel% 4-6%** + **xwOBA < wOBA** (lucky + weak power)
2. **> 50 PA** + **Chase% 35-40%** + **Barrel% < 7%**
3. **> 50 PA** + **Exit Velo < 88 mph** + **Speed < 27**

### VI.3 HOLD (Đừng drop):
1. **< 30 PA** - wait thêm
2. **Barrel% > 10%** dù unlucky - power will play
3. **Speed > 29 ft/s** - SB upside giữ giá trị
4. **xwOBA > wOBA + 0.030** - unlucky, sẽ bounce back

### VI.4 STRONG BUY (Add nếu free agent):
1. **xwOBA > wOBA + 0.040** + **Barrel% > 10%** + **> 50 PA**
2. **xBA > BA + 0.050** + **Hard Hit% > 42%**

---

## VII. VÍ DỤ THỰC TẾ

### Ví dụ 1: Jordan Beck (12 PA)
- Barrel%: 5.6% (weak)
- xBA diff: -.066 (lucky)
- PA: 12
- **Verdict: WAIT** - too early

### Ví dụ 2: Kyle Manzardo (13 PA)
- Barrel%: 3.7% (very weak)
- xBA diff: -.095 (very lucky)
- PA: 13
- **Verdict: WAIT but WATCH** - warning signs nhưng sample nhỏ

### Ví dụ 3: Giả định Player X (60 PA)
- Barrel%: 3.0% (terrible)
- xBA: .180 vs BA: .220 (lucky)
- Chase%: 38% (poor)
- Speed: 26.5 ft/s (slow)
- **Verdict: DEFINITE DROP** - lucky + no power + no discipline + slow

---

## VIII. CHECKLIST TRƯỚC KHI DROP

- [ ] PA > 50? (Nếu < 50, chờ thêm)
- [ ] Barrel% < 6%? (Nếu > 10%, giữ)
- [ ] xwOBA < wOBA? (Nếu xwOBA > wOBA, có thể unlucky)
- [ ] Playing time ổn định? (Nếu bench/platoon, xem xét)
- [ ] Speed < 27 và Barrel% < 6%? (Nếu có 1 cái tốt, giữ)

---

## IX. EXCEPTIONS

### Giữ dù stats tệ:
1. **Catcher** - position scarcity
2. **Prospect top 20** - adjustment period cho phép
3. **Speed demon** (> 29 ft/s) - SB category giữ giá trị
4. **Veteran proven track record** - slumps tạm thờI

### Drop dù stats tốt:
1. **Injured** (không IL spot)
2. **Sent to minors**
3. **Lost playing time** (bench/platoon)

---

## X. TÓM TẮT

**DROP khi có ≥3 điều:**
1. > 50 PA
2. Barrel% < 6%
3. xBA < BA (lucky)
4. Speed < 27
5. Chase% > 35%

**HOLD khi có ≥1 điều:**
1. < 30 PA
2. Barrel% > 10%
3. Speed > 29
4. xBA > BA + .030 (unlucky)
