import streamlit as st
from auth_utils import register_user, login_user # Import functions from our other file

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
    # Create columns for navigation, mimicking your template
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.image("logo.png", width=150) # Smaller logo on main page
    with col2:
        st.write(f"Welcome, {st.session_state['user_email']}") # Show logged-in user
    with col3:
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = ""
            st.rerun() # Rerun to go back to login page

    st.divider()

    # --- Main Search Content ---
    st.title("Find Your Next Obsession")
    st.subheader("Enter an anime or a game title to get started!")

    # The main search bar
    search_query = st.text_input(
        "Search", 
        placeholder="e.g., One Piece, Elden Ring, or Studio Ghibli", 
        label_visibility="collapsed"
    )

    if search_query:
        # --- THIS IS WHERE YOU CALL YOUR SIAMESE NETWORK ---
        # 1. Add your ML model loading logic here
        # 2. Call your model: recommendations = your_siamese_model.predict(search_query, k=5)
        # 3. Display the results:
        
        st.write(f"Top 5 recommendations based on '{search_query}':")
        
        # Example of how you would display the results (replace with your actual data)
        # for rec in recommendations:
        #    st.success(f"**{rec['title']}** - Score: {rec['similarity_score']:.2f}")
        #    st.write(rec['description'])
        
        st.write(f"(Dummy output: Your ML model will process '{search_query}' here)")


# ===============================================
# ===        MAIN ROUTER LOGIC                ===
# ===============================================

if not st.session_state['logged_in']:
    show_login_page()
else:
    show_home_page()