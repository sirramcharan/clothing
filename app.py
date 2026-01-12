import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
# 1. Paste the "Publish to Web" CSV link here:
INVENTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS488mmEiNdSNsGU3CbwItasQSkJQal-O1Uyt2cPVMXxiRYWp9UW3fyQlLRCZ36qp5MbOFbePpGj6kT/pub?gid=0&single=true&output=csv"

# 2. Paste the "Web App URL" from Apps Script here:
ORDER_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzCkOckpTZ2Tq8QondkNTipUmPc5TI_NQ44VTQWjuY3pZa01r7QUe1xQxWLhg_zbhFR/exec"

ADMIN_PASSWORD = st.secrets["admin_password"]

# --- GLASSMORPHISM CSS (Same as before) ---
def inject_custom_css():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e1e2f 0%, #252540 100%); color: white; }
    .glass-card {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px;
        padding: 20px; margin-bottom: 20px;
    }
    .stButton>button { background: linear-gradient(90deg, #ff8a00, #e52e71); color: white; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FUNCTIONS ---

def get_products():
    """Read inventory directly from the public CSV link"""
    try:
        # We read the CSV directly from the URL
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
    st.title("🌊 SHARK STREETWEAR")
    df = get_products()
    
    if df.empty:
        st.warning("No products found in the sheet.")
        return

    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            st.markdown(f"""
            <div class="glass-card">
                <img src="{row['image_url']}" style="width:100%; border-radius:10px; aspect-ratio: 1/1; object-fit: cover;">
                <h3 style="margin-top:10px;">{row['name']}</h3>
                <p>${row['price']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Buy {row['name']}", key=f"btn_{index}"):
                st.session_state.selected_product = row
                st.session_state.page = "order"
                st.rerun()

    st.markdown("---")
    st.markdown("<h3 style='text-align:center; opacity:0.6'>🦈 Hoodies Coming Soon</h3>", unsafe_allow_html=True)

def show_order():
    prod = st.session_state.selected_product
    st.button("← Back", on_click=lambda: st.session_state.update(page="shop"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(prod['image_url'])
    with col2:
        st.header(f"Order: {prod['name']}")
        with st.form("order_form"):
            name = st.text_input("Your Name")
            size = st.selectbox("Size", ["S", "M", "L", "XL"])
            phone = st.text_input("Phone Number")
            
            if st.form_submit_button("Place Order"):
                success = send_order(name, size, phone, prod['name'])
                if success:
                    st.success("✅ Order Placed! We'll text you.")
                    st.balloons()
                else:
                    st.error("❌ Connection failed.")

def show_admin():
    # Note: Adding products via Admin won't work perfectly with this method 
    # because we are reading a Read-Only CSV. 
    # You should add new products directly in the Google Sheet for this simple method.
    st.title("Admin Panel")
    pwd = st.text_input("Password", type="password")
    if pwd == ADMIN_PASSWORD:
        st.info("Since you are using the Simple Method, please add new T-shirts directly inside the Google Sheet 'Inventory' tab.")
        st.write("Current Live Inventory:")
        st.dataframe(get_products())

def main():
    inject_custom_css()
    with st.sidebar:
        st.title("Menu")
        if st.button("Shop"): st.session_state.page = "shop"; st.rerun()
        if st.button("Admin"): st.session_state.page = "admin"; st.rerun()

    if st.session_state.page == "shop": show_shop()
    elif st.session_state.page == "order": show_order()
    elif st.session_state.page == "admin": show_admin()

if __name__ == "__main__":
    main()
