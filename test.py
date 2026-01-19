import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Title
st.title("Pitch Design Automation")

# Load data
df = pd.read_csv("/Users/colbymorris/Downloads/arsenal_clustered_data.csv")

# Filter out known bad pitch shape
df = df[~((df['avg_speed'].round(1) == 89.0) &
          (df['pitcher_break_z_induced'].round(1) == 15.9) &
          (df['pitcher_break_x'].round(1) == 7.1))]

# Pitch classification
def classify_pitch_shape(ivb, hb, handedness):
    if 10 <= ivb <= 20 and ((0 <= hb <= 12 and handedness == 'RHP') or (-12 <= hb <= 0 and handedness == 'LHP')):
        return 'Four-Seam Fastball'
    elif -5 <= ivb <= 5 and -5 <= hb <= 5:
        return 'Slider'
    elif -5 <= ivb <= 10 and ((hb < -8 and handedness == 'RHP') or (hb > 8 and handedness == 'LHP')):
        return 'Sweeper'
    elif -5 <= ivb <= 10 and ((hb > 8 and handedness == 'RHP') or (hb < -8 and handedness == 'LHP')):
        return 'Changeup'
    else:
        return 'Other'

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    handedness = st.selectbox("Handedness", ["RHP", "LHP"])
    level = st.selectbox("Player Level", ["MLB", "NPB", "MiLB", "Other Pro", "College", "High School"])
    release_height = st.slider("Release Height (ft)", 4.0, 7.0, 5.3)
    spin_eff = st.slider("Spin Efficiency (%)", 0, 100, 92)
    command = st.selectbox("Command", ["Good", "Medium", "Poor"])

with col2:
    fb_type = st.selectbox("Fastball Type", ["Four-Seam", "Two-Seam"])
    fb_vel = st.slider("Fastball Velocity (mph)", 80.0, 100.0, 94.0)
    fb_ivb = st.slider("Fastball IVB (in)", 0.0, 20.0, 17.5)
    fb_hb = st.slider("Fastball HB (in)", -20.0, 20.0, 5.5)

# --- EXISTING OFFSPEED PITCHES ---
st.subheader("Current Offspeed Pitches")
existing_arsenal = []
for i in range(4):
    pitch_type = st.selectbox(f"Pitch Type {i+1}", ["None", "Changeup", "Slider", "Sweeper", "Other"], key=f"type_{i}")
    ivb = st.slider(f"IVB for {pitch_type}", -20.0, 20.0, 0.0, key=f"ivb_{i}")
    hb = st.slider(f"HB for {pitch_type}", -20.0, 20.0, 0.0, key=f"hb_{i}")
    if pitch_type != "None":
        existing_arsenal.append({
            "type": pitch_type,
            "ivb": ivb,
            "hb": hb
        })

# Determine pitch identity
df["shape_type"] = df.apply(lambda r: classify_pitch_shape(r["pitcher_break_z_induced"],
                                                           r["pitcher_break_x"],
                                                           handedness), axis=1)

# Filter out shapes already in arsenal
def is_similar(ivb, hb, velo, existing, fb_ivb, fb_hb, fb_vel):
    for p in existing:
        if abs(ivb - p["ivb"]) < 3 and abs(hb - p["hb"]) < 3:
            return True
    if abs(ivb - fb_ivb) < 3 and abs(hb - fb_hb) < 3 and abs(velo - fb_vel) < 3:
        return True
    return False

# Apply base constraints
filtered_df = df[
    (df["avg_speed"] <= fb_vel - 5) &
    (~df.apply(lambda r: is_similar(r["pitcher_break_z_induced"],
                                    r["pitcher_break_x"],
                                    r["avg_speed"],
                                    existing_arsenal,
                                    fb_ivb, fb_hb, fb_vel), axis=1)) &
    (df["shape_type"] != "Four-Seam Fastball")
]

# Apply advanced constraints
def is_valid(row):
    if command == "Poor" and row["pitch_name"] == "Splitter":
        return False
    return True

filtered_df = filtered_df[filtered_df.apply(is_valid, axis=1)]

# Rank suggestions by lowest run value
suggest = filtered_df.sort_values("run_value_per_100").head(1)

# --- CHART ---
st.subheader("Pitch Arsenal Chart")
fig, ax = plt.subplots()
ax.axhline(0, color='gray', linestyle='--')
ax.axvline(0, color='gray', linestyle='--')
ax.scatter(fb_hb, fb_ivb, c='red', marker='*', s=200, label="Fastball")

for pitch in existing_arsenal:
    ax.scatter(pitch["hb"], pitch["ivb"], label=pitch["type"])

if not suggest.empty:
    sug = suggest.iloc[0]
    sug_ivb = sug["pitcher_break_z_induced"]
    sug_hb = sug["pitcher_break_x"]
    sug_vel = sug["avg_speed"]
    sug_name = sug["pitch_name"]
    ax.scatter(sug_hb, sug_ivb, c='green', marker='x', s=150, label="Suggested")
    st.success(f"**Suggested Pitch**: {sug_name}\n- **Velo**: {sug_vel:.1f} mph\n- **IVB**: {sug_ivb:.1f}\" \n- **HB**: {sug_hb:.1f}\"")
else:
    st.warning("No suitable pitch suggestion found. Try adjusting your inputs.")

ax.set_xlabel("Horizontal Break (in)")
ax.set_ylabel("Induced Vertical Break (in)")
ax.set_title("IVB vs HB Arsenal Map")
ax.legend()
st.pyplot(fig)
