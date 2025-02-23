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
- Manage game sessions and player profiles.
- Track scores and statistics.
- Store and display faction data.
- Visualize game progress using interactive charts.

This tool is perfect for both game masters and players who want a digital companion to enhance their tabletop experience.

## Features

- **Interactive Dashboard:** Built with [Streamlit](https://docs.streamlit.io) for a smooth user experience.
- **Game Session Management:** Create, update, and track multiple game sessions.
- **Faction Management:** Easily add, edit, or remove factions.
- **Score Tracking:** Record and analyze game scores and player statistics.
- **Responsive Design:** Optimized for desktops and tablets.

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

  ```
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

3. **Install dependencies:**

Ensure your requirements.txt includes at least:

  ```
  streamlit
  pandas
  ```
Then run:

  ```
  pip install -r requirements.txt
  ```

## Usage
Start the application with Streamlit by running:

  ```
  streamlit run main.py
  ```

