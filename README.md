# Necromunda Game Manager

A web-based game management tool for the tabletop wargame **Necromunda** built with **Python** and **Streamlit**. This project aims to help players and game masters manage games, track scores, and handle faction information in an interactive and user-friendly interface.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)

## Overview

The **Necromunda Game Manager** simplifies the process of organizing and managing games for Necromunda. It provides an intuitive interface to:
- Manage gangs and their fighters
- Track territories and their ownership
- Record battle results and campaign progression
- Visualize game data through interactive charts and maps
- Import data from Yaktribe

This tool is perfect for both game masters and players who want a digital companion to enhance their tabletop experience.

## Features

- **Interactive Dashboard:** Visual analytics including gang reputation, territory control, and battle history
- **Gang Management:** Create and manage gangs, fighters, and equipment
- **Territory System:** Track territory ownership with an interactive map
- **Battle Tracking:** Record battle outcomes and their impact on the campaign
- **Data Visualization:** Charts, maps, and data tables for campaign analysis
- **Yaktribe Integration:** Import your gang data from Yaktribe
- **Automatic Backups:** Secure backup system to prevent data loss

## Installation

### Prerequisites

- Python 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yakuzadave/Necromunda-Game-Manager
   cd Necromunda-Game-Manager
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**

   ```bash
   streamlit run main.py
   ```

2. **Navigate to the application in your browser:**
   - The application will open automatically in your default browser
   - If not, navigate to the URL shown in your terminal (typically http://localhost:8501)

3. **First-time setup:**
   - Create your first gang in the "Gangs" section
   - Add territories in the "Territories" section
   - Start recording battles in the "Battles" section

## Project Structure

