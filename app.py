import streamlit as st
from auth_utils import register_user, login_user, get_recommendations 

# --- Page Configuration ---
st.set_page_config(page_title="RecommaI", layout="centered")

# --- Initialize Session State ---
# This is crucial. Session state remembers variables as the user interacts.
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""

# ===============================================
# ===         DEFINE THE PAGES/VIEWS          ===
# ===============================================

def show_login_page():
    """Displays the login and registration forms."""
    
    # Use columns to center the login box, similar to your template
    col1, col2, col3 = st.columns([1, 1.5, 1]) 

    with col2:
        with st.container(border=True):
            st.image("logo.png") # Make sure you have your logo file in the same folder
            st.title("Sign in to Unlock Your World")

            # Create two tabs for Login and Sign Up
            tab1, tab2 = st.tabs(["Log In", "Sign Up"])

            # --- LOGIN FORM ---
            with tab1:
                with st.form(key='login_form'):
                    email = st.text_input("Email Address", key="login_email")
                    password = st.text_input("Password", type="password", key="login_pass")
                    login_button = st.form_submit_button(label="Log In", use_container_width=True)
                    
                    if login_button:
                        success, message = login_user(email, password)
                        if success:
                            st.session_state['logged_in'] = True
                            st.session_state['user_email'] = email
                            st.rerun() # Rerun the script to show the main app
                        else:
                            st.error(message)

            # --- REGISTRATION FORM ---
            with tab2:
                with st.form(key='signup_form'):
                    reg_email = st.text_input("Email Address", key="reg_email")
                    reg_password = st.text_input("Create Password", type="password", key="reg_pass")
                    reg_confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")
                    signup_button = st.form_submit_button(label="Create Account", use_container_width=True)

                    if signup_button:
                        if reg_password == reg_confirm_pass:
                            success, message = register_user(reg_email, reg_password)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                        else:
                            st.error("Passwords do not match.")

def show_home_page():
    """Displays the main recommendation engine page."""
    
    # --- Top Navigation Bar ---
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.image("logo.png", width=150) 
    with col2:
        st.write(f"Welcome, {st.session_state['user_email']}")
    with col3:
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = ""
            st.rerun()

    st.divider()

    # --- Main Search Content ---
    st.title("Find Your Next Obsession")
    st.subheader("Enter an anime or a game title to get started!")

    search_query = st.text_input(
        "Search", 
        placeholder="e.g., One Piece, Elden Ring, or Studio Ghibli", 
        label_visibility="collapsed"
    )

    # --- THIS IS THE UPDATED LOGIC ---
    if search_query:
        # Call our new function to query the database
        recommendations, rec_domain = get_recommendations(search_query)

        if recommendations:
            st.subheader(f"Top 5 {rec_domain.capitalize()} recommendations for '{search_query}':")
            
            # Display each recommendation
            for rec in recommendations:
                # Format similarity as a percentage
                sim_percent = f"{rec['similarity'] * 100:.0f}% Similarity"
                
                # Use st.container to group each result
                with st.container(border=True):
                    st.markdown(f"**{rec['title']}**")
                    st.markdown(f"*{sim_percent}*")
        
        else:
            # Show this message if the search query returned no results
            st.warning("No recommendations found. Please check the spelling or try another title.")


# ===============================================
# ===        MAIN ROUTER LOGIC                ===
# ===============================================

if not st.session_state['logged_in']:
    show_login_page()
else:
    show_home_page()