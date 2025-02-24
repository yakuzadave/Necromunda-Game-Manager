
import streamlit as st

def show_home():
    st.title("Welcome to Necromunda Campaign Manager")
    
    # Introduction section
    st.markdown("""
    ### About the App
    Necromunda Campaign Manager is a comprehensive tool designed to help you manage your 
    Necromunda tabletop gaming campaigns with ease. Track gangs, territories, battles, 
    and equipment all in one place.
    
    ### Key Features
    - **Gang Management**: Create and manage your gangs and fighters
    - **Territory Control**: Track territory ownership and effects
    - **Battle Tracking**: Record battle outcomes and campaign progression
    - **Equipment Library**: Manage weapons and equipment
    - **Campaign Analytics**: View detailed statistics and reports
    
    ### Getting Started
    1. Create your first gang in the **Gangs** section
    2. Set up territories in the **Territories** section
    3. Record battles in the **Battles** section
    4. Track your campaign progress in the **Dashboard**
    
    Use the navigation menu on the left to explore different sections of the app.
    """)

    # Display some key metrics if data exists
    if st.session_state.gangs or st.session_state.territories or st.session_state.battles:
        st.subheader("Current Campaign Status")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Gangs", len(st.session_state.gangs))
        with col2:
            st.metric("Total Territories", len(st.session_state.territories))
        with col3:
            st.metric("Battles Fought", len(st.session_state.battles))
    else:
        st.info("Start by adding your first gang in the Gangs section!")

show_home()
