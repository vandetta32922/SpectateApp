import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os

# File paths
USER_DATA_FILE = "users.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def register_user(username, password):
    user_data = load_user_data()
    if username in user_data:
        return "Username already exists!"
    user_data[username] = {"password": password, "verified": False}
    save_user_data(user_data)
    return "Registration successful! Please wait for admin verification."

def login_user(username, password):
    user_data = load_user_data()
    if username not in user_data:
        return "Username does not exist!"
    if user_data[username]["password"] != password:
        return "Incorrect password!"
    if not user_data[username]["verified"]:
        return "Account not verified yet!"
    return None

def fetch_player_names(region, rank):
    url = f"https://porofessor.gg/current-games/{region}/{rank}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        name_elements = soup.find_all('div', class_='name')
        names = [name.get_text(strip=True) for name in name_elements]
        return names if names else ["No summoners found for this rank in this region"]
    except requests.exceptions.RequestException as e:
        return [f"Error fetching player names: {str(e)}"]

def main():
    # Set default session state values
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'verified' not in st.session_state:
        st.session_state.verified = False

    if not st.session_state.logged_in:
        st.title("Login or Register")

        # Display login and registration forms
        menu = st.selectbox("Select an option", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if menu == "Register":
            if st.button("Register"):
                message = register_user(username, password)
                st.success(message)
        elif menu == "Login":
            if st.button("Login"):
                error = login_user(username, password)
                if error:
                    st.error(error)
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.verified = load_user_data().get(username, {}).get("verified", False)
                    st.experimental_rerun()

    if st.session_state.logged_in:
        if not st.session_state.verified:
            st.warning("Your account is not verified. Please contact the admin.")
            return

        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Select a Page", ["Home", "Documentation", "Logout"])

        if page == "Logout":
            st.session_state.logged_in = False
            st.session_state.verified = False
            st.session_state.username = None
            st.session_state.names = None
            st.experimental_rerun()

        if page == "Home":
            st.markdown("<h1 style='font-size: 24px;'>Summoner Names by Region and Rank</h1>", unsafe_allow_html=True)

            region = st.selectbox("Select Region:", [
                "EUW", "EUNE", "NA", "KR", "BR", "LAN", "LAS", "OCE", "TR", "RU", "JP", "ME1"
            ])
            rank = st.selectbox("Select Rank:", [
                "Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", 
                "Master", "Grandmaster", "Challenger"
            ])

            if st.button("Update Table"):
                st.session_state.page = 0
                st.session_state.names = fetch_player_names(region.lower(), rank.lower())

            if 'names' in st.session_state:
                names = st.session_state.names
                names_per_page = 10
                num_pages = (len(names) + names_per_page - 1) // names_per_page

                start = st.session_state.page * names_per_page
                end = min(start + names_per_page, len(names))
                st.write(f"Showing players for {region} and rank {rank}:")
                table_data = {"Summoner Name": names[start:end], "Rank": [rank.capitalize()] * (end - start)}
                st.table(table_data)

                # Pagination controls
                num_buttons = 10
                start_page = max(0, st.session_state.page - num_buttons // 2)
                end_page = min(num_pages, start_page + num_buttons)
                page_buttons = list(range(start_page, end_page))

                cols = st.columns(len(page_buttons))
                for i, page_num in enumerate(page_buttons):
                    with cols[i]:
                        if st.button(f"{page_num + 1}", key=f"page_{page_num}"):
                            st.session_state.page = page_num

                # Handle page navigation beyond 10 pages
                if start_page > 0:
                    if st.button("Prev", key="prev"):
                        st.session_state.page = max(0, start_page - num_buttons)
                if end_page < num_pages:
                    if st.button("Next", key="next"):
                        st.session_state.page = min(num_pages - 1, end_page)

                # Copy button functionality using JavaScript
                for name in names[start:end]:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(name)
                    with col2:
                        if st.button("Copy", key=f"copy_{name}"):
                            st.markdown(f"""
                            <script>
                            navigator.clipboard.writeText("{name}").then(() => {{
                                console.log('Text copied to clipboard');
                            }}, (err) => {{
                                console.error('Error copying text: ', err);
                            }});
                            </script>
                            """, unsafe_allow_html=True)
                            st.success(f"Copied {name} to clipboard")

        elif page == "Documentation":
            st.markdown("<h1 style='font-size: 24px;'>Documentation</h1>", unsafe_allow_html=True)

            st.markdown("<h2 style='font-size: 20px;'>API Overview</h2>", unsafe_allow_html=True)
            st.write("""
                **`fetch_player_names(region, rank)`**: Fetches player names for a given region and rank.
                
                - **Parameters**:
                  - `region`: The region to fetch player names from.
                  - `rank`: The rank to fetch player names for.
                - **Returns**: A list of player names.
            """)

            st.markdown("<h2 style='font-size: 20px;'>Regions</h2>", unsafe_allow_html=True)
            st.write("""
                The supported regions are:
                - EUW: Europe West
                - EUNE: Europe Nordic & East
                - NA: North America
                - KR: Korea
                - BR: Brazil
                - LAN: Latin America North
                - LAS: Latin America South
                - OCE: Oceania
                - TR: Turkey
                - RU: Russia
                - JP: Japan
                - ME1: Middle East
            """)

            st.markdown("<h2 style='font-size: 20px;'>Ranks</h2>", unsafe_allow_html=True)
            st.write("""
                The supported ranks are:
                - Iron
                - Bronze
                - Silver
                - Gold
                - Platinum
                - Emerald
                - Diamond
                - Master
                - Grandmaster
                - Challenger
            """)

if __name__ == "__main__":
    main()
