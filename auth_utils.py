import psycopg2
import os
from dotenv import load_dotenv
import bcrypt
import streamlit as st

# Load .env variables
load_dotenv()
user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")
dbname = os.getenv("dbname") # Add your dbname to .env as well

# --- Database Connection ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# --- Password Hashing & Verification (This is the "strong encryption") ---

def hash_password(password):
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_pw.decode('utf-8') # Store as a string in the DB

def check_password(hashed_password, user_password):
    """Checks if the provided password matches the stored hash."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- User Management Functions ---

def register_user(email, password):
    """Registers a new user by hashing their password and saving to DB."""
    if not email or not password:
        return False, "Email and password are required."
        
    hashed_pw = hash_password(password)
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
                    (email, hashed_pw)
                )
                conn.commit()
            return True, "Registration successful! Please log in."
        except psycopg2.IntegrityError:
            return False, "Email already exists."
        except Exception as e:
            return False, f"An error occurred: {e}"
        finally:
            conn.close()
    return False, "Database connection failed."

def login_user(email, password):
    """Logs in a user by verifying their email and password hash."""
    if not email or not password:
        return False, "Please enter email and password."

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT email, password_hash FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                
                if user:
                    stored_email, stored_hash = user
                    # Verify password
                    if check_password(stored_hash, password):
                        return True, "Login successful!"
                    else:
                        return False, "Incorrect email or password."
                else:
                    return False, "Incorrect email or password."
        except Exception as e:
            return False, f"An error occurred: {e}"
        finally:
            conn.close()
            
    return False, "Database connection failed."

# ... (add this function at the end of the file, after your login/register functions)

def get_recommendations(search_title):
    """
    Fetches pre-calculated recommendations from the siamese_recommendations table
    based on the chosen_title.
    """
    conn = get_db_connection()
    if not conn:
        st.error("Database connection failed.")
        return [], None

    recommendations_list = []
    recommended_domain = "items" # Default text

    try:
        with conn.cursor() as cur:
            # We use ILIKE for a case-insensitive match and '%' as a wildcard.
            # This ensures that searching "one piece" will find "One Piece (1999)".
            query_term = f"%{search_title}%"
            
            cur.execute(
                "SELECT * FROM siamese_recommendations WHERE chosen_title ILIKE %s LIMIT 1",
                (query_term,)
            )
            
            result_row = cur.fetchone() # Get the first matching row

            if result_row:
                # Per your schema:
                # result_row[3] is rec_domain (e.g., "game" or "anime")
                recommended_domain = result_row[3]

                # Loop 5 times to get all 5 recommendations
                # Your recommendation data starts at index 4 (rec_id_1)
                # Each recommendation consists of 3 columns (id, title, percent)
                for i in range(5):
                    rec_title_index = 5 + (i * 3)
                    rec_percent_index = 6 + (i * 3)

                    title = result_row[rec_title_index]
                    percent = result_row[rec_percent_index]

                    # Add to list only if data exists
                    if title and percent is not None:
                        recommendations_list.append({
                            "title": title,
                            "similarity": percent
                        })
                
            return recommendations_list, recommended_domain

    except Exception as e:
        st.error(f"Error querying recommendations: {e}")
        return [], None
    finally:
        conn.close()