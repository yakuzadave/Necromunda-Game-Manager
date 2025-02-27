"""
Helper functions for territory operations in Necromunda Campaign Manager.
"""
import random
from typing import List, Dict, Any, Optional, Tuple

import streamlit as st

from common import Territory, save_data
from utils.map_utils import (
    get_random_coordinates,
    calculate_distance
)
from utils.logger import log_info, log_error

def find_territory_by_name(territories: List[Territory], name: str) -> Optional[Territory]:
    """Find a territory by name in the territory list"""
    return next((t for t in territories if t.name == name), None)

def find_nearest_territory(
    territories: List[Territory], 
    x: float, 
    y: float, 
    max_distance: float = float('inf')
) -> Tuple[Optional[Territory], float]:
    """
    Find the territory nearest to the given coordinates.
    
    Args:
        territories: List of territories to search
        x: X coordinate to compare against
        y: Y coordinate to compare against
        max_distance: Maximum distance to consider (default: infinite)
        
    Returns:
        Tuple of (nearest_territory, distance) or (None, float('inf')) if none found
    """
    nearest_territory = None
    min_distance = float('inf')
    
    for territory in territories:
        if territory.x is not None and territory.y is not None:
            distance = calculate_distance(x, y, territory.x, territory.y)
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest_territory = territory
                
    return nearest_territory, min_distance

def create_territory(
    name: str,
    territory_type: str,
    controller: Optional[str] = None,
    x: Optional[float] = None,
    y: Optional[float] = None
) -> Territory:
    """
    Create a new territory with the given properties.
    If coordinates are not provided, random ones will be generated.
    
    Args:
        name: Territory name
        territory_type: Type of territory
        controller: Controlling faction or None
        x: X coordinate or None for random
        y: Y coordinate or None for random
        
    Returns:
        A new Territory instance
    """
    # Generate random coordinates if needed
    if x is None or y is None:
        random_x, random_y = get_random_coordinates(seed=f"{name}_{territory_type}")
        x = x or random_x
        y = y or random_y
    
    return Territory(
        name=name,
        type=territory_type,
        controlled_by=controller,
        x=x,
        y=y
    )

def assign_territory(
    territory_name: str,
    gang_name: str,
    territories: List[Territory],
    gangs: List[Any]
) -> bool:
    """
    Assign a territory to a gang.
    
    Args:
        territory_name: Name of territory to assign
        gang_name: Name of gang to assign to
        territories: List of territories
        gangs: List of gangs
        
    Returns:
        True if assignment was successful, False otherwise
    """
    try:
        # Find territory and update controller
        territory_updated = False
        for territory in territories:
            if territory.name == territory_name:
                territory.controlled_by = gang_name
                territory_updated = True
                break
        
        if not territory_updated:
            return False
                
        # Update gang's territory list
        gang_updated = False
        for gang in gangs:
            if gang.gang_name == gang_name and territory_name not in gang.territories:
                gang.territories.append(territory_name)
                gang_updated = True
                break
                
        return territory_updated and gang_updated
    except Exception as e:
        log_error(f"Error assigning territory: {e}", exc_info=True)
        return False

def ensure_valid_coordinates(territories: List[Territory]) -> None:
    """
    Ensure all territories have valid coordinates, generating them if needed.
    This modifies the territories in-place.
    
    Args:
        territories: List of territories to process
    """
    for i, territory in enumerate(territories):
        if territory.x is None or territory.y is None:
            # Generate coordinates with territory name as seed for consistency
            x, y = get_random_coordinates(seed=f"{territory.name}_{i}")
            
            # Update territory with new coordinates
            territory_dict = {
                "name": territory.name,
                "type": territory.type,
                "controlled_by": territory.controlled_by,
                "x": territory.x if territory.x is not None else x,
                "y": territory.y if territory.y is not None else y,
                "lat": territory.lat,
                "lng": territory.lng,
                "elevation": territory.elevation
            }
            
            # Replace the territory in the list with updated version
            territories[i] = Territory(**territory_dict)
