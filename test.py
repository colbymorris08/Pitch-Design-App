import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import numpy as np

# ---------------- Load Data ----------------
model = joblib.load("pitch_value_model_download.pkl")
example_df = pd.read_csv("pitch_movement.csv")

# Standardize column names
example_df = example_df.rename(columns={
    "avg_speed": "velo",
    "pitcher_break_z_induced": "ivb",
    "pitcher_break_x": "hb"
})

# Drop rows without necessary data
example_df = example_df.dropna(subset=["last_name, first_name", "pitch_type"])

# ---------------- Helper Functions ----------------
def predict_rv100(velo, ivb, hb):
    return model.predict([[velo, ivb, hb]])[0]

def find_comps(pitch_type, velo, ivb, hb):
    subset = example_df[example_df["pitch_type"].str.lower().str.contains(pitch_type.lower())]
    subset = subset[(subset["velo"].between(velo-3, velo+3)) &
                    (subset["ivb"].between(ivb-3, ivb+3)) &
                    (subset["hb"].between(hb-3, hb+3))]
    return subset.head(3)

def shape_exists(target_hb, target_ivb, tolerance=3):
    for p in existing:
        if abs(p["hb"] - target_hb) <= tolerance and abs(p["ivb"] - target_ivb) <= tolerance:
            return True
    return False

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="Pitch Design Automation", layout="wide")
st.title("⚾️ Pitch Design Automation")

# ---------------- Sidebar Inputs ----------------
st.sidebar.header("Pitcher Inputs")
handedness = st.sidebar.selectbox("Handedness", ["RHP", "LHP"])
level = st.sidebar.selectbox("Level", ["MLB", "NPB", "MiLB", "Other Pro", "College", "High School"])
role = st.sidebar.selectbox("Role", ["Starter", "Reliever"])
command = st.sidebar.selectbox("Command", ["Good", "Medium", "Poor"])

release_height = st.sidebar.slider("Release Height (ft)", 4.0, 7.0, 5.5, 0.1)
fb_velocity = st.sidebar.slider("Fastball Velocity (mph)", 85, 102, 94)
fb_spin_eff = st.sidebar.slider("Fastball Spin Efficiency (%)", 60, 100, 90)
fb_spin_rate = st.sidebar.slider("Fastball Spin Rate (rpm)", 1800, 3500, 2400)
fb_type = st.sidebar.selectbox("Fastball Type", ["Four-Seam", "Two-Seam"])
fb_ivb = st.sidebar.slider("Fastball IVB (in)", 0.0, 25.0, 17.0, 0.5)
fb_hb = st.sidebar.slider("Fastball HB (in)", -20.0, 20.0, 6.0, 0.5)

# ---------------- Derived Traits ----------------
ssw = "Yes" if (60 < fb_spin_eff < 87) else "No"
vaa = "High" if ((fb_ivb > 12 and release_height < 5.0) or
                 (fb_ivb > 14 and release_height < 5.5) or
                 (fb_ivb > 17 and 5.5 <= release_height <= 6.1) or
                 (fb_ivb > 19 and release_height > 6.1)) else "Low"
arm_action = "Pronator" if fb_spin_eff >= 87 else "Supinator"

# ---------------- Existing Arsenal ----------------
st.header("📌 Existing Offspeed Pitches")
pitch_types = ["Slider", "Sweeper", "Changeup", "Splitter", "Cutter", "Curveball"]
has_pitch_dict = {}
existing = []

for p in pitch_types:
    has_pitch = st.selectbox(f"Has {p}?", ["No", "Yes"], key=p)
    has_pitch_dict[p] = has_pitch
    if has_pitch == "Yes":
        hb = st.slider(f"{p} HB", -20.0, 20.0, 0.0, 0.5, key=f"hb_{p}")
        ivb = st.slider(f"{p} IVB", -20.0, 20.0, 0.0, 0.5, key=f"ivb_{p}")
        velo = st.slider(f"{p} Velo", 70.0, 95.0, 85.0, 0.5, key=f"velo_{p}")
        existing.append({"name": p, "hb": hb, "ivb": ivb, "velo": velo})

# ---------------- Decision Logic ----------------
st.header("🎯 Pitch Recommendations")
recommendations = []

# -- Fastball shape suggestions --
if fb_type == "Two-Seam" and release_height < 5.5 and fb_spin_eff > 70:
    recommendations.append({
        "pitch": "Four-Seam Fastball",
        "why": "Low release height + high spin efficiency → potential High VAA four-seam",
        "grip": "Traditional four-seam grip; fingers across seams and parallel"
    })

if ssw == "Yes" and fb_type == "Four-Seam":
    recommendations.append({
        "pitch": "Two-Seam Fastball",
        "why": "Spin efficiency suggests seam-shifted wake potential",
        "grip": "Two-seam grip with fingers along seams"
    })

# -- Offspeed options --
all_options = {
    "Slider": {"hb": -6 if handedness=="RHP" else 6, "ivb": 3, "velo": 85,
               "why": "Low movement slider for command consistency",
               "grip": "Spike grip or two-seam orientation with neutral wrist"},
    "Sweeper": {"hb": -13 if handedness=="RHP" else 13, "ivb": 5, "velo": 83,
                "why": "Adds horizontal glove-side separation",
                "grip": "Yankees Whirly or fingers inside horseshoe"},
    "Changeup": {"hb": 13 if handedness=="RHP" else -13, "ivb": 7, "velo": 83,
                 "why": "Arm-side offspeed with separation",
                 "grip": "Two-seam changeup grip or circle grip"},
    "Splitter": {"hb": 1, "ivb": 3, "velo": 86,
                 "why": "Bottom-of-zone weapon for pronators",
                 "grip": "Fork grip over two-seam or four-seam"},
    "Curveball": {"hb": 4, "ivb": -12, "velo": 78,
                  "why": "Topspin option with vertical depth",
                  "grip": "Spike grip, stay supinated"},
    "Cutter": {"hb": -2 if handedness=="RHP" else 2, "ivb": 6, "velo": 88,
               "why": "Short glove-side shape for supinators",
               "grip": "Offset four-seam or two-seam; middle finger pressure"}
}

# Evaluate missing shapes and filter
for pitch, traits in all_options.items():
    if pitch == "Splitter" and command == "Poor":
        continue  # skip splitter if command is poor

    # group logic: don't suggest CH if FS exists and vice versa
    if (pitch == "Changeup" and has_pitch_dict["Splitter"] == "Yes") or \
       (pitch == "Splitter" and has_pitch_dict["Changeup"] == "Yes"):
        continue

    if has_pitch_dict.get(pitch, "No") == "No" and not shape_exists(traits["hb"], traits["ivb"]):
        pred = predict_rv100(traits["velo"], traits["ivb"], traits["hb"])
        if pred < 0:  # good performance shape
            comps = find_comps(pitch, traits["velo"], traits["ivb"], traits["hb"])
            mlb_examples = [
                f"{row['last_name, first_name']} — {row['velo']} mph, {row['ivb']} IVB, {row['hb']} HB"
                for _, row in comps.iterrows()
            ]
            recommendations.append({
                "pitch": pitch,
                "why": traits["why"],
                "grip": traits["grip"],
                "rv100": pred,
                "examples": mlb_examples
            })

# Last resort: suggest improving a bad pitch
if not recommendations:
    for pitch in existing:
        pred = predict_rv100(pitch["velo"], pitch["ivb"], pitch["hb"])
        if pred > 2:
            recommendations.append({
                "pitch": f"Improve {pitch['name']}",
                "why": "High predicted RV/100 indicates poor effectiveness",
                "grip": "Work with pitching coach on movement consistency",
                "rv100": pred,
                "examples": []
            })

# Reliever priority
if role == "Reliever":
    recommendations = sorted(recommendations, key=lambda r: 0 if "Slider" in r["pitch"] else 1)

# Show top 3
for i, rec in enumerate(recommendations[:3], 1):
    st.subheader(f"{i}. {rec['pitch']}")
    st.markdown(f"**Run Value (RV/100):** `{rec['rv100']:.2f}`")
    st.markdown(f"**Why:** {rec['why']}")
    st.markdown(f"💡 **Grip Cue:** {rec['grip']}")
    if rec["examples"]:
        st.markdown("**MLB Examples:**")
        for e in rec["examples"]:
            st.markdown(f"- {e}")

# ---------------- Arsenal Plot ----------------
st.header("📊 Arsenal Map")
fig, ax = plt.subplots(figsize=(5, 5))
ax.axhline(0, color="gray", lw=0.5)
ax.axvline(0, color="gray", lw=0.5)
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)

# Fastball
ax.scatter(fb_hb, fb_ivb, c="red", s=150, marker="*", label="Fastball")

# Existing
for p in existing:
    ax.scatter(p["hb"], p["ivb"], label=p["name"])

ax.set_xlabel("Horizontal Break (in)")
ax.set_ylabel("Induced Vertical Break (in)")
ax.set_title("Pitch Movement Map")
ax.legend()
st.pyplot(fig)
