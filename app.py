import streamlit as st
import pandas as pd
import requests
import random

# --- CONFIGURATION ---
# 1. Paste the "Publish to Web" CSV link here:
INVENTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS488mmEiNdSNsGU3CbwItasQSkJQal-O1Uyt2cPVMXxiRYWp9UW3fyQlLRCZ36qp5MbOFbePpGj6kT/pub?gid=0&single=true&output=csv"

# 2. Paste the "Web App URL" from Apps Script here:
ORDER_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzCkOckpTZ2Tq8QondkNTipUmPc5TI_NQ44VTQWjuY3pZa01r7QUe1xQxWLhg_zbhFR/exec"

ADMIN_PASSWORD = st.secrets["admin_password"]

# --- NETFLIX THEMED CSS ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main Background - Netflix Dark */
    .stApp {
        background-color: #141414;
        color: white;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #333;
    }

    /* Titles */
    h1, h2, h3 {
        font-weight: 700; 
        color: #ffffff;
    }

    /* Netflix Red Buttons */
    .stButton>button {
        background-color: #E50914; /* Netflix Red */
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: transform 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #f40612;
        color: white;
        border: none;
        transform: scale(1.05);
    }

    /* Product Cards / Posters */
    .movie-card {
        background-color: #181818;
        border-radius: 8px;
        padding: 0px;
        transition: transform 0.3s;
        cursor: pointer;
        margin-bottom: 20px;
    }
    .movie-card:hover {
        transform: scale(1.05);
        z-index: 10;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    
    /* Image Rounded Corners */
    [data-testid="stImage"] img {
        border-radius: 4px;
    }

    /* Text on cards */
    .card-title {
        color: white;
        font-size: 1rem;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .card-price {
        color: #46d369; /* Netflix "Match" Green or just Grey */
        font-size: 0.9rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FUNCTIONS ---

def get_products():
    """Read inventory directly from the public CSV link"""
    try:
        df = pd.read_csv(INVENTORY_CSV_URL)
        return df
    except Exception as e:
        st.error("Could not load inventory. Check your CSV URL.")
        return pd.DataFrame()

def send_order(name, size, phone, item):
    """Send order data to the Google Apps Script Webhook"""
    data = {
        "name": name,
        "size": size,
        "phone": phone,
        "item": item
    }
    try:
        response = requests.post(ORDER_WEBHOOK_URL, json=data)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

# --- APP LOGIC ---

if 'page' not in st.session_state: st.session_state.page = "shop"
if 'selected_product' not in st.session_state: st.session_state.selected_product = None

def show_shop():
    # Netflix Header
    # You can replace this text with an Image Logo using st.image('logo.png')
    st.markdown("<h1 style='color: #E50914; font-size: 3rem;'>C-RAM <span style='color:white; font-size:1.5rem'>ORIGINALS</span></h1>", unsafe_allow_html=True)
    
    df = get_products()
    
    if df.empty:
        st.warning("No products found in the sheet.")
        return

    # --- HERO SECTION (Featured Item) ---
    # We pick a random item to display effectively as a "Banner"
    if not df.empty:
        # Pick a random product for the 'Hero' banner
        hero_item = df.sample(1).iloc[0]
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(to right, #000 0%, transparent 80%), url('{hero_item['image_url']}');
            background-size: cover;
            background-position: center;
            border-radius: 10px;
            padding: 50px;
            margin-bottom: 40px;
            height: 400px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            color: white;
        ">
            <h1 style="font-size: 3.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px #000;">{hero_item['name']}</h1>
            <p style="font-size: 1.5rem; margin-bottom: 20px; text-shadow: 1px 1px 2px #000;">Trending #1 in T-Shirts</p>
            <p style="color: #46d369; font-weight: bold; font-size: 1.2rem; text-shadow: 1px 1px 2px #000;">98% Match • ₹{hero_item['price']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Hero Buttons
        col_hero_1, col_hero_2 = st.columns([1, 4])
        with col_hero_1:
            if st.button("▶ Play (Buy)", key="hero_btn"):
                st.session_state.selected_product = hero_item
                st.session_state.page = "order"
                st.rerun()

    # --- ROW: TRENDING NOW ---
    st.markdown("### Trending Now")
    
    # Grid Layout
    cols = st.columns(4) # Netflix usually shows more items per row
    
    for index, row in df.iterrows():
        # Cycle through columns
        with cols[index % 4]:
            # Use a container for the hover effect style
            with st.container():
                st.image(row['image_url'], use_container_width=True)
                st.markdown(f"""
                <div style="padding: 5px;">
                    <div class="card-title">{row['name']}</div>
                    <div class="card-price">₹{row['price']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Add to List", key=f"btn_{index}"):
                    st.session_state.selected_product = row
                    st.session_state.page = "order"
                    st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align:center; color: #666; font-size: 0.8rem;'>C-Ram Inc. • 2026</p>", unsafe_allow_html=True)
    
def show_order():
    prod = st.session_state.selected_product
    
    # Back Button (Styled like a text link)
    if st.button("← Back to Browse"):
        st.session_state.page = "shop"
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(prod['image_url'])
    with col2:
        st.markdown(f"<h1 style='color:white;'>{prod['name']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#46d369;'>₹{prod['price']}</h3>", unsafe_allow_html=True)
        st.write("2026 | U/A 13+ | 1 Season | Suspenseful")
        st.markdown("This limited edition merchandise is trending. Order now before it leaves the platform.")
        
        st.markdown("---")
        with st.form("order_form"):
            name = st.text_input("Who's watching? (Name)")
            size = st.selectbox("Size Configuration", ["S", "M", "L", "XL"])
            phone = st.text_input("Account Number (Phone)")
            
            # Submit button will pick up the global Red styling
            if st.form_submit_button("Complete Order"):
                success = send_order(name, size, phone, prod['name'])
                if success:
                    st.success("✅ Added to your collection! We'll text you.")
                    st.balloons()
                else:
                    st.error("❌ Connection failed.")

def show_admin():
    st.title("Admin Settings")
    pwd = st.text_input("Enter Pin", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Access Granted")
        st.write("Live Content Library:")
        st.dataframe(get_products())

def main():
    inject_custom_css()
    
    # Custom Sidebar Navigation
    with st.sidebar:
        st.markdown("<h2 style='color:#E50914'>NETFLIX</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Home"): st.session_state.page = "shop"; st.rerun()
        if st.button("My List (Admin)"): st.session_state.page = "admin"; st.rerun()
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.info("Season 1 Streaming Now")

    if st.session_state.page == "shop": show_shop()
    elif st.session_state.page == "order": show_order()
    elif st.session_state.page == "admin": show_admin()

if __name__ == "__main__":
    main()
