import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
INVENTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS488mmEiNdSNsGU3CbwItasQSkJQal-O1Uyt2cPVMXxiRYWp9UW3fyQlLRCZ36qp5MbOFbePpGj6kT/pub?gid=0&single=true&output=csv"
ORDER_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzCkOckpTZ2Tq8QondkNTipUmPc5TI_NQ44VTQWjuY3pZa01r7QUe1xQxWLhg_zbhFR/exec"
ADMIN_PASSWORD = st.secrets["admin_password"]

# --- YOUTUBE THEMED CSS ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main Background - YouTube Dark */
    .stApp {
        background-color: #0f0f0f;
        color: #f1f1f1;
        font-family: 'Roboto', Arial, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f; /* Same as main to blend in */
        border-right: 1px solid #2d2d2d;
    }

    /* YouTube Red Buttons */
    .stButton>button {
        background-color: #f1f1f1; /* White "Subscribe" style or Red */
        color: #0f0f0f;
        border: none;
        border-radius: 18px; /* Rounded pill shape */
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #d9d9d9;
    }
    
    /* Special "Buy" Buttons (Red) */
    .buy-btn > button {
        background-color: #FF0000;
        color: white;
    }

    /* Video Thumbnail Card */
    .video-card {
        background-color: transparent;
        cursor: pointer;
        margin-bottom: 20px;
    }
    
    /* Image Rounded Corners (YouTube style) */
    [data-testid="stImage"] img {
        border-radius: 12px;
    }

    /* Text on cards */
    .video-title {
        color: #f1f1f1;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 8px;
        line-height: 1.2;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .video-meta {
        color: #aaaaaa;
        font-size: 0.85rem;
        margin-top: 4px;
    }
    
    /* Hoodies Section */
    .hoodie-section {
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #2d2d2d;
        text-align: center;
        color: #aaaaaa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FUNCTIONS ---
def get_products():
    try:
        df = pd.read_csv(INVENTORY_CSV_URL)
        return df
    except:
        st.error("Could not load inventory.")
        return pd.DataFrame()

def send_order(name, size, phone, item):
    data = {"name": name, "size": size, "phone": phone, "item": item}
    try:
        requests.post(ORDER_WEBHOOK_URL, json=data)
        return True
    except:
        return False

# --- APP LOGIC ---
if 'page' not in st.session_state: st.session_state.page = "shop"
if 'selected_product' not in st.session_state: st.session_state.selected_product = None

def show_shop():
    # YouTube Style Header (Logo + Search Bar mock)
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown("<h2 style='margin:0; color:white; display:flex; align-items:center;'><span style='color:#FF0000; font-size:2rem; margin-right:5px;'>▶</span> CRX</h2>", unsafe_allow_html=True)
    with c2:
        # Mock Search Bar styling
        st.markdown("""
        <div style="background:#121212; border:1px solid #303030; border-radius:40px; padding:10px 20px; color:#888; width:100%; max-width:600px;">
            🔍 &nbsp; Search merchandise...
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filter Tabs (Chips)
    st.markdown("""
    <div style="display:flex; gap:10px; margin-bottom:20px; overflow-x:auto;">
        <span style="background:#f1f1f1; color:black; padding:5px 12px; border-radius:8px; font-weight:500; font-size:0.9rem;">All</span>
        <span style="background:#272727; color:white; padding:5px 12px; border-radius:8px; font-weight:500; font-size:0.9rem;">T-Shirts</span>
        <span style="background:#272727; color:white; padding:5px 12px; border-radius:8px; font-weight:500; font-size:0.9rem;">Accessories</span>
        <span style="background:#272727; color:white; padding:5px 12px; border-radius:8px; font-weight:500; font-size:0.9rem;">Live</span>
    </div>
    """, unsafe_allow_html=True)

    df = get_products()
    if df.empty: return

    # Grid Layout (YouTube Video Grid)
    cols = st.columns(3)
    
    for index, row in df.iterrows():
        with cols[index % 3]:
            # Image (Thumbnail)
            st.image(row['image_url'], use_container_width=True)
            
            # Metadata (Profile pic + Title)
            c_meta_1, c_meta_2 = st.columns([1, 5])
            with c_meta_1:
                # Mock Profile Pic
                st.markdown("<div style='width:36px; height:36px; background:#555; border-radius:50%; margin-top:5px;'></div>", unsafe_allow_html=True)
            with c_meta_2:
                st.markdown(f"""
                <div class="video-title">{row['name']}</div>
                <div class="video-meta">C-Ram Official • 2.4K views • 1 day ago</div>
                <div class="video-meta" style="color:#FF0000; font-weight:bold;">₹{row['price']}</div>
                """, unsafe_allow_html=True)
            
            if st.button(f"Buy Now", key=f"btn_{index}"):
                st.session_state.selected_product = row
                st.session_state.page = "order"
                st.rerun()
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # --- 1. HOODIES COMING SOON SECTION ---
    st.markdown("""
    <div class="hoodie-section">
        <h3 style="color:white;">🦈 Hoodies Coming Soon</h3>
        <p>Turn on notifications to get notified when they drop.</p>
        <button style="background:#272727; border:none; color:#aaa; padding:10px 20px; border-radius:18px; margin-top:10px;">Notify Me</button>
    </div>
    """, unsafe_allow_html=True)

def show_order():
    prod = st.session_state.selected_product
    
    # YouTube "Watch Page" Layout
    c_main, c_rec = st.columns([2, 1])
    
    with c_main:
        st.image(prod['image_url'], use_container_width=True)
        st.markdown(f"<h2 style='margin-top:10px;'>{prod['name']}</h2>", unsafe_allow_html=True)
        
        # Action Bar
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:40px; height:40px; background:#FF0000; border-radius:50%;"></div>
                <div>
                    <div style="font-weight:bold;">C-Ram Official</div>
                    <div style="font-size:0.8rem; color:#aaa;">1.2M subscribers</div>
                </div>
                <button style="background:white; color:black; border:none; padding:8px 16px; border-radius:18px; font-weight:bold; margin-left:20px;">Subscribe</button>
            </div>
            <div style="display:flex; gap:10px;">
                 <span style="background:#272727; padding:8px 16px; border-radius:18px;">👍 12K</span>
                 <span style="background:#272727; padding:8px 16px; border-radius:18px;">👎</span>
                 <span style="background:#272727; padding:8px 16px; border-radius:18px;">Share</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### Price: ₹{prod['price']}")
        
        # Order Form
        with st.container(border=True):
            st.markdown("#### Buy this merchandise")
            with st.form("order_form"):
                name = st.text_input("Name")
                size = st.selectbox("Size", ["S", "M", "L", "XL"])
                phone = st.text_input("Phone")
                if st.form_submit_button("Confirm Purchase"):
                    if send_order(name, size, phone, prod['name']):
                        st.success("Order Placed!")
                        st.balloons()
                    else:
                        st.error("Error.")
            if st.button("Cancel / Back"):
                st.session_state.page = "shop"
                st.rerun()

    with c_rec:
        st.markdown("#### Recommended")
        # Just simulated recommendations
        for i in range(3):
            st.markdown(f"""
            <div style="display:flex; gap:10px; margin-bottom:10px;">
                <div style="width:168px; height:94px; background:#333; border-radius:8px;"></div>
                <div>
                    <div style="font-size:0.9rem; font-weight:bold; line-height:1.2;">Upcoming Design #{i+1}</div>
                    <div style="font-size:0.8rem; color:#aaa;">C-Ram Clips</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_admin():
    st.title("Studio Dashboard")
    if st.text_input("Password", type="password") == ADMIN_PASSWORD:
        st.dataframe(get_products())

def main():
    inject_custom_css()
    with st.sidebar:
        st.markdown("### Guide")
        if st.button("🏠 Home"): st.session_state.page = "shop"; st.rerun()
        if st.button("🛍️ Shorts (Orders)"): st.session_state.page = "shop"; st.rerun()
        if st.button("⚙️ Studio (Admin)"): st.session_state.page = "admin"; st.rerun()
        st.markdown("---")
        st.markdown("Made with Streamlit")

    if st.session_state.page == "shop": show_shop()
    elif st.session_state.page == "order": show_order()
    elif st.session_state.page == "admin": show_admin()

if __name__ == "__main__":
    main()
