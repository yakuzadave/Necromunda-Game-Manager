import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from streamlit_chat import message
from streamlit.components.v1 import html

# Set the title of the web app
st.title("Tabletop Manager")

# Create a sidebar with a text input and a button
st.sidebar.title("Tabletop Manager")


def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.past.append(user_input)
    st.session_state.generated.append("The messages from Bot\nWith new line")

def on_btn_click():
    del st.session_state.past[:]
    del st.session_state.generated[:]

# Create the base sidebar in streamlit with default width 
# Create a sidebar with a selectbox for choosing the game type
sidebar_option = st.sidebar.selectbox("Select Game Type:", ('Board Game', 'Card Game', 'RPG'))

# Create a sidebar with a slider for the number of players
num_players = st.sidebar.slider("Number of Players:", 1, 10)

# Create a sidebar with a checkbox for game availability
is_available = st.sidebar.checkbox("Available")

# Create a text input for the user to enter their name
name = st.sidebar.text_input("Enter your name:")
# Create a button for the user to click
button = st.sidebar.button("Submit")
# If the button is clicked, display a message with the user's name
if button:
    st.sidebar.success(f"Hello, {name}!")

# Create a text input for the user to enter the name of the tabletop


# Define constant variables for the data source and date column name
DATE_COLUMN = 'OrderDate'
DATA_URL = 'quantity.csv'

# Function to load data from the CSV file with a specified number of rows
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Create a text element to let the reader know the data is loading
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe
data = load_data(10000)
# Notify the reader that the data was successfully loaded
data_load_state.text('Loading data...done!')

# Display the raw data in a subheader
st.subheader('Raw data')
st.write(data)
