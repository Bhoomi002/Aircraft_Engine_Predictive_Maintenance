import streamlit as st
import numpy as np
import pandas as pd
import os
import sqlite3
import matplotlib.pyplot as plt
import warnings
from datetime import date, datetime

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Aircraft Engine RUL Prediction", page_icon="✈️", layout="wide")

# --- Styling and Configuration ---
st.markdown("""
<style>
    /* General Styles */
    .st-emotion-cache-1r65z4z { border-radius: 0.5rem; }

    /* Centered login card */
    div[data-testid="stVerticalBlock"] > div:has(> form) {
        max-width: 450px;
        margin: 0 auto;
        padding: 20px 25px;
        background-color: #111827;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }

    /* Sidebar specific styling */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
        border-right: 2px solid #e0e0e0;
        color: #333333;
    }
    .sidebar-profile-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .profile-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 10px;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 5px;
    }
    .profile-info {
        font-size: 0.9rem;
        margin-bottom: 5px;
        color: #555555;
    }
    .stButton>button {
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton button[data-testid*="secondary"] {
        background-color: #333333;
        color: white !important;
        border: 1px solid #333333;
    }

    /* Force login-page title to stay on one line */
    .login-hero h1 {
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# ========== AUTHENTICATION CONFIG ==========
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# ---------- LOGIN + HEADER (LOGIN PAGE ONLY) ----------
# Check current status
authentication_status = st.session_state.get("authentication_status", None)

if not authentication_status:
    # Header first
    st.markdown(
        """
        <div class="login-hero" style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
            <h1 style="color:#ffffff;">✈️ Aircraft Engine RUL Prediction</h1>
            <h3 style="color:#bbbbbb;">AI-based Predictive Maintenance</h3>
            <p style="color:#888888; font-size: 0.9rem;">
                Secure access for engineers and administrators to monitor engine health, RUL, and maintenance logs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Centered login under header
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        authenticator.login(location="main", key="login")

    # Re-read status after user interaction
    authentication_status = st.session_state.get("authentication_status", None)

   # if still not authenticated, show error (wrong credentials) and stop
    if authentication_status is False:
        st.error("❌ Incorrect username or password. Please try again.")
        st.stop()
    elif authentication_status is None:
        # first load, no attempt yet
        st.stop()

# From here on, user is authenticated (engineer or admin)
name = st.session_state.get("name")
username = st.session_state.get("username")

# ========== DATABASE PATH ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')

# ========== DATABASE INIT & HELPERS ==========
def initialize_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL,
                engine_id TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT
            )
        ''')

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                username TEXT PRIMARY KEY,
                last_login TEXT,
                last_logout TEXT
            )
        """)

        cursor.execute('SELECT COUNT(*) FROM maintenance_log')
        if cursor.fetchone()[0] == 0:
            sample_data = [
                ("2025-12-01", "Engine-1", "Sensor Calibration", "✅ Completed", "All sensors recalibrated"),
                ("2025-11-28", "Engine-2", "Oil Change", "✅ Completed", "Engine 2000 hours maintained"),
                ("2025-11-25", "Engine-1", "Vibration Check", "✅ Completed", "No abnormalities detected"),
                ("2025-11-20", "Engine-3", "Filter Replacement", "✅ Completed", "Efficiency improved 3%"),
                ("2025-11-15", "Engine-2", "Temperature Sensor Cleaning", "✅ Completed", "Sensor accuracy verified"),
            ]
            cursor.executemany(
                'INSERT INTO maintenance_log (log_date, engine_id, action, status, notes) VALUES (?, ?, ?, ?, ?)',
                sample_data
            )

        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database Initialization Error: {e}")

initialize_database()

def load_maintenance_log():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT log_id AS _log_id, log_date AS Date, engine_id AS 'Engine ID', "
            "action AS Action, notes AS Notes, status AS Status "
            "FROM maintenance_log ORDER BY log_date DESC", conn
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading maintenance log: {e}")
        return pd.DataFrame(columns=["_log_id", "Date", "Engine ID", "Action", "Notes", "Status"])

def save_maintenance_entry(date_str, engine_id, action, status, notes):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO maintenance_log (log_date, engine_id, action, status, notes) VALUES (?, ?, ?, ?, ?)',
            (date_str, engine_id, action, status, notes)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving maintenance entry: {e}")
        return False

def update_maintenance_entry(log_id, date_str, engine_id, action, status, notes):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE maintenance_log 
            SET log_date = ?, engine_id = ?, action = ?, status = ?, notes = ?
            WHERE log_id = ?
        ''', (date_str, engine_id, action, status, notes, log_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating maintenance entry: {e}")
        return False

def update_login_time(username):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO user_activity (username, last_login, last_logout)
            VALUES (?, ?, COALESCE((SELECT last_logout FROM user_activity WHERE username=?), NULL))
            ON CONFLICT(username) DO UPDATE SET last_login=excluded.last_login
        """, (username, now_str, username))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error updating login time: {e}")

def update_logout_time(username):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO user_activity (username, last_login, last_logout)
            VALUES (?, NULL, ?)
            ON CONFLICT(username) DO UPDATE SET last_logout=excluded.last_logout
        """, (username, now_str))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error updating logout time: {e}")

def load_user_activity():
    activity = {}
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT username, last_login, last_logout FROM user_activity", conn)
        conn.close()
        for _, row in df.iterrows():
            activity[row["username"]] = {
                "last_login": row["last_login"],
                "last_logout": row["last_logout"],
            }
    except Exception:
        pass
    return activity

# ========== HANDLE AUTH STATUS AFTER LOGIN ==========
if authentication_status:
    user_info = config['credentials']['usernames'][username]
    roles = user_info.get('roles', [])
    is_admin = 'admin' in roles

    st.session_state.username = username
    st.session_state.email = user_info.get('email', '')
    st.session_state.role = ", ".join(roles)

    update_login_time(username)
else:
    # Should not happen because we handled not-authenticated above
    st.error("Invalid username or password")
    st.stop()

# ========== RUL LOGIC ==========
def predict_rul_dynamic(T2, T24, T30, T50, P2, P15, P30, Nf):
    temp_factor = (abs(T2) + abs(T24) + abs(T30) + abs(T50)) / 4
    temp_deg = temp_factor * 1.5

    pressure_factor = abs(P2 - 50) + abs(P15 - 55) + abs(P30 - 60)
    pressure_deg = (pressure_factor / 30) * 20

    speed_dev = abs(Nf - 5000) / 100
    speed_deg = speed_dev * 0.5

    base_rul = 120
    total_deg = temp_deg + pressure_deg + speed_deg
    rul = base_rul - total_deg
    rul = np.clip(rul, 5, 140)

    confidence = 85 - (temp_factor + pressure_factor + speed_dev) / 10
    confidence = np.clip(confidence, 60, 95)

    return rul, confidence

def get_health_status(rul):
    if rul <= 20:
        return "🔴 CRITICAL", "Immediate maintenance required"
    elif rul <= 40:
        return "🟠 WARNING", "Schedule maintenance within 1 week"
    elif rul <= 80:
        return "🟡 CAUTION", "Monitor closely"
    else:
        return "🟢 HEALTHY", "Operating normally"

# ========== SESSION STATE DEFAULTS ==========
if 'current_rul' not in st.session_state: 
    st.session_state.current_rul = 85
if 'selected_engine' not in st.session_state:
    st.session_state.selected_engine = "Engine-1"
if 'maintenance_log' not in st.session_state:
    st.session_state.maintenance_log = load_maintenance_log()
if 'engine_fleet' not in st.session_state:
    st.session_state.engine_fleet = {
        "Engine-1": {'T2': 20.0, 'T24': 25.0, 'T30': 30.0, 'T50': 35.0, 
                     'P2': 50.0, 'P15': 55.0, 'P30': 60.0, 'Nf': 5000.0},
        "Engine-2": {'T2': 40.0, 'T24': 50.0, 'T30': 60.0, 'T50': 70.0, 
                     'P2': 60.0, 'P15': 70.0, 'P30': 80.0, 'Nf': 5500.0},
        "Engine-3": {'T2': 15.0, 'T24': 20.0, 'T30': 25.0, 'T50': 30.0, 
                     'P2': 45.0, 'P15': 50.0, 'P30': 55.0, 'Nf': 4900.0}
    }

# ========== MAIN DASHBOARD ==========
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-profile-box">
            <p class="profile-title">👤 User Profile</p>
            <p class="profile-info"><strong>User:</strong> {st.session_state.username}</p>
            <p class="profile-info"><strong>Email:</strong> {st.session_state.email}</p>
            <p class="profile-info"><strong>Role:</strong> 🛠️ {st.session_state.role}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ Threshold Settings")
    st.markdown(
        "<div style='margin-bottom: 10px; color: #555;'>Set the minimum acceptable RUL (cycles):</div>",
        unsafe_allow_html=True,
    )
    threshold = st.slider("RUL Alert Threshold", 10, 100, 40, label_visibility="collapsed")
    st.markdown(f"**Current Threshold:** **{threshold}** cycles", unsafe_allow_html=True)

    authenticator.logout("🚪 LOGOUT", "sidebar")
    # After clicking logout, authentication_status will become False on next rerun
    if st.session_state.get("authentication_status") is False and "username" in st.session_state:
        update_logout_time(st.session_state["username"])

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; font-size: 0.75rem; color: #555;'>
            Aircraft Engine Monitoring System v1.0<br>
            Predictive Maintenance Dashboard
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("# ✈️ Aircraft Engine Health Monitoring")

# Tabs
if 'is_admin' not in locals():
    is_admin = False
if is_admin:
    tab_labels = ["🛡️ Admin", "🔍 Single Engine", "📊 Comparison",
                  "📈 Predictive", "🔧 Components", "📋 Maintenance"]
else:
    tab_labels = ["🔍 Single Engine", "📊 Comparison",
                  "📈 Predictive", "🔧 Components", "📋 Maintenance"]

tabs = st.tabs(tab_labels)

if is_admin:
    tab_admin = tabs[0]
    tab1, tab2, tab3, tab4, tab5 = tabs[1], tabs[2], tabs[3], tabs[4], tabs[5]
else:
    tab1, tab2, tab3, tab4, tab5 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]
    tab_admin = None

# ====== TAB 1: SINGLE ENGINE ======
with tab1:
    st.markdown("## Real-Time RUL Prediction")
    st.markdown("### Select Engine to View & Update Data")

    selected_engine = st.selectbox(
        "Engine ID:",
        list(st.session_state.engine_fleet.keys()),
        key='current_engine_select',
    )
    st.session_state.selected_engine = selected_engine
    current_data = st.session_state.engine_fleet[selected_engine]

    st.markdown("### Sensor Input Readings")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        T2 = st.slider("T2 (°C)", -50.0, 100.0, current_data['T2'], step=1.0, key="T2")
    with c2:
        T24 = st.slider("T24 (°C)", -50.0, 100.0, current_data['T24'], step=1.0, key="T24")
    with c3:
        T30 = st.slider("T30 (°C)", -50.0, 100.0, current_data['T30'], step=1.0, key="T30")
    with c4:
        T50 = st.slider("T50 (°C)", -50.0, 100.0, current_data['T50'], step=1.0, key="T50")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        P2 = st.slider("P2 (psi)", 20.0, 80.0, current_data['P2'], step=1.0, key="P2")
    with c6:
        P15 = st.slider("P15 (psi)", 30.0, 90.0, current_data['P15'], step=1.0, key="P15")
    with c7:
        P30 = st.slider("P30 (psi)", 40.0, 100.0, current_data['P30'], step=1.0, key="P30")
    with c8:
        Nf = st.slider("Nf (rpm)", 2000.0, 8000.0, current_data['Nf'], step=100.0, key="Nf")

    st.divider()
    cb1, cb2, _ = st.columns([1, 1, 3])

    with cb1:
        if st.button("💾 Save Engine Data", use_container_width=True, type="secondary"):
            st.session_state.engine_fleet[selected_engine] = {
                'T2': T2, 'T24': T24, 'T30': T30, 'T50': T50,
                'P2': P2, 'P15': P15, 'P30': P30, 'Nf': Nf
            }
            rul_saved, _ = predict_rul_dynamic(T2, T24, T30, T50, P2, P15, P30, Nf)
            st.session_state.current_rul = rul_saved
            st.toast(f"✅ Data for {selected_engine} saved to fleet!", icon="💾")
            st.success(f"✅ Data for **{selected_engine}** saved! Comparison and Predictive tabs will now reflect this data.")
            st.rerun()

    with cb2:
        if st.button("🔮 Predict RUL", use_container_width=True, type="primary"):
            rul, conf = predict_rul_dynamic(T2, T24, T30, T50, P2, P15, P30, Nf)
            status, action = get_health_status(rul)
            days = max(0.1, rul / 30)

            st.session_state.rul = rul
            st.session_state.conf = conf
            st.session_state.status = status
            st.session_state.action = action
            st.session_state.days = days
            st.session_state.current_rul = rul
            st.session_state.current_engine_name = selected_engine

            icon_map = {"🔴": "🚨", "🟠": "⚠️", "🟡": "🔔", "🟢": "✅"}
            icon = icon_map.get(status.split()[0], "💡")
            toast_message = f"{status}: RUL is **{rul:.0f} cycles**. {action.split(':')[0]}."
            st.toast(toast_message, icon=icon)

    st.divider()
    if 'rul' in st.session_state:
        st.markdown(f"### RUL Prediction for {st.session_state.current_engine_name}")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("RUL (cycles)", f"{st.session_state.rul:.0f}")
        with m2:
            st.metric("Confidence", f"{st.session_state.conf:.1f}%")
        with m3:
            st.metric("Status", st.session_state.status)
        with m4:
            st.metric("Days Left", f"{st.session_state.days:.1f}")
        st.info(f"📌 {st.session_state.action}")

# ====== TAB 2: COMPARISON ======
with tab2:
    st.subheader("🔄 Multi-Engine Comparison (Dynamic Fleet Status)")
    comparison_data = []
    for engine_id, sensors in st.session_state.engine_fleet.items():
        rul, confidence = predict_rul_dynamic(
            sensors['T2'], sensors['T24'], sensors['T30'], sensors['T50'],
            sensors['P2'], sensors['P15'], sensors['P30'], sensors['Nf']
        )
        status, _ = get_health_status(rul)
        comparison_data.append({
            "Engine ID": engine_id,
            "RUL (cycles)": int(rul),
            "Confidence %": f"{confidence:.1f}%",
            "Status": status
        })
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)
    st.info("💡 **Dynamic Comparison:** Table reflects last saved sensor data for each engine.")

# ====== TAB 3: PREDICTIVE ======
with tab3:
    st.subheader("📈 RUL Degradation Forecast (Next 50 Cycles)")
    selected_engine_for_plot = st.session_state.get("selected_engine", "Engine-1")
    saved_data = st.session_state.engine_fleet.get(
        selected_engine_for_plot, st.session_state.engine_fleet.get("Engine-1", {})
    )
    if saved_data:
        current_rul_from_saved, _ = predict_rul_dynamic(
            saved_data['T2'], saved_data['T24'], saved_data['T30'], saved_data['T50'],
            saved_data['P2'], saved_data['P15'], saved_data['P30'], saved_data['Nf']
        )
        current_rul = int(current_rul_from_saved)
    else:
        current_rul = 85

    st.markdown(f"**Forecast for:** **{selected_engine_for_plot}** (Current RUL: **{current_rul}** cycles)")
    cycles = np.arange(0, 51)
    degradation_rate = 1.2
    forecast_rul = np.clip(current_rul - (cycles * degradation_rate), 5, 140)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(cycles, forecast_rul, linewidth=2.5, color="#2E86AB", label="Predicted RUL")
    ax.axhline(y=20, color="red", linestyle="--", linewidth=2, label="Critical (≤20)")
    ax.axhline(y=40, color="orange", linestyle="--", linewidth=2, label="Warning (20-40)")
    ax.fill_between(cycles, 0, 20, alpha=0.2, color="red")
    ax.fill_between(cycles, 20, 40, alpha=0.2, color="orange")
    ax.set_xlabel("Cycles", fontsize=12)
    ax.set_ylabel("RUL (cycles)", fontsize=12)
    ax.set_title("Engine RUL Degradation Forecast", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    if np.any(forecast_rul <= threshold):
        first_cycle = np.where(forecast_rul <= threshold)[0][0]
        st.warning(f"⚠️ **Alert:** RUL forecasted to drop below **{threshold} cycles** within **{first_cycle} cycles**.")
    else:
        st.info(f"✅ **Forecast:** RUL predicted to stay above **{threshold} cycles** for next 50 cycles.")

# ====== TAB 4: COMPONENT HEALTH ======
with tab4:
    st.subheader("🔧 Component Health Status")
    current_data = st.session_state.engine_fleet[st.session_state.selected_engine]
    components = {
        "T2 (Total Temp)": current_data['T2'], "T24 (Fan Inlet)": current_data['T24'],
        "T30 (Mid Compress)": current_data['T30'], "T50 (Compressor)": current_data['T50'],
        "P2 (Fan Press)": current_data['P2'], "P15 (Mid Press)": current_data['P15'],
        "P30 (High Press)": current_data['P30'], "Nf (Speed)": current_data['Nf']
    }
    st.markdown(f"### Health Metrics for {st.session_state.selected_engine}")
    c1h, c2h = st.columns(2)
    for idx, (name_c, val) in enumerate(components.items()):
        if "T" in name_c:
            health = min(100, max(0, 100 - abs(val - 85) * 0.8))
        elif "P" in name_c:
            health = min(100, max(0, 100 - abs(val - 50) * 1.5))
        else:
            health = min(100, max(0, 100 - abs(val - 5000) / 100))

        if health >= 80:
            color = "🟢"; h_status = "Excellent"
        elif health >= 60:
            color = "🟡"; h_status = "Good"
        else:
            color = "🟠"; h_status = "Fair/Poor"

        target_col = c1h if idx < 4 else c2h
        with target_col:
            st.metric(f"{color} {name_c}", f"{health:.1f}%", delta=h_status)

    st.divider()
    st.info(f"🔍 **Component Analysis:** Individual component health for **{st.session_state.selected_engine}** is derived from its current sensor readings.")

# ====== TAB 5: MAINTENANCE LOG ======
with tab5:
    st.subheader("📋 Maintenance History & Logs (Click cells to edit)")
    edited_df = st.data_editor(
        st.session_state.maintenance_log,
        key="maintenance_editor",
        column_config={
            "Date": st.column_config.DateColumn("Date", disabled=True),
            "Engine ID": st.column_config.Column("Engine ID", disabled=True),
            "Action": st.column_config.Column("Action", disabled=True),
            "Notes": st.column_config.TextColumn("Notes"),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["✅ Completed", "⚙️ In Progress", "🚫 Deferred", "❌ Failed"],
                required=True
            ),
        },
        hide_index=True,
        use_container_width=True
    )

    if not edited_df.equals(st.session_state.maintenance_log):
        st.info("Changes detected. Saving to database...")
        for index, row in edited_df.iterrows():
            original_row = st.session_state.maintenance_log.iloc[index]
            if row['Status'] != original_row['Status'] or row['Notes'] != original_row['Notes']:
                update_maintenance_entry(
                    log_id=row['_log_id'],
                    date_str=row['Date'],
                    engine_id=row['Engine ID'],
                    action=row['Action'],
                    status=row['Status'],
                    notes=row['Notes']
                )
        st.session_state.maintenance_log = load_maintenance_log()
        st.toast("Database updated successfully!", icon="📝")
        st.rerun()

    st.divider()
    st.subheader("➕ Log New Maintenance")
    c1m, c2m = st.columns(2)
    with c1m:
        new_engine = st.selectbox("Select Engine:", list(st.session_state.engine_fleet.keys()), key="new_engine_select")
        new_action = st.text_input("Maintenance Action:", placeholder="e.g., Oil Change", key="new_action_input")
        new_notes = st.text_input("Notes:", placeholder="Enter additional notes", key="new_notes_input")
    with c2m:
        new_date = st.date_input("Date:", value=date.today(), key="new_date_input")
        new_status = st.selectbox("Initial Status:", ["✅ Completed", "⚙️ In Progress", "🚫 Deferred", "❌ Failed"], key="new_status_select")

    if st.button("💾 Save New Maintenance Log", key="save_maintenance_btn"):
        if new_action:
            date_str = new_date.strftime("%Y-%m-%d")
            success = save_maintenance_entry(date_str, new_engine, new_action, new_status, new_notes)
            if success:
                st.session_state.maintenance_log = load_maintenance_log()
                st.success(f"✅ Maintenance for {new_engine} logged successfully and saved persistently!")
                st.toast("New maintenance record saved!", icon="📝")
                st.rerun()
        else:
            st.warning("Please enter a maintenance action.")

# ====== ADMIN TAB ======
if is_admin and tab_admin is not None:
    with tab_admin:
        st.subheader("🛡️ Admin Dashboard")

        st.markdown("#### Registered Users")
        users = config["credentials"]["usernames"]
        activity = load_user_activity()

        rows = []
        for uname, info in users.items():
            act = activity.get(uname, {})
            rows.append({
                "Username": uname,
                "Name": info.get("name", ""),
                "Email": info.get("email", ""),
                "Roles": ", ".join(info.get("roles", [])),
                "Last Login": act.get("last_login", "—"),
                "Last Logout": act.get("last_logout", "—"),
            })
        users_df = pd.DataFrame(rows)
        st.dataframe(users_df, use_container_width=True, height=260)

        st.markdown("---")
        st.markdown(
            "This panel summarizes who can access the predictive maintenance dashboard, their roles, and recent login activity."
        )
