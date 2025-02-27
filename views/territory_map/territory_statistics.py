import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.logger import log_error
from utils.map_utils import calculate_territory_stats, calculate_faction_dominance, calculate_territory_adjacency

def render_territory_statistics():
    """Render the territory statistics tab content"""
    st.header("Territory Statistics")
    
    # Calculate and display statistics
    try:
        territory_stats = calculate_territory_stats(st.session_state.territories)
        
        # Display overall counts
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Territories", territory_stats["total"])
        with col2:
            st.metric("Claimed Territories", territory_stats["claimed"])
        with col3:
            st.metric("Unclaimed Territories", territory_stats["unclaimed"])
        
        # Calculate territory value by faction
        faction_dominance = calculate_faction_dominance(st.session_state.territories)
        
        # Create tabs for different statistics views
        stat_tab1, stat_tab2, stat_tab3 = st.tabs([
            "Faction Control", "Territory Types", "Strategic Analysis"
        ])
        
        with stat_tab1:
            if territory_stats["faction_counts"]:
                st.subheader("Territory Control by Faction")
                
                # Add faction control visualization options
                viz_type = st.radio(
                    "Visualization Type",
                    options=["Bar Chart", "Pie Chart"],
                    horizontal=True
                )
                
                faction_df = pd.DataFrame({
                    "Faction": list(territory_stats["faction_counts"].keys()),
                    "Territories": list(territory_stats["faction_counts"].values())
                })
                
                if viz_type == "Bar Chart":
                    st.bar_chart(faction_df.set_index("Faction"))
                else:
                    try:
                        fig, ax = plt.subplots()
                        ax.pie(
                            faction_df["Territories"],
                            labels=faction_df["Faction"].tolist(),
                            autopct='%1.1f%%',
                            startangle=90
                        )
                        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                        st.pyplot(fig)
                    except Exception:
                        st.bar_chart(faction_df.set_index("Faction"))
                        st.warning("Could not generate pie chart - matplotlib may not be installed")
            else:
                st.info("No faction control data available yet.")
                
        with stat_tab2:
            if territory_stats["type_counts"]:
                st.subheader("Territory Types Distribution")
                
                type_df = pd.DataFrame({
                    "Type": list(territory_stats["type_counts"].keys()),
                    "Count": list(territory_stats["type_counts"].values())
                })
                
                # Add a visualization selector
                viz_type = st.radio(
                    "Visualization Type",
                    options=["Bar Chart", "Pie Chart"],
                    horizontal=True,
                    key="type_viz"
                )
                
                if viz_type == "Bar Chart":
                    st.bar_chart(type_df.set_index("Type"))
                else:
                    try:
                        fig, ax = plt.subplots()
                        ax.pie(
                            type_df["Count"],
                            labels=type_df["Type"].tolist(),
                            autopct='%1.1f%%',
                            startangle=90
                        )
                        ax.axis('equal')
                        st.pyplot(fig)
                    except Exception:
                        st.bar_chart(type_df.set_index("Type"))
                        st.warning("Could not generate pie chart - matplotlib may not be installed")
            else:
                st.info("No territory type data available yet.")
        
        with stat_tab3:
            st.subheader("Strategic Territory Analysis")
            
            if faction_dominance:
                st.write("Faction Strategic Control (based on territory clusters):")
                
                faction_dom_df = pd.DataFrame({
                    "Faction": list(faction_dominance.keys()),
                    "Strategic Value": list(faction_dominance.values())
                })
                
                st.bar_chart(faction_dom_df.set_index("Faction"))
                
                # Find the strategically dominant faction
                dominant_faction = max(faction_dominance.items(), key=lambda x: x[1])[0]
                dom_value = faction_dominance[dominant_faction]
                
                st.info(f"**{dominant_faction}** has the strongest strategic position with control of {dom_value} clustered territories.")
            
            # Calculate territory isolation/connectivity
            if len(st.session_state.territories) > 1:
                adjacency = calculate_territory_adjacency(st.session_state.territories)
                
                # Identify isolated territories
                isolated = [t.name for t in st.session_state.territories 
                           if t.name not in adjacency or not adjacency[t.name]]
                
                if isolated:
                    st.warning(f"Found {len(isolated)} isolated territories with no connections to other territories.")
                    st.write(", ".join(isolated))
                else:
                    st.success("All territories are connected to at least one other territory.")
                
                # Territory with most connections
                if adjacency:
                    most_connected = max(adjacency.items(), key=lambda x: len(x[1]))
                    st.write(f"**{most_connected[0]}** is the most connected territory with {len(most_connected[1])} connections.")
        
        # Create a 2D histogram for territory locations
        st.subheader("Territory Density Map")
        
        # Create a 2D histogram for territory locations
        if len(st.session_state.territories) > 1:
            x_coords = [t.x for t in st.session_state.territories if t.x is not None]
            y_coords = [t.y for t in st.session_state.territories if t.y is not None]
            
            if x_coords and y_coords:
                try:
                    # Create grid for heatmap
                    x_bins = np.linspace(0, 4096, 20)
                    y_bins = np.linspace(0, 4096, 20)
                    heatmap_data, _, _ = np.histogram2d(x_coords, y_coords, bins=[x_bins, y_bins])
                    
                    # Display the heatmap
                    st.write("Areas with more territories appear darker:")
                    fig, ax = plt.subplots(figsize=(10, 8))
                    ax.imshow(heatmap_data.T, origin='lower', extent=(0, 4096, 0, 4096), 
                              cmap='viridis', interpolation='gaussian')
                    ax.set_xlabel("X Coordinate")
                    ax.set_ylabel("Y Coordinate")
                    ax.set_title("Territory Density Heatmap")
                    st.pyplot(fig)
                except ImportError:
                    st.warning("Matplotlib is required for the density heatmap. Install with 'pip install matplotlib'")
                    st.info("Alternatively, you can view territory distribution in the tables above")
                except Exception as e:
                    st.warning(f"Could not generate density map: {str(e)}")
            else:
                st.info("Need territories with valid coordinates to generate a density map.")
        else:
            st.info("Need at least 2 territories with coordinates to generate a density map.")
                
    except Exception as e:
        log_error(f"Error generating statistics: {e}", exc_info=True)
        st.error(f"Error generating statistics: {str(e)}")
