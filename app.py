import streamlit as st
import pandas as pd
import requests
import random

# --- CONFIGURATION (Your Links) ---
INVENTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS488mmEiNdSNsGU3CbwItasQSkJQal-O1Uyt2cPVMXxiRYWp9UW3fyQlLRCZ36qp5MbOFbePpGj6kT/pub?gid=0&single=true&output=csv"
ORDER_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzCkOckpTZ2Tq8QondkNTipUmPc5TI_NQ44VTQWjuY3pZa01r7QUe1xQxWLhg_zbhFR/exec"
ADMIN_PASSWORD = st.secrets["admin_password"]

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="C-RAM Originals",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. NETFLIX UI CSS (The "Beauty in Details") ---
def inject_netflix_css():
    st.markdown("""
    <style>
    /* RESET & BASICS */
    @import url('https://fonts.googleapis.com/css2?family=Martel+Sans:wght@200;400;700;800&display=swap');
    
    .stApp {
        background-color: #141414; /* Netflix Background */
        color: white;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* REMOVE STREAMLIT PADDING */
    .block-container {
        padding-top: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- NAVBAR --- */
    .netflix-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 40px;
        background: linear-gradient(to bottom, rgba(0,0,0,0.7) 10%, rgba(0,0,0,0));
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
    }
    .nav-left { display: flex; align-items: center; gap: 20px; }
    .nav-logo { color: #E50914; font-size: 30px; font-weight: bold; text-decoration: none; margin-right: 20px; }
    .nav-link { color: #e5e5e5; text-decoration: none; font-size: 14px; transition: color 0.3s; }
    .nav-link:hover { color: #b3b3b3; }
    .nav-right { display: flex; align-items: center; gap: 15px; font-size: 14px; }

    /* --- BILLBOARD (HERO) --- */
    .billboard-container {
        position: relative;
        height: 70vh; /* 70% of viewport height */
        width: 100%;
        color: white;
        margin-bottom: -100px; /* Pull rows up slightly */
        overflow: hidden;
    }
    .billboard-bg {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-size: cover;
        background-position: center top;
        z-index: 0;
    }
    /* The Vignette (Gradient Fade) */
    .billboard-gradient {
        background: linear-gradient(0deg, #141414 0%, transparent 50%);
        position: absolute;
        width: 100%; height: 100%;
        top: 0; z-index: 1;
    }
    .billboard-left-gradient {
        background: linear-gradient(90deg, rgba(20,20,20,0.8) 0%, transparent 60%);
        position: absolute;
        width: 40%; height: 100%;
        top: 0; z-index: 1;
    }
    .billboard-content {
        position: relative;
        z-index: 2;
        padding-top: 20vh;
        padding-left: 40px;
        max-width: 500px;
    }
    .billboard-title {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.45);
    }
    .billboard-desc {
        font-size: 1.2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.45);
        margin-bottom: 20px;
        font-weight: 400;
    }
    
    /* --- BUTTONS --- */
    /* Primary White Button (Play) */
    .btn-play {
        background-color: white;
        color: black;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 4px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        transition: background-color 0.2s;
    }
    .btn-play:hover { background-color: rgba(255, 255, 255, 0.75); }

    /* Secondary Gray Button (More Info) */
    .btn-info {
        background-color: rgba(109, 109, 110, 0.7);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 4px;
        cursor: pointer;
        margin-left: 10px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        transition: background-color 0.2s;
    }
    .btn-info:hover { background-color: rgba(109, 109, 110, 0.4); }

    /* --- ROWS & CARDS --- */
    .row-header {
        font-size: 1.4vw;
        color: #e5e5e5;
        font-weight: 700;
        margin-left: 40px;
        margin-bottom: 10px;
        margin-top: 20px;
        z-index: 10;
        position: relative;
    }
    
    /* Card Container */
    .card-container {
        transition: transform 0.3s;
        cursor: pointer;
        position: relative;
    }
    .card-container:hover {
        transform: scale(1.05); /* The signature Netflix Pop */
        z-index: 100;
    }
    
    /* Streamlit Image styling override */
    [data-testid="stImage"] img {
        border-radius: 4px;
    }

    /* Card Metadata (Match score etc) */
    .meta-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 8px;
        font-size: 0.8rem;
    }
    .match-score { color: #46d369; font-weight: bold; }
    .maturity-rating { border: 1px solid #808080; padding: 0 4px; font-size: 0.7rem; color: #bcbcbc; }
    .quality-badge { border: 1px solid #808080; border-radius: 3px; padding: 0 4px; font-size: 0.6rem; color: #bcbcbc; }

    /* --- FORM STYLING --- */
    input, select {
        background-color: #333 !important;
        color: white !important;
        border: none !important;
        border-bottom: 2px solid #E50914 !important; /* Red underline */
    }
    
    /* Custom Streamlit Button Override for the whole app to be generic, 
       we use custom HTML buttons for the specific Netflix look where possible */
    .stButton > button {
        background-color: #E50914;
        color: white;
        border-radius: 2px;
        font-weight: bold;
        border: none;
    }
    
    /* Hide the top colored bar of Streamlit */
    header[data-testid="stHeader"] {background:none;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA FUNCTIONS ---
@st.cache_data(ttl=600)
def get_products():
    try:
        df = pd.read_csv(INVENTORY_CSV_URL)
        return df
    except:
        return pd.DataFrame()

def send_order(name, size, phone, item):
    data = {"name": name, "size": size, "phone": phone, "item": item}
    try:
        requests.post(ORDER_WEBHOOK_URL, json=data)
        return True
    except:
        return False

# --- UI COMPONENTS ---

def render_navbar():
    st.markdown("""
    <div class="netflix-nav">
        <div class="nav-left">
            <div class="nav-logo">C-RAM</div>
            <a href="#" class="nav-link">Home</a>
            <a href="#" class="nav-link">T-Shirts</a>
            <a href="#" class="nav-link">Accessories</a>
            <a href="#" class="nav-link">My List</a>
        </div>
        <div class="nav-right">
            <span>🔍</span>
            <span>🔔</span>
            <div style="width:30px; height:30px; background-color:#b3b3b3; border-radius:4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero(item):
    """
    Renders the massive 'Billboard' at the top using the item's image as background.
    """
    if item is None: return

    # We use CSS Grid/Flex inside the markdown to layer the image and text
    html_hero = f"""
    <div class="billboard-container">
        <div class="billboard-bg" style="background-image: url('{item['image_url']}');"></div>
        <div class="billboard-gradient"></div>
        <div class="billboard-left-gradient"></div>
        
        <div class="billboard-content">
            <div style="margin-bottom:10px; color: #E50914; font-weight:bold; letter-spacing: 2px;"> N SERIES</div>
            <div class="billboard-title">{item['name']}</div>
            <div class="billboard-desc">
                Ranked #1 in Apparel Today.<br>
                This limited edition design captures the essence of street style. 
                Gritty, raw, and authentically yours.
            </div>
            <div style="display:flex; gap:15px;">
                </div>
        </div>
    </div>
    """
    st.markdown(html_hero, unsafe_allow_html=True)
    
    # Position actual clickable Streamlit buttons "inside" the layout visually
    # We use columns to align them with the text above
    c1, c2, c3 = st.columns([0.1, 0.3, 0.6])
    with c2:
        # This button is styled via CSS to look like the "Play" button
        if st.button(f"▶ Play (Buy ₹{item['price']})", key="hero_play"):
            st.session_state.selected_product = item
            st.session_state.page = "order"
            st.rerun()

def render_row(title, df, key_prefix):
    """
    Renders a horizontal list of products.
    """
    if df.empty: return

    st.markdown(f'<div class="row-header">{title}</div>', unsafe_allow_html=True)
    
    # Create 4 columns for the row
    cols = st.columns(4)
    for i, (index, row) in enumerate(df.iterrows()):
        col = cols[i % 4]
        with col:
            # Image
            st.image(row['image_url'], use_container_width=True)
            
            # Metadata block (The Netflix Match Score look)
            st.markdown(f"""
            <div class="meta-row">
                <span class="match-score">{random.randint(95, 99)}% Match</span>
                <span class="maturity-rating">U/A 13+</span>
                <span class="maturity-rating">4K</span>
            </div>
            <div style="font-size: 0.9rem; margin-top:5px; font-weight:bold;">{row['name']}</div>
            <div style="font-size: 0.8rem; color:#b3b3b3;">Gritty • Dark • Urban</div>
            """, unsafe_allow_html=True)
            
            # Action Button
            if st.button(f"Details", key=f"{key_prefix}_{index}"):
                st.session_state.selected_product = row
                st.session_state.page = "order"
                st.rerun()

# --- PAGES ---

def page_home():
    render_navbar()
    df = get_products()
    
    if df.empty:
        st.error("No inventory found.")
        return

    # 1. Billboard (Hero) - Randomly select one item
    hero_item = df.sample(1).iloc[0]
    render_hero(hero_item)

    # 2. Rows
    # We simulate different categories by shuffling the dataframe
    st.markdown("<div style='margin-top: -50px; position: relative; z-index: 5;'>", unsafe_allow_html=True)
    
    render_row("Trending Now", df, "trend")
    render_row("New Releases", df.sample(frac=1), "new")
    render_row("Because you bought 'Black T-Shirt'", df.sample(frac=1), "rec")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Footer / Coming Soon
    st.markdown("""
    <br><br><br>
    <div style="text-align:center; color: #666;">
        <h3>🦈 Hoodies Coming Soon</h3>
        <p>Questions? Call 000-800-040-1843</p>
        <p style="font-size:0.7rem; margin-top:20px;">C-RAM Inc.</p>
    </div>
    """, unsafe_allow_html=True)

def page_order():
    render_navbar()
    prod = st.session_state.selected_product
    
    # Back button
    st.markdown("<br><br><br>", unsafe_allow_html=True) # Spacer for fixed nav
    if st.button("← Back to Browse"):
        st.session_state.page = "shop"
        st.rerun()
        
    # Layout: Two columns, Left is details/form, Right is image (flipped standard layout for cinematic feel)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.image(prod['image_url'], use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <h1 style="font-size: 3rem; margin-bottom: 0;">{prod['name']}</h1>
        <div class="meta-row" style="font-size: 1.1rem; margin-bottom: 20px;">
            <span class="match-score">98% Match</span>
            <span style="color:#b3b3b3">2026</span>
            <span class="maturity-rating">U/A 13+</span>
            <span style="color:#b3b3b3">Limited Edition</span>
        </div>
        <p style="font-size: 1.2rem; line-height: 1.5;">
            This merchandise is currently trending in your area. 
            High-quality fabric meeting the specific C-RAM aesthetics. 
            Order now to secure your piece before the season ends.
        </p>
        <h2 style="color: #46d369;">₹{prod['price']}</h2>
        <hr style="border-color: #333;">
        """, unsafe_allow_html=True)

        with st.form("netflix_form"):
            st.markdown("### Complete your order")
            name = st.text_input("Name", placeholder="Who is watching?")
            size = st.selectbox("Size", ["S", "M", "L", "XL", "XXL"])
            phone = st.text_input("Phone Number", placeholder="For delivery updates")
            
            submitted = st.form_submit_button("Start Membership (Buy)")
            
            if submitted:
                if send_order(name, size, phone, prod['name']):
                    st.success("Welcome to the C-RAM family. Order confirmed.")
                    st.balloons()
                else:
                    st.error("Network Error. Please try again.")

def page_admin():
    st.title("Admin")
    pwd = st.text_input("Password", type="password")
    if pwd == ADMIN_PASSWORD:
        st.dataframe(get_products())
    if st.button("Back"):
        st.session_state.page = "shop"
        st.rerun()

# --- MAIN CONTROLLER ---
def main():
    inject_netflix_css()
    
    # Initialize Session State
    if 'page' not in st.session_state: st.session_state.page = "shop"
    if 'selected_product' not in st.session_state: st.session_state.selected_product = None

    # Routing
    if st.session_state.page == "shop":
        page_home()
    elif st.session_state.page == "order":
        page_order()
    elif st.session_state.page == "admin":
        page_admin()

if __name__ == "__main__":
    main()
