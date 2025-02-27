import base64
import random
from io import BytesIO
import math
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw
import streamlit as st

from common import Territory
from utils.logger import log_debug, log_error, log_info, log_warning

def assign_coordinates_if_missing(
    territory, 
    default_x_range=(0, 4096), 
    default_y_range=(0, 4096)
):
    """
    If the territory lacks x/y coordinates, create a new Territory with random coordinates.
    Returns a new Territory object to avoid mutating the original.
    """
    try:
        # Create a dictionary from the territory for creating a new instance
        territory_dict = {
            "name": territory.name,
            "type": territory.type,
            "controlled_by": territory.controlled_by,
            "x": territory.x,
            "y": territory.y,
            "lat": territory.lat,
            "lng": territory.lng,
            "elevation": territory.elevation
        }
        
        # Assign random coordinates if needed
        if territory_dict["x"] is None:
            territory_dict["x"] = random.uniform(*default_x_range)
        if territory_dict["y"] is None:
            territory_dict["y"] = random.uniform(*default_y_range)
            
        # Create and return a new Territory object
        return Territory(**territory_dict)
    except Exception as e:
        log_error(f"Error assigning coordinates to territory {territory.name}: {e}", exc_info=True)
        # If something goes wrong, return the original territory to avoid crashing
        return territory

@st.cache_data
def get_random_coordinates(seed=None, default_x_range=(0, 4096), default_y_range=(0, 4096)):
    """
    Generate random coordinates that can be cached based on seed.
    This function returns simple values that are serializable.
    """
    if seed is not None:
        random.seed(seed)
    x = random.uniform(*default_x_range)
    y = random.uniform(*default_y_range)
    return x, y

@st.cache_data
def generate_placeholder_map(width=4096, height=4096):
    """
    Generate a placeholder grid map when no base map is available.
    This is cached to avoid regenerating the image on every rerun.
    """
    try:
        # Create a blank white image
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw a grid
        grid_spacing = 512
        
        # Draw vertical lines
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=(200, 200, 200), width=2)
        
        # Draw horizontal lines
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=(200, 200, 200), width=2)
        
        # Draw a border
        draw.rectangle([0, 0, width-1, height-1], outline=(0, 0, 0), width=5)
        
        # Add title text
        draw.text((width//2-150, height//2), "Necromunda Territory Map", fill=(0, 0, 0))
        draw.text((width//2-130, height//2+30), "Generated Grid", fill=(0, 0, 0))
        
        # Convert to bytes for folium
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        log_error(f"Error generating placeholder map: {e}", exc_info=True)
        # Return a fallback minimal image if there's an error
        return (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8"
            "AAAAASUVORK5CYII="
        )

@st.cache_data
def generate_distinct_colors(n):
    """Generate visually distinct colors for territories"""
    color_list = [
        "#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", 
        "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990", "#dcbeff",
        "#9A6324", "#800000", "#aaffc3", "#808000", "#000075", "#a9a9a9",
        "#FF00FF", "#2F4F4F", "#FF8C00", "#00CED1", "#8A2BE2", "#00FF7F"
    ]
    # If we need more colors than in our predefined list, generate them
    if n > len(color_list):
        import colorsys
        for i in range(n - len(color_list)):
            # Generate HSV colors with good separation
            h = i / n
            s = 0.7 + (i % 3) * 0.1  # Vary saturation slightly
            v = 0.8 + (i % 2) * 0.1  # Vary brightness slightly
            # Convert to RGB and then to hex
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color_list.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
    return color_list[:n]

@st.cache_data
def calculate_territory_stats(_territories):
    """Calculate statistics about territory control and distribution"""
    stats = {
        "total": len(_territories),
        "claimed": 0,
        "unclaimed": 0,
        "faction_counts": {},
        "type_counts": {}
    }
    
    for t in _territories:
        # Count by control status
        if t.controlled_by:
            stats["claimed"] += 1
            # Count by faction
            if t.controlled_by not in stats["faction_counts"]:
                stats["faction_counts"][t.controlled_by] = 0
            stats["faction_counts"][t.controlled_by] += 1
        else:
            stats["unclaimed"] += 1
        
        # Count by territory type
        if t.type not in stats["type_counts"]:
            stats["type_counts"][t.type] = 0
        stats["type_counts"][t.type] += 1
    
    return stats

def calculate_distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points"""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

@st.cache_data
def cluster_territories(_territories, max_distance=200):
    """
    Group territories that are close to each other into clusters
    for better visualization when many territories exist.
    """
    clusters = []
    processed = set()
    
    for i, t1 in enumerate(_territories):
        if i in processed:
            continue
            
        # Start a new cluster with this territory
        cluster = [t1]
        processed.add(i)
        
        # Find all territories within max_distance
        for j, t2 in enumerate(_territories):
            if j in processed or j == i:
                continue
                
            if (t1.x and t1.y and t2.x and t2.y and 
                calculate_distance(t1.x, t1.y, t2.x, t2.y) <= max_distance):
                cluster.append(t2)
                processed.add(j)
                
        clusters.append(cluster)
        
    return clusters

def calculate_territory_adjacency(_territories, adjacency_threshold=400):
    """Calculate which territories are adjacent to each other"""
    adjacency = defaultdict(list)
    
    for i, t1 in enumerate(_territories):
        if not t1.x or not t1.y:
            continue
            
        for j, t2 in enumerate(_territories):
            if i == j or not t2.x or not t2.y:
                continue
                
            distance = calculate_distance(t1.x, t1.y, t2.x, t2.y)
            if distance <= adjacency_threshold:
                adjacency[t1.name].append({
                    "name": t2.name,
                    "distance": distance,
                    "controlled_by": t2.controlled_by
                })
    
    return adjacency

def calculate_faction_dominance(_territories):
    """Calculate which factions control strategic territory clusters"""
    # Territory cluster analysis
    clusters = cluster_territories(_territories)
    
    # Analyze faction control in each cluster
    faction_dominance = defaultdict(int)
    
    for cluster in clusters:
        if not cluster:
            continue
            
        # Count factions in this cluster
        faction_count = defaultdict(int)
        for territory in cluster:
            if territory.controlled_by:
                faction_count[territory.controlled_by] += 1
        
        # Determine dominant faction in cluster
        if faction_count:
            dominant_faction = max(faction_count.items(), key=lambda x: x[1])[0]
            faction_dominance[dominant_faction] += len(cluster)
    
    return faction_dominance
