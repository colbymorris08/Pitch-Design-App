# ⚾ Pitch Design Automation

**Pitch Design Automation** is a Streamlit-based baseball pitch recommendation tool that blends **nonlinear machine learning** with **expert-driven decision-tree baseball logic** to help pitchers, coaches, and analysts identify missing or improvable pitches in a pitcher’s arsenal.

Note:
-as things stand currently, the working model is deployed in the pdcode.py file and the new additionas are tested in the test.py file to better incorporate predictive machine learning methods and MLB player examples into the model.

This tool is designed as both:
- 🧠 **A teaching device** for MiLB / college coaches  
- 🛠️ **A pitch design assistant** for analysts and player development staff  

---

## 🚀 What This App Does

Given a pitcher’s **fastball traits** and **current offspeed arsenal**, the app:

- Predicts **run value per 100 pitches (RV/100)** using a trained nonlinear ML model
- Identifies **missing or underperforming pitch shapes**
- Recommends **specific pitch types**, not abstract shapes
- Provides **baseball reasoning**, **grip cues**, and **real MLB comps**
- Visualizes the pitcher’s arsenal on an **IVB vs HB movement map**

---

## ✅ Core Features

- ✅ Uses a **nonlinear ML model** to predict run value  
- ✅ Respects **decision-tree baseball logic** (VAA, arm action, command)  
- ✅ Avoids recommending **duplicate movement shapes**  
- ✅ Groups **Changeup / Splitter** correctly (never suggests both)  
- ✅ Enforces **pitch classification constraints** (Slider vs Sweeper, etc.)  
- ✅ Shows **MLB pitcher comps** with matching movement + velocity  
- ✅ Provides **baseball explanations + grip cues**  
- ✅ Fully interactive **Streamlit UI**  

---

## 📂 Data & Model Requirements

This app uses **only two files**:
pitch_movement.csv
pitch_value_model_download.pkl
> ❌ No arsenal CSV is required  
> ❌ No player ID matching is required  

### Required Columns (from `pitch_movement.csv`)
- `last_name, first_name`
- `pitch_type`
- `avg_speed`
- `pitcher_break_z_induced` (IVB)
- `pitcher_break_x` (HB)

---

## 🧠 Baseball Logic Built In

### 1. Vertical Approach Angle (VAA)
VAA is classified as **High** or **Low** based on release height and IVB thresholds.

### 2. Arm Action Classification
- **Pronator**: Fastball spin efficiency ≥ 87%
- **Supinator**: Fastball spin efficiency < 87%

### 3. Seam-Shifted Wake (SSW)
Fastballs with **60–87% spin efficiency** are flagged as SSW-capable.

### 4. Command Guardrails
- ❌ Splitters are **not recommended** if command is *Poor*
- ✅ Changeups are **always suggested** if the pitcher lacks both CH and FS

### 5. Pitch Classification Constraints
- Slider with |HB| > 10" → **Reclassify to Sweeper**
- Sweeper with IVB < –10" → **Reclassify to Curveball**

---

## 🎯 Pitch Recommendation Logic

The app will either:
1. **Recommend a missing pitch** that projects to a good run value  
2. **Suggest improving an existing pitch** with poor predicted RV/100  

### Offspeed Pitch Pool
- Slider  
- Sweeper  
- Changeup  
- Splitter  
- Cutter  
- Curveball  
- Gyro Slider  

Each recommendation includes:
- **Why** the pitch fits the pitcher
- **Suggested grip**
- **Ideal movement + velocity profile**
- **3 MLB pitcher examples** with matching shape

---

## 🧪 MLB Pitcher Comparisons

For every recommended pitch, the app finds up to **3 MLB examples** where:
- Velocity is within ±3 mph  
- IVB is within ±3 inches  
- HB is within ±3 inches  
- Pitch type matches  

These examples are displayed by **pitcher name**, movement, and velocity.

---

## 📊 Visualization

- Interactive **IVB vs HB movement plot**
- Fastball plotted as ⭐
- Existing pitches plotted with labels
- Helps coaches quickly identify:
  - Redundant shapes
  - Missing movement zones
  - Arsenal balance

---

## 🧑‍🏫 Intended Use Cases

- MiLB & college **pitch design education**
- Player development meetings
- Bullpen vs starter pitch planning
- Teaching **movement-based pitch identity**
- Foundation for future:
  - Pitch routine recommendations
  - Starter vs reliever modeling
  - AI pitch design assistants

---

## ▶️ Running the App

```bash
streamlit run test.py
