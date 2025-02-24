import streamlit as st
import os

# st.set_page_config(
#     page_title="Necromunda Campaign Manager",
#     page_icon="🎮",
#     layout="wide"
# )

st.title("🎮 Necromunda Campaign Manager")
st.markdown(
    """
    Welcome to the **Necromunda Campaign Manager**!  
    This tool helps you track your campaign, manage gangs, territories, battles, and equipment.
    """
)

st.markdown("---")

# **Campaign Overview - Quick Stats**
col1, col2, col3, col4 = st.columns(4)

total_gangs = len(st.session_state.get("gangs", []))
total_territories = len(st.session_state.get("territories", []))
total_battles = len(st.session_state.get("battles", []))
total_equipment = len(st.session_state.get("equipment_list", []))

with col1:
    st.metric("🛡️ Total Gangs", total_gangs)
with col2:
    st.metric("🌍 Total Territories", total_territories)
with col3:
    st.metric("⚔️ Battles Fought", total_battles)
with col4:
    st.metric("🔧 Equipment Items", total_equipment)

st.markdown("---")

# **Navigation Shortcuts**
st.markdown("### 🔗 Quick Navigation")

col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)

with col_nav1:
    if st.button("📊 Dashboard"):
        st.switch_page("views/1_Dashboard.py")

with col_nav2:
    if st.button("👥 Manage Gangs"):
        st.switch_page("views/2_Gangs.py")

with col_nav3:
    if st.button("🌍 Territories"):
        st.switch_page("views/3_Territories.py")

with col_nav4:
    if st.button("⚔️ Battles"):
        st.switch_page("views/4_Battles.py")

st.markdown("#### 🔄 Campaign Management")
col_mgmt1, col_mgmt2 = st.columns(2)

with col_mgmt1:
    if st.button("🛠️ Rebuild Campaign Data"):
        st.switch_page("pages/Rebuild_Campaign.py")

with col_mgmt2:
    if st.button("☁️ Import Yaktribe Data"):
        st.switch_page("pages/8_ImportYaktribe.py")

st.markdown("---")

# **Instructions and Information**
st.markdown("### 📖 How to Use This Tool")
st.write(
    """
    - **📊 Dashboard**: View an overview of your campaign statistics.
    - **👥 Manage Gangs**: Create, edit, and manage gangs and their fighters.
    - **🌍 Territories**: Assign and manage territories owned by gangs.
    - **⚔️ Battles**: Record battle results and outcomes.
    - **🔧 Equipment**: Manage weapons and gear used by fighters.
    - **☁️ Import Yaktribe Data**: Import existing gangs from Yaktribe.
    - **🛠️ Rebuild Campaign Data**: Reload campaign data from JSON files if needed.

    This tool is designed to streamline your **Necromunda** campaign, making it easy to track progress and manage game data.
    """
)

st.info("💡 Tip: Use the sidebar to quickly access different sections of the app.")
