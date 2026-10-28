"""
HotelPro — Modern Hotel Management Solution
Ready for Streamlit Community Cloud and Local Execution.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os
import database as db

# Page setup
st.set_page_config(
    page_title="HotelPro — Hotel Management Solution",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_db()

# Custom CSS for styling
st.markdown("""
<style>
    /* Global styles */
    .main {
        background-color: #FAFAFA;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Header branding */
    .brand-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F5132;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0px;
    }
    .brand-subtitle {
        color: #6C757D;
        font-size: 0.95rem;
        margin-top: -4px;
        margin-bottom: 20px;
    }

    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #E9ECEF;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6C757D;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #1A202C;
        margin: 6px 0;
    }
    .metric-note {
        font-size: 0.8rem;
        color: #0F5132;
        font-weight: 500;
    }
    
    /* Status Badges */
    .badge-available {
        background-color: #D1E7DD;
        color: #0F5132;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-occupied {
        background-color: #FFF3CD;
        color: #664D03;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-maintenance {
        background-color: #F8D7DA;
        color: #842029;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-confirmed {
        background-color: #CFE2FF;
        color: #084298;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-paid {
        background-color: #D1E7DD;
        color: #0F5132;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-pending {
        background-color: #FFF3CD;
        color: #856404;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }

    /* Room Cards */
    .room-card {
        background: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    
    /* Welcome Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F5132 0%, #198754 100%);
        border-radius: 14px;
        color: #FFFFFF;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 6px 18px rgba(15, 81, 50, 0.15);
    }
    .hero-banner h2 {
        color: #FFFFFF !important;
        margin: 0 0 6px 0;
        font-size: 1.6rem;
    }
    .hero-banner p {
        color: #D1E7DD;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Invoice Card */
    .invoice-container {
        background: #FFFFFF;
        border: 1px solid #DEE2E6;
        border-radius: 12px;
        padding: 30px;
        max-width: 720px;
        margin: 0 auto;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Helper formatting functions
def format_currency(val):
    try:
        return f"₹{int(float(val)):,}"
    except (ValueError, TypeError):
        return f"₹{val}"

def format_date(val):
    if not val:
        return "—"
    try:
        d = datetime.date.fromisoformat(str(val))
        return d.strftime("%d %b %Y")
    except Exception:
        return str(val)

# Session state initialization for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

def login_user(user_obj):
    st.session_state.logged_in = True
    st.session_state.user = user_obj

def logout_user():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# -------------------------------------------------------------
# AUTHENTICATION SCREEN
# -------------------------------------------------------------
if not st.session_state.logged_in:
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
            <div style="font-size: 3rem;">🏨</div>
            <h1 style="color: #0F5132; margin-bottom: 4px;">HotelPro</h1>
            <p style="color: #6C757D; font-size: 1.05rem;">The Art of Modern Hospitality Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register, tab_info = st.tabs(["🔑 Sign In", "✨ Create Account", "ℹ️ Demo Access"])
        
        with tab_login:
            st.markdown("##### Good to have you back")
            st.caption("Sign in with your HotelPro administrator or staff credentials.")
            
            with st.form("login_form"):
                email = st.text_input("Email address", placeholder="admin@hotelpro.com").strip().lower()
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In to Workspace ➜", use_container_width=True, type="primary")
                
                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        user, msg = db.authenticate_user(email, password)
                        if user:
                            login_user(user)
                            st.success(f"Welcome back, {user['name']}!")
                            st.rerun()
                        else:
                            st.error(msg)
                            
        with tab_register:
            st.markdown("##### Create your workspace")
            st.caption("Set up an administrator account to get started.")
            
            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Aanya Sharma")
                reg_email = st.text_input("Email address", placeholder="aanya@hotelpro.com").strip().lower()
                reg_password = st.text_input("Password (min 6 characters)", type="password", placeholder="••••••••")
                reg_role = st.selectbox("Role", ["Administrator", "Front Desk Staff", "Manager"])
                reg_submitted = st.form_submit_button("Create Account ➜", use_container_width=True, type="primary")
                
                if reg_submitted:
                    if not reg_name or not reg_email or not reg_password:
                        st.error("Please fill in all required fields.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        success, msg = db.register_user(reg_name, reg_email, reg_password, reg_role)
                        if success:
                            st.success(f"{msg} You may now sign in using the 'Sign In' tab.")
                        else:
                            st.error(msg)
                            
        with tab_info:
            st.info("""
            **Pre-configured Demo Accounts:**
            - **Administrator:** `admin@hotelpro.com` / `admin123`
            - **Front Desk Staff:** `staff@hotelpro.com` / `staff123`
            
            Click **Sign In** and enter either credential set above for quick evaluation.
            """)
            
    st.stop()


# -------------------------------------------------------------
# MAIN DASHBOARD APPLICATION (LOGGED IN)
# -------------------------------------------------------------

# Fetch fresh data
rooms = db.get_all_rooms()
reservations = db.get_all_reservations()
guest_summary = db.get_guest_summary()

# Metrics calculations
total_rooms = len(rooms)
occupied_rooms = len([r for r in rooms if r["status"] == "Occupied"])
available_rooms = len([r for r in rooms if r["status"] == "Available"])
maintenance_rooms = len([r for r in rooms if r["status"] == "Maintenance"])
occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0

active_bookings = len([r for r in reservations if r["status"] in ("Confirmed", "Checked-in")])
total_revenue = sum([r["total_amount"] for r in reservations if r["status"] != "Cancelled"])
pending_payments = sum([r["total_amount"] for r in reservations if r["payment_status"] == "Pending" and r["status"] != "Cancelled"])
unique_guests = len(guest_summary)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="font-size: 2rem;">🏨</span>
        <div>
            <h3 style="margin: 0; color: #0F5132; font-weight: 700;">HotelPro</h3>
            <span style="font-size: 0.75rem; color: #6C757D; letter-spacing: 0.5px;">MANAGEMENT SYSTEM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # User Profile card
    user = st.session_state.user or {"name": "Admin User", "role": "Administrator"}
    st.markdown(f"""
    <div style="background: #F1F8F5; border: 1px solid #D1E7DD; border-radius: 8px; padding: 10px 14px; margin-bottom: 20px;">
        <div style="font-weight: 600; color: #0F5132;">👤 {user.get('name', 'Admin')}</div>
        <div style="font-size: 0.8rem; color: #6C757D;">{user.get('role', 'Administrator')}</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "NAVIGATION",
        [
            "📊 Overview & Analytics",
            "🛏️ Room Inventory",
            "📅 Reservations & Bookings",
            "👥 Guest Directory",
            "🧾 Billing & Invoices",
            "⚙️ Deployment & Settings"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # Quick Status
    st.caption("SYSTEM STATUS")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #0F5132; font-weight: 600; display: flex; align-items: center; gap: 6px;">
        <span>🟢</span> All systems operational
    </div>
    """, unsafe_allow_html=True)
    st.caption("Database: SQLite (Embedded) + Atlas Sync Ready")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sign Out ➔", use_container_width=True):
        logout_user()


# =============================================================
# PAGE 1: OVERVIEW & ANALYTICS
# =============================================================
if menu == "📊 Overview & Analytics":
    # Hero Welcome Banner
    st.markdown(f"""
    <div class="hero-banner">
        <h2>Good day, {user.get('name', 'there').split()[0]} ✦</h2>
        <p>Here is what is happening across your hotel property today. Monitor occupancy, track active guests, and streamline daily operations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Rooms</div>
            <div class="metric-value">{total_rooms}</div>
            <div class="metric-note">{available_rooms} currently available</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Bookings</div>
            <div class="metric-value">{active_bookings}</div>
            <div class="metric-note">{len([r for r in reservations if r['status'] == 'Checked-in'])} checked-in today</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Occupancy Rate</div>
            <div class="metric-value">{occupancy_rate}%</div>
            <div class="metric-note">{occupied_rooms} of {total_rooms} rooms booked</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">{format_currency(total_revenue)}</div>
            <div class="metric-note">Lifetime confirmed stays</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Unique Guests</div>
            <div class="metric-value">{unique_guests}</div>
            <div class="metric-note">Across registered bookings</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Section
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("Room Availability Breakdown")
        status_counts = {
            "Available": available_rooms,
            "Occupied": occupied_rooms,
            "Maintenance": maintenance_rooms
        }
        status_df = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
        
        fig_donut = px.pie(
            status_df, 
            values="Count", 
            names="Status", 
            hole=0.55,
            color="Status",
            color_discrete_map={
                "Available": "#198754",
                "Occupied": "#FFC107",
                "Maintenance": "#DC3545"
            }
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            height=300
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Revenue by Room Type")
        if reservations:
            res_df = pd.DataFrame(reservations)
            valid_res = res_df[res_df["status"] != "Cancelled"]
            if not valid_res.empty:
                rev_by_type = valid_res.groupby("room_type")["total_amount"].sum().reset_index()
                fig_bar = px.bar(
                    rev_by_type, 
                    x="room_type", 
                    y="total_amount", 
                    labels={"room_type": "Room Category", "total_amount": "Revenue (₹)"},
                    color="room_type",
                    color_discrete_sequence=["#0F5132", "#198754", "#20C997", "#0D6EFD"]
                )
                fig_bar.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    showlegend=False,
                    height=300
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No completed reservations to display revenue trends.")
        else:
            st.info("No reservations added yet.")
            
    st.markdown("---")
    
    # Recent Bookings Table
    st.subheader("Recent Guest Reservations")
    if reservations:
        recent = reservations[:5]
        table_data = []
        for r in recent:
            table_data.append({
                "Guest Name": r["guest_name"],
                "Email": r["guest_email"],
                "Room": f"{r['room_number']} ({r['room_type']})",
                "Stay Dates": f"{format_date(r['check_in'])} → {format_date(r['check_out'])}",
                "Status": r["status"],
                "Payment": r["payment_status"],
                "Amount": format_currency(r["total_amount"])
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
    else:
        st.info("No reservations recorded yet.")


# =============================================================
# PAGE 2: ROOM INVENTORY MANAGEMENT
# =============================================================
elif menu == "🛏️ Room Inventory":
    st.title("Room Inventory Management")
    st.caption("Manage room numbers, categories, pricing per night, and maintenance statuses.")
    
    tab_rooms_view, tab_add_room = st.tabs(["📋 View & Filter Rooms", "➕ Add New Room"])
    
    with tab_rooms_view:
        # Filter controls
        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col1:
            search_room = st.text_input("🔍 Search by room number or amenities", "")
        with f_col2:
            filter_type = st.selectbox("Room Type", ["All Categories", "Single", "Double", "Deluxe", "Suite"])
        with f_col3:
            filter_status = st.selectbox("Status", ["All Statuses", "Available", "Occupied", "Maintenance"])
            
        filtered_rooms = rooms
        if search_room:
            filtered_rooms = [
                r for r in filtered_rooms 
                if search_room.lower() in r["number"].lower() or search_room.lower() in (r.get("amenities") or "").lower()
            ]
        if filter_type != "All Categories":
            filtered_rooms = [r for r in filtered_rooms if r["type"] == filter_type]
        if filter_status != "All Statuses":
            filtered_rooms = [r for r in filtered_rooms if r["status"] == filter_status]
            
        st.markdown(f"**Showing {len(filtered_rooms)} of {len(rooms)} rooms**")
        
        # Room Cards Grid
        cols_per_row = 3
        for i in range(0, len(filtered_rooms), cols_per_row):
            row_rooms = filtered_rooms[i:i+cols_per_row]
            cols = st.columns(cols_per_row)
            for idx, r in enumerate(row_rooms):
                with cols[idx]:
                    status_class = f"badge-{r['status'].lower()}"
                    with st.container(border=True):
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: #1A202C;">Room {r['number']}</h3>
                            <span class="{status_class}">{r['status']}</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #6C757D; margin-top: 4px;">{r['type']} Bed</div>
                        <h4 style="color: #0F5132; margin: 10px 0;">{format_currency(r['price'])} <span style="font-size: 0.8rem; font-weight: normal; color: #6C757D;">/ night</span></h4>
                        <div style="font-size: 0.82rem; color: #495057; background: #F8F9FA; padding: 6px 10px; border-radius: 6px; margin-bottom: 12px;">
                            ✨ {r.get('amenities', 'Wi-Fi, AC')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Edit / Delete actions in expander
                        with st.expander(f"⚙️ Manage Room {r['number']}"):
                            edit_price = st.number_input(f"Price (₹) - Room {r['number']}", min_value=100.0, value=float(r['price']), step=100.0, key=f"p_{r['id']}")
                            edit_status = st.selectbox(f"Status - Room {r['number']}", ["Available", "Occupied", "Maintenance"], index=["Available", "Occupied", "Maintenance"].index(r["status"]), key=f"s_{r['id']}")
                            edit_amenities = st.text_input("Amenities", value=r.get("amenities", ""), key=f"a_{r['id']}")
                            
                            c_up, c_del = st.columns(2)
                            with c_up:
                                if st.button("Save Changes", key=f"btn_up_{r['id']}", use_container_width=True):
                                    ok, msg = db.update_room(r["id"], r["number"], r["type"], edit_price, edit_status, edit_amenities)
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            with c_del:
                                if st.button("Delete Room", key=f"btn_del_{r['id']}", type="secondary", use_container_width=True):
                                    ok, msg = db.delete_room(r["id"])
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                        
        if not filtered_rooms:
            st.info("No rooms match your filter criteria.")

    with tab_add_room:
        st.subheader("Add Room to Inventory")
        st.caption("Expand your property by registering new room suites.")
        
        with st.form("add_room_form"):
            ar_col1, ar_col2 = st.columns(2)
            with ar_col1:
                new_number = st.text_input("Room Number", placeholder="e.g. 501").strip()
                new_type = st.selectbox("Room Category", ["Single", "Double", "Deluxe", "Suite"])
            with ar_col2:
                new_price = st.number_input("Price per Night (₹)", min_value=500.0, value=2500.0, step=100.0)
                new_status = st.selectbox("Initial Status", ["Available", "Occupied", "Maintenance"])
                
            new_amenities = st.text_input("Amenities", value="Wi-Fi, AC, Smart TV, Mini Bar, Balcony")
            add_submitted = st.form_submit_button("➕ Save Room to Inventory", type="primary", use_container_width=True)
            
            if add_submitted:
                if not new_number:
                    st.error("Please provide a room number.")
                else:
                    ok, msg = db.add_room(new_number, new_type, new_price, new_status, new_amenities)
                    if ok:
                        st.success(f"Room {new_number} added successfully!")
                        st.rerun()
                    else:
                        st.error(msg)


# =============================================================
# PAGE 3: RESERVATIONS & BOOKINGS
# =============================================================
elif menu == "📅 Reservations & Bookings":
    st.title("Reservation & Booking Management")
    st.caption("Record guest reservations, prevent double-bookings with date conflict detection, and track payment status.")
    
    tab_res_list, tab_new_res = st.tabs(["📋 All Reservations", "➕ Create New Booking"])
    
    with tab_new_res:
        st.subheader("New Guest Reservation")
        
        # Filter available rooms for booking
        bookable_rooms = [r for r in rooms if r["status"] != "Maintenance"]
        
        if not bookable_rooms:
            st.warning("No bookable rooms available. Please add rooms or resolve maintenance status first.")
        else:
            with st.form("new_booking_form"):
                b_c1, b_c2 = st.columns(2)
                with b_c1:
                    guest_name = st.text_input("Guest Full Name", placeholder="e.g. Rahul Verma").strip()
                    guest_email = st.text_input("Guest Email", placeholder="rahul@example.com").strip().lower()
                    guest_phone = st.text_input("Contact Phone", placeholder="+91 98765 00000").strip()
                    num_guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=2)
                    
                with b_c2:
                    room_options = {r["id"]: f"Room {r['number']} — {r['type']} ({format_currency(r['price'])}/night)" for r in bookable_rooms}
                    selected_room_id = st.selectbox("Select Room", options=list(room_options.keys()), format_func=lambda x: room_options[x])
                    
                    today = datetime.date.today()
                    d1, d2 = st.columns(2)
                    with d1:
                        check_in = st.date_input("Check-in Date", min_value=today, value=today)
                    with d2:
                        check_out = st.date_input("Check-out Date", min_value=check_in + datetime.timedelta(days=1), value=check_in + datetime.timedelta(days=2))
                        
                    init_payment = st.selectbox("Payment Status", ["Pending", "Paid"])
                    
                booking_notes = st.text_area("Special Requests / Notes", placeholder="e.g. Early check-in requested, vegetarian breakfast, quiet room...")
                
                # Dynamic cost calculation preview
                if check_out > check_in:
                    nights = (check_out - check_in).days
                    sel_room = next((r for r in rooms if r["id"] == selected_room_id), None)
                    price_night = sel_room["price"] if sel_room else 0
                    estimated_total = nights * price_night
                    st.info(f"Stay duration: **{nights} night(s)** | Estimated Total: **{format_currency(estimated_total)}**")
                
                create_res_btn = st.form_submit_button("Confirm & Create Reservation ➜", type="primary", use_container_width=True)
                
                if create_res_btn:
                    if not guest_name or not guest_email:
                        st.error("Please enter guest name and email address.")
                    elif check_out <= check_in:
                        st.error("Check-out date must be after check-in date.")
                    else:
                        ok, msg = db.create_reservation(
                            guest_name, guest_email, guest_phone, selected_room_id,
                            check_in, check_out, num_guests, init_payment, booking_notes
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                            
    with tab_res_list:
        # Search & Filter
        r_f1, r_f2, r_f3 = st.columns([2, 1, 1])
        with r_f1:
            res_search = st.text_input("🔍 Search reservations (by guest, email, room)", "")
        with r_f2:
            status_filter = st.selectbox("Filter Status", ["All Statuses", "Confirmed", "Checked-in", "Checked-out", "Cancelled"])
        with r_f3:
            pay_filter = st.selectbox("Filter Payment", ["All Payments", "Paid", "Pending"])
            
        filtered_res = reservations
        if res_search:
            filtered_res = [
                r for r in filtered_res
                if res_search.lower() in r["guest_name"].lower() or 
                   res_search.lower() in r["guest_email"].lower() or 
                   res_search.lower() in str(r.get("room_number", "")).lower()
            ]
        if status_filter != "All Statuses":
            filtered_res = [r for r in filtered_res if r["status"] == status_filter]
        if pay_filter != "All Payments":
            filtered_res = [r for r in filtered_res if r["payment_status"] == pay_filter]
            
        st.markdown(f"**Showing {len(filtered_res)} of {len(reservations)} reservations**")
        
        if not filtered_res:
            st.info("No reservations match your filters.")
        else:
            for r in filtered_res:
                with st.container(border=True):
                    head_col1, head_col2, head_col3 = st.columns([2, 2, 2])
                    
                    with head_col1:
                        st.markdown(f"### {r['guest_name']}")
                        st.caption(f"📧 {r['guest_email']}  |  📞 {r.get('guest_phone') or 'Not provided'}")
                        if r.get("notes"):
                            st.markdown(f"<small style='color: #6C757D;'>📝 {r['notes']}</small>", unsafe_allow_html=True)
                            
                    with head_col2:
                        st.markdown(f"**Room {r['room_number']}** ({r['room_type']})")
                        st.write(f"📅 {format_date(r['check_in'])} → {format_date(r['check_out'])}")
                        st.markdown(f"**Total:** <span style='color: #0F5132; font-size: 1.1rem; font-weight: 700;'>{format_currency(r['total_amount'])}</span> ({r['guests']} Guest{'s' if r['guests']>1 else ''})", unsafe_allow_html=True)
                        
                    with head_col3:
                        status_badge = f"badge-{r['status'].lower().replace(' ', '-')}"
                        pay_badge = f"badge-{r['payment_status'].lower()}"
                        st.markdown(f"""
                        <div style="margin-bottom: 8px;">
                            Status: <span class="{status_badge}">{r['status']}</span><br>
                            Payment: <span class="{pay_badge}">{r['payment_status']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Interactive Status & Payment Controls
                        st_col, pay_col, cancel_col = st.columns([1, 1, 1])
                        with st_col:
                            new_st = st.selectbox(
                                "Update Status",
                                ["Confirmed", "Checked-in", "Checked-out", "Cancelled"],
                                index=["Confirmed", "Checked-in", "Checked-out", "Cancelled"].index(r["status"]),
                                key=f"res_st_{r['id']}",
                                label_visibility="collapsed"
                            )
                            if new_st != r["status"]:
                                db.update_reservation_status(r["id"], new_st)
                                st.rerun()
                                
                        with pay_col:
                            toggle_pay = "Mark Pending" if r["payment_status"] == "Paid" else "Mark Paid"
                            if st.button(toggle_pay, key=f"btn_pay_{r['id']}", use_container_width=True):
                                new_p = "Pending" if r["payment_status"] == "Paid" else "Paid"
                                db.update_reservation_payment(r["id"], new_p)
                                st.rerun()
                                
                        with cancel_col:
                            if r["status"] not in ("Cancelled", "Checked-out"):
                                if st.button("Cancel", key=f"btn_cnc_{r['id']}", type="secondary", use_container_width=True):
                                    db.cancel_reservation(r["id"])
                                    st.rerun()


# =============================================================
# PAGE 4: GUEST DIRECTORY & PROFILES
# =============================================================
elif menu == "👥 Guest Directory":
    st.title("Guest Directory & Profiles")
    st.caption("Comprehensive directory of all guests who have stayed or made bookings at HotelPro.")
    
    g_search = st.text_input("🔍 Search guest directory by name, email, or phone", "")
    
    filtered_guests = guest_summary
    if g_search:
        filtered_guests = [
            g for g in filtered_guests
            if g_search.lower() in g["guest_name"].lower() or 
               g_search.lower() in g["guest_email"].lower() or 
               g_search.lower() in (g.get("guest_phone") or "").lower()
        ]
        
    st.markdown(f"**Showing {len(filtered_guests)} registered guest profiles**")
    
    if filtered_guests:
        # Table view
        g_df = pd.DataFrame([{
            "Guest Name": g["guest_name"],
            "Email": g["guest_email"],
            "Phone": g["guest_phone"] or "—",
            "Total Bookings": g["total_bookings"],
            "Lifetime Spend": format_currency(g["total_spent"]),
            "Outstanding": format_currency(g["outstanding_balance"]),
            "Latest Check-in": format_date(g["latest_check_in"])
        } for g in filtered_guests])
        st.dataframe(g_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("Guest History Explorer")
        
        selected_guest_email = st.selectbox(
            "Select a guest to inspect complete booking history",
            options=[g["guest_email"] for g in filtered_guests],
            format_func=lambda email: f"{next(g['guest_name'] for g in filtered_guests if g['guest_email'] == email)} ({email})"
        )
        
        if selected_guest_email:
            guest_bookings = [r for r in reservations if r["guest_email"] == selected_guest_email]
            st.write(f"Found **{len(guest_bookings)}** booking(s) for `{selected_guest_email}`:")
            
            for b in guest_bookings:
                with st.container(border=True):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"**Room {b['room_number']}** ({b['room_type']})")
                        st.caption(f"Booking ID: #{b['id']}")
                    with c2:
                        st.write(f"📅 {format_date(b['check_in'])} → {format_date(b['check_out'])}")
                        st.write(f"Guests: {b['guests']}")
                    with c3:
                        st.markdown(f"**{format_currency(b['total_amount'])}**  |  {b['status']}  |  {b['payment_status']}")
    else:
        st.info("No guests found in the directory.")


# =============================================================
# PAGE 5: BILLING & INVOICES
# =============================================================
elif menu == "🧾 Billing & Invoices":
    st.title("Billing & Invoice Generator")
    st.caption("Generate official itemized billing invoices for guests with tax and payment status details.")
    
    if not reservations:
        st.info("No reservations available to generate invoices.")
    else:
        res_map = {r["id"]: f"Booking #{r['id']} — {r['guest_name']} (Room {r['room_number']}, {format_date(r['check_in'])})" for r in reservations}
        selected_inv_id = st.selectbox("Select Reservation to Generate Invoice", options=list(res_map.keys()), format_func=lambda x: res_map[x])
        
        inv_res = next((r for r in reservations if r["id"] == selected_inv_id), None)
        
        if inv_res:
            d_in = datetime.date.fromisoformat(str(inv_res["check_in"]))
            d_out = datetime.date.fromisoformat(str(inv_res["check_out"]))
            nights = max((d_out - d_in).days, 1)
            room_rate = inv_res["room_price"]
            subtotal = nights * room_rate
            tax_rate = 0.12  # 12% GST
            tax_amount = round(subtotal * tax_rate, 2)
            grand_total = subtotal + tax_amount
            
            # Invoice Card Render
            st.markdown(f"""
            <div class="invoice-container">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #E9ECEF; padding-bottom: 15px; margin-bottom: 20px;">
                    <div>
                        <h2 style="color: #0F5132; margin: 0;">🏨 HotelPro Luxury Suites</h2>
                        <div style="color: #6C757D; font-size: 0.85rem; margin-top: 4px;">
                            100 Grand Boulevard, Hospitality Enclave<br>
                            support@hotelpro.com | +91 800-HOTELPRO
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <h3 style="margin: 0; color: #1A202C;">INVOICE</h3>
                        <div style="color: #6C757D; font-size: 0.9rem;">#INV-2026-{inv_res['id']:04d}</div>
                        <div style="font-size: 0.85rem; color: #6C757D;">Date: {datetime.date.today().strftime('%d %b %Y')}</div>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 25px;">
                    <div>
                        <strong style="color: #6C757D; font-size: 0.8rem; text-transform: uppercase;">Billed To:</strong>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #1A202C; margin-top: 2px;">{inv_res['guest_name']}</div>
                        <div style="font-size: 0.9rem; color: #495057;">{inv_res['guest_email']}</div>
                        <div style="font-size: 0.9rem; color: #495057;">{inv_res.get('guest_phone') or ''}</div>
                    </div>
                    <div style="text-align: right;">
                        <strong style="color: #6C757D; font-size: 0.8rem; text-transform: uppercase;">Stay Summary:</strong>
                        <div style="font-size: 0.9rem; color: #1A202C; margin-top: 2px;">Room: <strong>{inv_res['room_number']} ({inv_res['room_type']})</strong></div>
                        <div style="font-size: 0.9rem; color: #495057;">Check-in: {format_date(inv_res['check_in'])}</div>
                        <div style="font-size: 0.9rem; color: #495057;">Check-out: {format_date(inv_res['check_out'])}</div>
                    </div>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background: #F8F9FA; border-bottom: 2px solid #DEE2E6; text-align: left;">
                            <th style="padding: 10px; font-size: 0.85rem;">ITEM DESCRIPTION</th>
                            <th style="padding: 10px; text-align: center; font-size: 0.85rem;">NIGHTS</th>
                            <th style="padding: 10px; text-align: right; font-size: 0.85rem;">RATE / NIGHT</th>
                            <th style="padding: 10px; text-align: right; font-size: 0.85rem;">AMOUNT</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid #E9ECEF;">
                            <td style="padding: 12px 10px;">
                                <strong>Room Accommodation ({inv_res['room_type']})</strong><br>
                                <small style="color: #6C757D;">Guests: {inv_res['guests']} | Room No: {inv_res['room_number']}</small>
                            </td>
                            <td style="padding: 12px 10px; text-align: center;">{nights}</td>
                            <td style="padding: 12px 10px; text-align: right;">{format_currency(room_rate)}</td>
                            <td style="padding: 12px 10px; text-align: right;">{format_currency(subtotal)}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="display: flex; justify-content: flex-end;">
                    <div style="width: 280px;">
                        <div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 0.9rem;">
                            <span>Subtotal:</span>
                            <strong>{format_currency(subtotal)}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 0.9rem;">
                            <span>GST / Tax (12%):</span>
                            <strong>{format_currency(tax_amount)}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-top: 2px solid #1A202C; margin-top: 6px; font-size: 1.15rem; font-weight: 700; color: #0F5132;">
                            <span>Grand Total:</span>
                            <span>{format_currency(grand_total)}</span>
                        </div>
                        <div style="text-align: right; margin-top: 10px;">
                            Payment Status: <span class="badge-{'paid' if inv_res['payment_status'] == 'Paid' else 'pending'}">{inv_res['payment_status'].upper()}</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 30px; padding-top: 15px; border-top: 1px dashed #DEE2E6; text-align: center; font-size: 0.82rem; color: #6C757D;">
                    Thank you for choosing HotelPro! We hope you enjoyed your stay.<br>
                    This is an electronically generated receipt and does not require a physical signature.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Download options
            invoice_text = f"""====================================================
HOTELPRO LUXURY SUITES — OFFICIAL INVOICE
Invoice #: INV-2026-{inv_res['id']:04d}
Date: {datetime.date.today().strftime('%d %b %Y')}
====================================================
Billed to:
Name:  {inv_res['guest_name']}
Email: {inv_res['guest_email']}
Phone: {inv_res.get('guest_phone') or 'N/A'}

Stay Details:
Room:      Room {inv_res['room_number']} ({inv_res['room_type']})
Check-in:  {format_date(inv_res['check_in'])}
Check-out: {format_date(inv_res['check_out'])}
Nights:    {nights}
Guests:    {inv_res['guests']}

Charges:
Room Rate:     {format_currency(room_rate)} / night
Subtotal:      {format_currency(subtotal)}
GST / Tax 12%: {format_currency(tax_amount)}
----------------------------------------------------
TOTAL AMOUNT:  {format_currency(grand_total)}
PAYMENT:       {inv_res['payment_status'].upper()}
====================================================
Thank you for staying with HotelPro!
"""
            st.download_button(
                "📥 Download Invoice as Text File",
                data=invoice_text,
                file_name=f"HotelPro_Invoice_{inv_res['id']}_{inv_res['guest_name'].replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )


# =============================================================
# PAGE 6: DEPLOYMENT & SETTINGS
# =============================================================
elif menu == "⚙️ Deployment & Settings":
    st.title("System, Deployment & Data Export")
    st.caption("Manage configurations, export reports to CSV, and deploy easily to Streamlit Community Cloud.")
    
    tab_deploy, tab_export, tab_mern = st.tabs(["🚀 Deploy to Streamlit Cloud", "📥 Data Export (CSV)", "💻 Full MERN Stack Run"])
    
    with tab_deploy:
        st.subheader("Streamlit Community Cloud Deployment Guide")
        st.markdown("""
        Deploying HotelPro on **Streamlit Community Cloud** (share.streamlit.io) gives you a live, free public web application URL in 2 minutes:
        
        #### Step-by-Step Instructions:
        1. **Push your code to GitHub**:
           ```bash
           git init
           git add .
           git commit -m "Deploy HotelPro on Streamlit"
           git branch -M main
           git remote add origin https://github.com/<your-username>/hotelpro.git
           git push -u origin main
           ```
        2. **Log in to Streamlit Community Cloud**:
           - Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
        3. **Deploy New App**:
           - Click **New app**.
           - Select your repository: `<your-username>/hotelpro`.
           - Branch: `main`.
           - Main file path: `app.py` (or `streamlit_app.py`).
        4. **Click Deploy**:
           - Streamlit Cloud automatically reads `requirements.txt`, installs packages, initializes the database, and gives you a shareable link!
        """)
        
        st.info("💡 **Tip**: SQLite database (`hotelpro.db`) works out of the box with zero external configuration required!")

    with tab_export:
        st.subheader("Export System Data to CSV")
        st.caption("Download offline records of your hotel operations for bookkeeping and reporting.")
        
        e1, e2, e3 = st.columns(3)
        with e1:
            if rooms:
                rooms_df = pd.DataFrame(rooms)
                st.download_button(
                    "📥 Export Rooms CSV",
                    data=rooms_df.to_csv(index=False),
                    file_name="hotelpro_rooms.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with e2:
            if reservations:
                res_df = pd.DataFrame(reservations)
                st.download_button(
                    "📥 Export Reservations CSV",
                    data=res_df.to_csv(index=False),
                    file_name="hotelpro_reservations.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with e3:
            if guest_summary:
                guests_df = pd.DataFrame(guest_summary)
                st.download_button(
                    "📥 Export Guests Directory CSV",
                    data=guests_df.to_csv(index=False),
                    file_name="hotelpro_guests.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with tab_mern:
        st.subheader("MERN Stack Local Run Instructions")
        st.markdown("""
        All dependencies for the **MERN (MongoDB, Express, React, Node.js)** stack have been pre-installed and verified!
        
        To run the dual React + Express development servers:
        1. Open your terminal in the `HotelPro` folder:
           ```bash
           cd HotelPro
           ```
        2. Ensure MongoDB Community Server is running locally (or provide your MongoDB Atlas URI in `server/.env`).
        3. Launch both backend and frontend:
           ```bash
           npm run dev
           ```
        4. Open:
           - Frontend: [http://localhost:5173](http://localhost:5173)
           - Backend API: [http://localhost:5000/api/health](http://localhost:5000/api/health)
        """)
