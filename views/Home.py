import streamlit as st
import os
from datetime import datetime
import pandas as pd

from common import Gang, load_data, Territory, LocalBattle

def show_home():
    st.title("🎮 Necromunda Campaign Manager")
    st.markdown(
        """
        Welcome to the **Necromunda Campaign Manager**!  
        This tool helps you track your campaign, manage gangs, territories, battles, and equipment.
        """
    )

    st.markdown("---")

    # Load data
    try:
        gangs, territories, battles = load_data()
        
        # **Campaign Overview - Quick Stats**
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🛡️ Total Gangs", len(gangs))
        with col2:
            st.metric("🌍 Total Territories", len(territories))
        with col3:
            st.metric("⚔️ Battles Fought", len(battles))
        with col4:
            total_equipment = 0
            for gang in gangs:
                if hasattr(gang, 'stash'):
                    total_equipment += len(gang.stash)
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
                st.switch_page("views/0_Rebuild_Campaign.py")

        with col_mgmt2:
            if st.button("☁️ Import Yaktribe Data"):
                st.switch_page("views/8_ImportYaktribe.py")
        
        # Recent activity
        st.markdown("---")
        st.subheader("Recent Activity")
        
        # Recent battles
        if battles:
            st.markdown("### Recent Battles")
            recent_battles = sorted(
                battles, 
                key=lambda b: datetime.fromisoformat(b.battle_created_datetime),
                reverse=True
            )[:3]
            
            for battle in recent_battles:
                with st.container():
                    st.markdown(f"**{battle.battle_scenario}** on {battle.battle_created_datetime}")
                    st.markdown(f"Winner: **{battle.winner_gang}**")
                    st.markdown(f"Participants: {', '.join(battle.participating_gangs)}")
                    st.markdown("---")

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
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("You may need to create your first gang or rebuild campaign data.")

# Call the show_home function to display the page content
show_home()
