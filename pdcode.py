import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pitch Design Automation", layout="wide")
st.title("⚾️ Pitch Design Automation")

# ---------------- Sidebar Inputs ----------------
st.sidebar.header("Pitcher Inputs")

handedness = st.sidebar.selectbox("Handedness", ["RHP", "LHP"])
level = st.sidebar.selectbox("Level", ["MLB", "NPB", "MiLB", "Other Pro", "College", "High School"])
role = st.sidebar.selectbox("Role", ["Starter", "Reliever"])
command = st.sidebar.selectbox("Command", ["Good", "Medium", "Poor"])

release_height = st.sidebar.slider("Release Height (ft)", 4.0, 7.0, 5.5, 0.1)
extension = st.sidebar.slider("Extension (ft)", 4.0, 8.0, 6.5, 0.1)

fb_velocity = st.sidebar.slider("Fastball Velocity (mph)", 85, 102, 94)
fb_spin_eff = st.sidebar.slider("Fastball Spin Efficiency (%)", 60, 100, 90)
fb_spin_rate = st.sidebar.slider("Fastball Spin Rate (rpm)", 1800, 3500, 2400)

fb_type = st.sidebar.selectbox("Fastball Type", ["Four-Seam", "Two-Seam"])
fb_ivb = st.sidebar.slider("Fastball IVB (in)", 0.0, 25.0, 17.0, 0.5)
fb_hb = st.sidebar.slider("Fastball HB (in)", -20.0, 20.0, 6.0, 0.5)

# ---------------- Derived Fastball Traits ----------------

# Seam-Shifted Wake
ssw = "Yes" if (60 < fb_spin_eff < 87) else "No"

# VAA
if (
    (fb_ivb > 12 and release_height < 5.0) or
    (fb_ivb > 14 and release_height < 5.5) or
    (fb_ivb > 17 and 5.5 <= release_height <= 6.1) or
    (fb_ivb > 19 and release_height > 6.1)
):
    vaa = "High"
else:
    vaa = "Low"

# Pronator vs Supinator
arm_action = "Pronator" if fb_spin_eff >= 87 else "Supinator"

# ---------------- Existing Arsenal ----------------
st.header("📌 Existing Offspeed Pitches")

existing = []
pitch_types = ["Slider", "Sweeper", "Changeup", "Cutter", "Curveball"]
has_pitch_dict = {}

for p in pitch_types:
    has_pitch = st.selectbox(f"Has {p}?", ["No", "Yes"], key=f"has_{p}")
    has_pitch_dict[p] = has_pitch
    if has_pitch == "Yes":
        col1, col2 = st.columns(2)
        hb = col1.slider(f"{p} HB (in)", -20.0, 20.0, 0.0, 0.5, key=f"hb_{p}")
        ivb = col2.slider(f"{p} IVB (in)", -20.0, 20.0, 0.0, 0.5, key=f"ivb_{p}")
        existing.append({"name": p, "hb": hb, "ivb": ivb})

        if p == "Slider" and abs(hb) > 10:
            st.warning(f"⚠️ `{p}` has {hb}'' horizontal break. Please reclassify to **Sweeper**.")
        if p == "Sweeper" and ivb < -10:
            st.warning(f"⚠️ `{p}` has {ivb}'' vertical break. Please reclassify to **Curveball**.")

# ---------------- Decision Tree Logic ----------------
st.header("🎯 Pitch Recommendations")

recommendations = []

def shape_exists(target_hb, target_ivb):
    for p in existing:
        if abs(p["hb"] - target_hb) <= 3 and abs(p["ivb"] - target_ivb) <= 3:
            return True
    return False

# ---- Fastball Type Logic ----
if fb_type == "Two-Seam" and release_height < 5.5 and fb_spin_eff > 70:
    recommendations.append({
        "pitch": "Four-Seam Fastball",
        "why": "Low release height + sufficient spin efficiency → potential High VAA four-seam",
        "grip": "Traditional four-seam grip; fingers across seams and parallel"
    })

if ssw == "Yes" and fb_type == "Four-Seam":
    recommendations.append({
        "pitch": "Two-Seam Fastball",
        "why": "Spin efficiency suggests seam-shifted wake potential",
        "grip": "Two-seam grip with fingers along the seams (parallel)"
    })

# ---- Offspeed Logic ----
if arm_action == "Pronator":
    if not shape_exists(-12 if handedness=="RHP" else 12, 5):
        recommendations.append({
            "pitch": "Sweeper",
            "why": "Pronator profile benefits from horizontal glove-side separation",
            "grip": "Two fingers inside horseshoe or Yankees whirly grip"
        })

    if command == "Good" and level in ["MLB", "NPB", "MiLB", "Other Pro"]:
        recommendations.append({
            "pitch": "Splitter",
            "why": "Good command + pronation supports bottom-of-zone weapon",
            "grip": "Fork grip over 2-seam or 4-seam orientation"
        })

    recommendations.append({
        "pitch": "Gyro Slider",
        "why": "Lower movement pitch improves command consistency",
        "grip": "Spike grip or two-seam orientation with neutral hand"
    })

else:  # Supinator
    recommendations.append({
        "pitch": "Cutter",
        "why": "Supinator profile pairs well with short, hard glove-side movement",
        "grip": "Offset four-seam or two-seam grip; middle finger pressure"
    })

    if not shape_exists(-14 if handedness=="RHP" else 14, 4):
        recommendations.append({
            "pitch": "Sweeper",
            "why": "Natural supination supports east-west shape",
            "grip": "Non-spiked grip on two-seam orientation"
        })

# ---- Command Guardrail ----
if command == "Poor":
    recommendations = [r for r in recommendations if r["pitch"] != "Splitter"]
    if has_pitch_dict["Changeup"] == "No":
        recommendations.append({
            "pitch": "Changeup",
            "why": "Poor command + no current changeup → suggest arm-side offspeed with minimal movement demands",
            "grip": "Two-seam changeup grip (fingers parallel on seams)"
        })

# ---- Reliever Priority ----
if role == "Reliever":
    recommendations = sorted(
        recommendations,
        key=lambda r: 0 if "Slider" in r["pitch"] else 1
    )

recommendations = recommendations[:3]

# ---------------- Output ----------------
if recommendations:
    for i, r in enumerate(recommendations, 1):
        st.success(f"**{i}. {r['pitch']}** — {r['why']}\n\n💡 **Suggested Grip**: {r['grip']}")
else:
    st.warning("No clear pitch recommendations given current inputs.")

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
