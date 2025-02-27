"""
Smart label placement utilities for the Necromunda Territory Map.
Helps avoid label overlaps and improves map readability.
"""
from typing import List, Dict, Tuple, Any
import math
import random

def calculate_label_position(
    x: float, 
    y: float, 
    territory_name: str, 
    strategy: str = "offset",
    offset: int = 50,
    all_positions: List[Tuple[float, float, str]] = None
) -> Tuple[float, float]:
    """
    Calculate the optimal position for a territory label.
    
    Args:
        x: X coordinate of the territory
        y: Y coordinate of the territory
        territory_name: Name of the territory (used for length calculations)
        strategy: Label placement strategy ('offset', 'radial', 'smart')
        offset: Basic offset for simple positioning
        all_positions: List of other territory positions for collision detection
        
    Returns:
        Tuple of (y_position, x_position) for the label
    """
    if strategy == "offset":
        # Simple offset above the territory point
        return (y + offset, x)
    
    elif strategy == "radial":
        # Place labels in a circular pattern around dense areas
        if all_positions:
            # Count territories in vicinity
            nearby_count = 0
            for pos_y, pos_x, _ in all_positions:
                if abs(pos_x - x) < 200 and abs(pos_y - y) < 200:
                    nearby_count += 1
            
            # Adjust angle based on position to avoid overlaps
            angle_step = 360 / max(8, nearby_count)
            angle = (hash(territory_name) % 8) * angle_step
            
            # Convert angle to radians and calculate position
            radians = math.radians(angle)
            radius = offset * 1.2  # Slightly larger radius for radial layout
            
            return (
                y + radius * math.sin(radians),
                x + radius * math.cos(radians)
            )
    
    elif strategy == "smart":
        # Advanced positioning to minimize overlaps
        # This is a simplified version - a full implementation would be more complex
        if not all_positions:
            return (y + offset, x)
        
        # Try different positions and score them based on overlaps
        possible_positions = [
            (y + offset, x),           # Top
            (y - offset, x),           # Bottom
            (y, x + offset),           # Right
            (y, x - offset),           # Left
            (y + offset, x + offset),  # Top-right
            (y + offset, x - offset),  # Top-left
            (y - offset, x + offset),  # Bottom-right
            (y - offset, x - offset)   # Bottom-left
        ]
        
        best_position = possible_positions[0]
        best_score = float('inf')
        
        for pos_y, pos_x in possible_positions:
            score = 0
            for other_y, other_x, other_name in all_positions:
                # Skip self
                if abs(other_x - x) < 5 and abs(other_y - y) < 5:
                    continue
                
                # Calculate distance from this position to other territory's position
                distance = ((pos_x - other_x) ** 2 + (pos_y - other_y) ** 2) ** 0.5
                score += 1000 / (distance + 1)  # Inverse distance scoring
            
            if score < best_score:
                best_score = score
                best_position = (pos_y, pos_x)
                
        return best_position
            
    # Default to simple offset if no strategy matches
    return (y + offset, x)

def optimize_label_placement(territories: List[Dict[str, Any]], strategy: str = "offset") -> List[Dict[str, Any]]:
    """
    Optimize label positions for a list of territories to minimize overlaps.
    
    Args:
        territories: List of territory dictionaries with 'x', 'y', 'name' keys
        strategy: Label placement strategy
        
    Returns:
        List of territory dictionaries with 'label_x' and 'label_y' added
    """
    # Extract positions for collision detection
    all_positions = [(t['y'], t['x'], t['name']) for t in territories]
    
    # Calculate optimal positions
    for territory in territories:
        label_y, label_x = calculate_label_position(
            x=territory['x'],
            y=territory['y'],
            territory_name=territory['name'],
            strategy=strategy,
            all_positions=all_positions
        )
        
        territory['label_y'] = label_y
        territory['label_x'] = label_x
    
    return territories
