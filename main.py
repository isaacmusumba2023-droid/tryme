import streamlit as st
from datetime import datetime, date
import pandas as pd
from supabase import create_client, Client
from streamlit_option_menu import option_menu
import plotly.express as px
import os

#system variable
USERS_LIST=['WORKSHOP','ESP-KOC','PDI','BURGUN YARD','ABDALY FARM','DESALTER PROJECT','FIELD OP.REPAIR','JO-ESP',
            'MISHRIF','MOBILE','NEW GENERATOR','OFF-HIRE','READY','WSH-POWER']
FIELD_LIST=["NORTH","WORKSHOP","SEK","EK","PDI", "WAFRA", "WEST","MISHRIF"]
MODEL_LIST=["3406", "3412", "C13", "C15", "C18", "C3.3", "CUMMINS", "TAD-1342GE", "TAD-1343GE", "TAD-1344GE", "TAD-1641GE", "TAD-532GE",
           "TAD-734GE", "TAD-840GE", "TWD-1643GE", "TWD-1645GE"]
TYPE_LIST=["CAT", "VOLVO", "CUMMINS", "BAUDOUIN"]
Area_LIST=["SK", "EK", "RA","NK"]
CONTRACT_OPTIONS=['--select--','70006301','70005701']
TRANSFER_STATUS=['DISPATCH','RECEIVE','INTERNAL-SHIFT']

# --- DB CLIENT UTILITY INITIALIZATION ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(URL, KEY)

supabase = get_supabase_client()

# Date constants
max_date = datetime.today().date()
min_date = date(1990, 1, 1)
TABLE_NAME = "GENSET ASSET"

# --- DELETING MAPPED LOCATIONS UTILITY ---
def delete_location_mapping(mapping_id):
    try:
        supabase.table("LOCATION_MAPPING").delete().eq("id", mapping_id).execute()
        st.cache_data.clear()
        return True, "✅ Mapping deleted successfully!"
    except Exception as e:
        if "violates foreign key constraint" in str(e).lower():
            return False, "❌ Cannot delete: Active assets are currently assigned to this route configuration. Reassign those assets first."
        return False, f"❌ Deletion failed: {str(e)}"

# --- PAGE CONFIGURATION & CUSTOM STYLING ---
st.set_page_config(
    page_title="GENSET ASSET",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        header {
            visibility: hidden;
            height: 0px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SYSTEM CACHED DATA FETCHERS ---
@st.cache_data(ttl=300)
def get_location_mappings():
    try:
        response = supabase.table("LOCATION_MAPPING").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_full_dataframe_with_realations():
    try:
        response = supabase.table("GENSET ASSET").select("""
            *,
            LOCATION_MAPPING (
                CONTRACT_NO,
                FIELD,
                AREA,
                LOCATION
            )
        """).execute()

        flat_data = []
        for row in response.data:
            mapping = row.get("LOCATION_MAPPING") or {}
            row["CONTRACT_NO"] = mapping.get("CONTRACT_NO", "N/A")
            row["FIELD"] = mapping.get("FIELD", "N/A")
            row["AREA"] = mapping.get("AREA", "N/A")
            row["LOCATION"] = mapping.get("LOCATION", "N/A")
            flat_data.append(row)

        return pd.DataFrame(flat_data)
    except Exception as e:
        st.error(f"Error fetching unified data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_full_dataframe_with_realations():
    try:
        response = supabase.table("GENSET ASSET").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error("📡 **Network Connection Error**")
        st.warning("FODAMS cannot reach the database. Please check your internet connection or VPN.")
        return pd.DataFrame()

# --- SECURITY APP STATE TRACKERS ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_role" not in st.session_state:
    st.session_state.user_role = ["Guest",'developer']

# --- GATEWAY AUTHENTICATION SHIELD ---
# --- GATEWAY AUTHENTICATION SHIELD ---
if not st.session_state.get('authenticated', False):
    st.title("🔒 FODAMS Internal Gate")
    st.caption("Please sign in with your corporate credentials to access the digital supervisory system.")

    with st.form("login_form", clear_on_submit=False):
        email_input = st.text_input("Corporate Email Address")
        password_input = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Authenticate Access")

        if submit_btn:
            if email_input and password_input:
                try:
                    # 1. Sign in the user first so Supabase issues a secure session token
                    auth_response = supabase.auth.sign_in_with_password({
                        "email": email_input,
                        "password": password_input
                    })

                    target_uid = auth_response.user.id

                    # 2. NOW query the profile table (RLS will now allow this because the user is authenticated!)
                    profile_query = supabase.table("PROFILES").select("role").eq("id", target_uid).execute()

                    if profile_query.data and len(profile_query.data) > 0:
                        raw_role = profile_query.data[0].get("role", "Guest")
                        assigned_role = raw_role.title() if raw_role else "Guest"
                    else:
                        assigned_role = "Guest"

                    # 3. Save parameters safely to your session states
                    st.session_state.authenticated = True
                    st.session_state.user_email = email_input
                    st.session_state.user_role = assigned_role

                    st.success(f"Welcome back! Authenticated as {assigned_role}")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Authentication Failed: {e}")
            else:
                st.warning("Please fill in both email and password fields.")

    # Stop execution here if not logged in yet
    st.stop()
# --- DYNAMIC NAVIGATION MENU MENU BUILDER ---
all_menu_options = {
    "GENERAL ASSETS": {"icon": "diagram-3-fill",
                       "roles": ["Developer", "Manager", "Mechanical", "Supervisor", "Admin", "Engineer"]},
    "ASSET_MANAGEMENT": {"icon": "boxes",
                         "roles": ["Developer", "Manager", "Supervisor", "Admin", "Mechanical", "Engineer"]},
    "WORKSHOP": {"icon": "tools", "roles": ["Developer", "Manager", "Mechanical", "Admin", "Supervisor"]},
    "MAINTENANCE": {"icon": "speedometer2",
                    "roles": ["Developer", "Manager", "Supervisor", "Admin", "Mechanical", "Engineer"]},
    "PARTS AND PRODUCTS": {"icon": "gear-wide-connected",
                           "roles": ["Developer", "Manager", "Supervisor", "Mechanical", "Admin"]},
    "FIXED ASSETS": {"icon": "arrow-90deg-right",
                     "roles": ["Developer", "Manager", "Supervisor", "Mechanical", "Engineer"]},
    "FLEET MANAGEMENT": {"icon": "car-front",
                         "roles": ["Developer", "Manager", "Supervisor", "Mechanical", "Engineer"]},
    "LOCATION_MAPPING": {"icon": "sliders", "roles": ["Developer", "Manager", "Supervisor", "Mechanical"]},
}

user_role = st.session_state.get('user_role', 'Guest')

# Filter allowed selections
allowed_options = [opt for opt, data in all_menu_options.items() if user_role in data["roles"]]
allowed_icons = [all_menu_options[opt]["icon"] for opt in allowed_options]

# Safe-guard: If the user role matches absolutely nothing, provide a default layout view
if not allowed_options:
    allowed_options = ["ACCESS RESTRICTED"]
    allowed_icons = ["exclamation-triangle-fill"]

# --- SIDEBAR INTERACTION MATRIX ---
with st.sidebar:
    st.markdown(f"### 🛡️ Secure Session")
    st.caption(f"User: *{st.session_state.user_email}*")
    st.caption(f"Role: *{user_role.upper()}*")
    try:
        st.image('img.png', width=80)
    except:
        pass

    selected = option_menu(
        menu_title="FIELD_OP",
        options=allowed_options,
        icons=allowed_icons,
        menu_icon="person-gear",
        default_index=0,
        styles={
            "container": {"background-color": "#cceeff"},
            "nav-link": {"font-size": "11px", "text-align": "left", "color": "#000000"},
            "nav-link-selected": {"background-color": "#b3d9ff"},
        }
    )

    st.divider()
    if st.button("REFRESH PAGE", use_container_width=True):
        st.rerun()

    if st.button("Log Out 🚪", type="primary", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except:
            pass
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_role = "Guest"
        st.rerun()

# --- RENDERING ENGINE HANDLER ---
if selected == "ACCESS RESTRICTED":
    st.error("⚠️ Your user profile has not been assigned operational permissions yet.")
    st.warning(
        "Please contact your database Administrator to configure your organizational title in the backend 'PROFILES' registry table.")
    st.stop()


#-----program line in----(source code)
if selected == "GENERAL ASSETS":
    st.info(f"****WELCOME TO FIELD_OPERATIONS INTERNAL DIGITAL SUPERVISORLY & MONITORING SYSTEM****")

    # 1. Fetching Data with Safe Defaults
    try:
        df = get_full_dataframe_with_realations()
        V_greater = supabase.table("GENSET ASSET").select("*").gte("KVA", 200).execute()
        V_KVA1 = len(V_greater.data) if hasattr(V_greater, 'data') else 0
    except Exception as e:
        st.error(f"⚠️ Database connection failed: {e}")
        df = pd.DataFrame()  # Fallback to an empty DataFrame so the UI elements don't crash
        V_KVA1 = 0

    # 2. Base Counts
    V_TOTAL = len(df)
    V_B2 = max(0, V_TOTAL - V_KVA1)

    # 3. Safe Extraction of Column Names
    # This prevents KeyErrors across ALL metrics simultaneously
    has_user = 'USER' in df.columns and not df.empty
    has_location = 'LOCATION' in df.columns and not df.empty

    # 4. Metric Calculations (Defaults to 0 if column is missing or empty)
    V_WORKSHOP = len(df[df['LOCATION'] == "WORKSHOP"]) if has_location else 0
    V_USER1 = len(df[df['USER'] == "ESP-KOC"]) if has_user else 0
    V_USER10 = len(df[df['USER'] == "READY"]) if has_user else 0
    V_USER2 = len(df[df['USER'] == "JO-ESP"]) if has_user else 0
    V_USER3 = len(df[df['USER'] == "BURGUN YARD"]) if has_user else 0  # Double check if this should be 'BURGAN'
    V_USER11 = len(df[df['USER'] == "WSH-POWER"]) if has_user else 0
    V_USER5 = len(df[df['USER'] == "MOBILE"]) if has_user else 0
    V_USER4 = len(df[df['LOCATION'] == "PDI"]) if has_location else 0  # Fixed column context logic
    V_USER12 = len(df[df['USER'] == "NEW GENERATOR"]) if has_user else 0
    V_USER6 = len(df[df['USER'] == "OFF-HIRE"]) if has_user else 0
    V_USER7 = len(df[df['USER'] == "MISHRIF"]) if has_user else 0
    V_USER13 = len(df[df['USER'] == "DESALTER PROJECT"]) if has_user else 0
    V_USER8 = len(df[df['USER'] == "FIELD OP.REPAIR"]) if has_user else 0
    V_USER9 = len(df[df['USER'] == "ABDALY FARM"]) if has_user else 0

    # 5. UI Layout Display
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("TOTAL ASSETS", value=V_TOTAL, delta_color="blue", border=True, height=120, delta="+")
        st.metric("WORKSHOP", value=V_WORKSHOP, delta_color="blue", border=True, height=120, delta="+")
        st.metric("ESP-KOC", value=V_USER1, delta_color="blue", border=True, height=120, delta="+")
        st.metric("READY", value=V_USER10, delta_color="blue", border=True, height=120, delta="+")

    with col2:
        st.metric("JO-ESP", value=V_USER2, delta_color="blue", border=True, height=120, delta="+")
        st.metric("BURGUN YARD", value=V_USER3, delta_color="blue", border=True, height=120, delta="+")
        st.metric("WSH-POWER", value=V_USER11, delta_color="blue", border=True, height=120, delta="+")
        st.metric("KVA<200", value=V_B2, delta_color="blue", border=True, height=120, delta="+")

    with col3:
        st.metric("PDI", value=V_USER4, delta_color="blue", border=True, height=120, delta="+")
        st.metric("MOBILE", value=V_USER5, delta_color="blue", border=True, height=120, delta="+")
        st.metric("NEW-GENERATOR", value=V_USER12, delta_color="blue", border=True, height=120, delta="+")

    with col4:
        st.metric("OFF-HIRE", value=V_USER6, delta_color="blue", border=True, height=120, delta="+")
        st.metric("MISHRIF", value=V_USER7, delta_color="blue", border=True, height=120, delta="+")
        st.metric("DESALTER-PROJECT", value=V_USER13, delta_color="blue", border=True, height=120, delta="+")

    with col5:
        st.metric("FIELD OP.REPAIR", value=V_USER8, delta_color="blue", border=True, height=120, delta="+")
        st.metric("ABDALY FARM", value=V_USER9, delta_color="blue", border=True, height=120, delta="+")
        st.metric("KVA=>200", value=V_KVA1, delta_color="blue", border=True, height=120, delta="+")
    "---"
    st.caption("REPORTS")
    col1,col2,col3=st.columns(3)
    with col1:
        with st.expander("READY GENERATORS"):
            df=supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,KVA,LOCATION").eq("USER","READY").execute()
            df_2=df.data
            st.dataframe(df_2)
    with col2:
        with st.expander("UNDER WORKSHOP"):
            df = supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,KVA,LOCATION").eq("LOCATION",
                                                                                                 "WORKSHOP").execute()
            df_2 = df.data
            st.dataframe(df_2)
    with col3:
        with st.expander("UNDER PDI"):
            df = supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,KVA,LOCATION").eq("LOCATION",
                                                                                                 "PDI").execute()
            df_2 = df.data
            st.dataframe(df_2)
    st.caption("DATA_VISUALIZATION")
    with st.expander("CLICK HERE"):
        # Simple native replacement for your matplotlib block:
        chart_data = pd.DataFrame({
            'Location': ['WORKSHOP', 'ESP-KOC', 'PDI', 'JO-ESP', 'BURGAN YARD'],
            'Quantity': [V_WORKSHOP, V_USER1, V_USER4, V_USER2, V_USER3]
        })
        st.bar_chart(chart_data, x='Location', y='Quantity', color="#1a8cff")

elif selected == "ASSET_MANAGEMENT":
    st.info("**Welcome to asset_management(update,add_asset,filter)**")
    #-----write code here for asset management----
    tab1, tab2, tab3, tab4 ,tab5= st.tabs(["View Assets", "Filter & Download", "Add New Asset", "Update Asset","Audit logs"])

    df=get_full_dataframe_with_realations()
    with tab1:
        st.subheader("Current Assets")
        try:
            df=get_full_dataframe_with_realations()
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True, height=600)
                st.info(f"Total Assets: {len(df)}")
            else:
                st.warning("No Assets Available")
        except Exception as e:
            st.error(f"error fetching data {e}")

    with tab2:
        st.subheader("Filter & Download")
        try:
            df=get_full_dataframe_with_realations()
            if not df.empty:
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    loctions=sorted([str(u) for u in df["LOCATION"].unique() if u is not None])
                    selected_location=st.multiselect("Select Location", options=loctions)
                with col_f2:
                    kvas=sorted([int(u) for u in df["KVA"].unique() if u is not None])
                    selected_kvas=st.multiselect("Select KVA", options=kvas)
                with col_f3:
                    users=sorted([str(u) for u in df["USER"].unique() if u is not None])
                    selected_users=st.multiselect("Select User", options=users)
                filtered_df=df.copy()
                if selected_location:
                    filtered_df=filtered_df[filtered_df["LOCATION"].astype(str).isin(selected_location)]
                if selected_kvas:
                    filtered_df=filtered_df[filtered_df["KVA"].astype(int).isin(selected_kvas)]
                if selected_users:
                    filtered_df=filtered_df[filtered_df["USER"].astype(str).isin(selected_users)]
                st.write("filtered results")
                st.dataframe(filtered_df, use_container_width=True, height=300)
                st.info(f"Showing {len(filtered_df)} of {len(df)} total assets.")
                if not filtered_df.empty:
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Filtered Data as CSV",
                        data=csv,
                        file_name='genset_assets_filtered.csv',
                        mime='text/csv',
                    )
            else:
                st.warning("No assets found in the database.")
        except Exception as e:
            st.error(f"error fetching data {e}")
    with tab3:
        if user_role in ['Developer', 'Manager', 'Supervisor', 'Engineer', 'Mechanical']:
            st.write("ADD NEW ASSETS:")
            map_df = get_location_mappings()

            if not map_df.empty:
                st.caption("🗺️ Route Selection Path (Updates dynamically: FIELD ➔ AREA ➔ LOCATION ➔ CONTACT_NO)")

                # --- DYNAMIC ROUTING DROP-DOWNS (PLACED OUTSIDE THE FORM) ---
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)

                with col_m1:
                    field_options = sorted([str(x) for x in map_df["FIELD"].dropna().unique()])
                    field_val = st.selectbox("1. Select Field", options=field_options)
                    filtered_by_field = map_df[map_df["FIELD"] == field_val]

                with col_m2:
                    # Defensive guard check for valid column name case in dataframe dictionary mapping
                    area_col = "AREA" if "AREA" in filtered_by_field.columns else "area"
                    area_options = sorted([str(x) for x in filtered_by_field[
                        area_col].dropna().unique()]) if area_col in filtered_by_field.columns else []
                    area_val = st.selectbox("2. Select Area", options=area_options)
                    filtered_by_area = filtered_by_field[
                        filtered_by_field[area_col] == area_val] if area_options else filtered_by_field

                with col_m3:
                    location_options = sorted([str(x) for x in filtered_by_area["LOCATION"].dropna().unique()])
                    location_val = st.selectbox("3. Select Location", options=location_options)
                    filtered_by_location = filtered_by_area[filtered_by_area["LOCATION"] == location_val]

                with col_m4:
                    contract_options = sorted([str(x) for x in filtered_by_location["CONTRACT_NO"].dropna().unique()])
                    contract_val = st.selectbox("4. Select Contract No", options=contract_options)

                # --- FORM INITIALIZATION FOR STATIC METRICS ---
                with st.form("add_new_asset", clear_on_submit=True):
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        g_code = st.text_input("G-CODE")
                        serial_no = st.text_input("SERIAL_NO")
                        model = st.selectbox("MODEL", options=MODEL_LIST)
                        asset_type = st.selectbox("TYPE", options=TYPE_LIST)

                    with col2:
                        kva = st.number_input("KVA", min_value=0, step=1)
                        user_id = st.number_input("user_id:", min_value=0, step=1)
                        manuf_yr = st.date_input("MANUF_YR:", min_value=min_date, max_value=max_date)
                        service_yr_koc = st.date_input("SERVICE_YR_KOC")

                    with col3:
                        run_hrs = st.number_input("RUN_Hrs", min_value=0, step=1)
                        area = st.selectbox("AREA", options=Area_LIST)
                        appr_kva = st.number_input("APPR_KVA", min_value=0, step=1)
                        # 🛑 TRANSFER_STATUS selectbox has been completely removed from here

                    with col4:
                        user = st.selectbox("USER", options=USERS_LIST)
                        crew = st.number_input("CREW", min_value=0, step=1)
                        movement_date = st.date_input("MOVEMENT_DATE", min_value=min_date, max_value=max_date)
                        moved_from = st.text_input("MOVED_FROM")
                        reason = st.text_area("REASON")

                    submit = st.form_submit_button("Add Asset")

                    if submit:
                        # Find the matching backend ID for your chained combo selection
                        matching_rows = map_df[
                            (map_df["FIELD"] == field_val) &
                            (map_df["AREA"] == area_val) &
                            (map_df["LOCATION"] == location_val) &
                            (map_df["CONTRACT_NO"] == contract_val)
                        ]
                        if not matching_rows.empty:
                            chosen_mapping_id = int(matching_rows.iloc[0]["id"])

                            # 🛠️ Clean payload reflecting the pure 4-tier structural mapping update
                            new_data = {
                                "G-CODE": g_code,
                                "SERIAL_NO": serial_no,
                                "MODEL": model,
                                "TYPE": asset_type,
                                "KVA": kva,
                                "user_id": user_id,
                                "location_mapping_id": chosen_mapping_id,
                                "MANUF_YR": str(manuf_yr),
                                "SERVICE_YR_KOC": str(service_yr_koc),
                                "RUN_Hrs": run_hrs,
                                "AREA": area,
                                "APPR_KVA": appr_kva,
                                "USER": user,
                                "CREW": crew,
                                "MOVEMENT_DATE": str(movement_date),
                                "MOVED_FROM": moved_from,
                                "REASON": reason,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                            try:
                                supabase.table(TABLE_NAME).insert(new_data).execute()
                                st.cache_data.clear()
                                st.success("✅ Asset added successfully with relational route parameters mapping!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error adding asset: {e}")
                        else:
                            st.error(
                                "❌ The chosen path is valid in the UI but could not match a row in your backend DB configuration.")
                    else:
                        st.warning("Permission Denied: Authorized roles only.")

    with tab4:
        # ----- PLACE THIS ENTIRE REFACTORED BLOCK DIRECTLY INSIDE TAB 4 -----
        if user_role in ['Developer', 'Manager', 'Supervisor', 'Engineer', 'Mechanical']:
            try:
                df = get_full_dataframe_with_realations()
                if not df.empty:
                    # 1. Get the list of codes for the dropdown selection
                    g_code_options = df["G-CODE"].dropna().tolist()
                    select_gcode = st.selectbox("SELECT G-CODE TO UPDATE:", options=g_code_options)

                    # 2. Extract specific active row data as a baseline dictionary
                    asset_data = df[df["G-CODE"] == select_gcode].iloc[0].to_dict()

                    # --- DYNAMIC ROUTING STEP (KEPT OUTSIDE THE FORM) ---
                    # Fetch master configuration routing database
                    map_df = get_location_mappings()
                    chosen_mapping_id = None

                    # 🛑 Removed u_transfer_status from here
                    u_contract = asset_data.get("CONTRACT_NO", "")
                    u_field = asset_data.get("FIELD", "")
                    u_location = asset_data.get("LOCATION", "")

                    if not map_df.empty:
                        st.caption("🗺️ Route Modification Path (FIELD ➔ AREA ➔ LOCATION ➔ CONTACT_NO)")
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

                        # Extract active column configurations safely for dropdown state defaults
                        current_field = str(asset_data.get("FIELD", ""))
                        current_area = str(asset_data.get("AREA", ""))
                        current_location = str(asset_data.get("LOCATION", ""))
                        current_contract = str(asset_data.get("CONTRACT_NO", ""))

                        with col_m1:
                            field_options = sorted([str(x) for x in map_df["FIELD"].dropna().unique()])
                            field_idx = field_options.index(current_field) if current_field in field_options else 0
                            u_field = st.selectbox("1. FIELD", options=field_options, index=field_idx)
                            filtered_by_field = map_df[map_df["FIELD"] == u_field]

                        with col_m2:
                            area_col = "AREA" if "AREA" in filtered_by_field.columns else "area"
                            area_options = sorted([str(x) for x in filtered_by_field[area_col].dropna().unique()]) if area_col in filtered_by_field.columns else []
                            area_idx = area_options.index(current_area) if current_area in area_options else 0
                            u_area_val = st.selectbox("2. AREA", options=area_options, index=area_idx)
                            filtered_by_area = filtered_by_field[filtered_by_field[area_col] == u_area_val] if area_options else filtered_by_field

                        with col_m3:
                            location_options = sorted([str(x) for x in filtered_by_area["LOCATION"].dropna().unique()])
                            location_idx = location_options.index(current_location) if current_location in location_options else 0
                            u_location = st.selectbox("3. LOCATION", options=location_options, index=location_idx)
                            filtered_by_location = filtered_by_area[filtered_by_area["LOCATION"] == u_location]

                        with col_m4:
                            contract_options = sorted([str(x) for x in filtered_by_location["CONTRACT_NO"].dropna().unique()])
                            contract_idx = contract_options.index(current_contract) if current_contract in contract_options else 0
                            u_contract = st.selectbox("4. CONTRACT_NO", options=contract_options, index=contract_idx)

                        # Pre-calculate matching ID from the dynamic path
                        matching_rows = map_df[
                            (map_df["FIELD"] == u_field) &
                            (map_df["AREA"] == u_area_val) &
                            (map_df["LOCATION"] == u_location) &
                            (map_df["CONTRACT_NO"] == u_contract)
                            ]
                        if not matching_rows.empty:
                            chosen_mapping_id = int(matching_rows.iloc[0]["id"])
                    else:
                        st.error("⚠️ Master mapping rules could not be parsed from database.")

                        # 3. Form Initialization for specifications input
                    with st.form("update_asset_form"):
                        st.caption(f"🔧 UPDATING ASSET SPECIFICATIONS FOR: **{select_gcode}**")

                        # 4. Standard Specifications 4-Column Layout Grid Rows
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            u_serial_no = st.text_input("SERIAL_NO", value=str(asset_data.get("SERIAL_NO", "")))
                            current_model = str(asset_data.get("MODEL", ""))
                            temp_model = MODEL_LIST if current_model in MODEL_LIST else MODEL_LIST + [current_model]
                            u_model = st.selectbox("MODEL", options=temp_model, index=temp_model.index(current_model))

                            current_type = str(asset_data.get("TYPE", ""))
                            temp_type = TYPE_LIST if current_type in TYPE_LIST else TYPE_LIST + [current_type]
                            u_type = st.selectbox("TYPE", options=temp_type, index=temp_type.index(current_type))
                            u_appr_kva = st.number_input("APPR_KVA", value=int(asset_data.get("APPR_KVA", 0)))

                        with col2:
                            def parse_date(date_str):
                                try:
                                    return datetime.strptime(str(date_str), "%Y-%m-%d").date()
                                except:
                                    return datetime.now().date()


                            u_manuf_yr = st.date_input("MANUF_YR", value=parse_date(asset_data.get("MANUF_YR", "")))
                            u_movement_yr = st.date_input("MOVEMENT_DATE",
                                                          value=parse_date(asset_data.get("MOVEMENT_DATE", "")),
                                                          min_value=min_date, max_value=max_date)
                            u_service_yr_koc = st.date_input("SERVICE_YR_KOC",
                                                             value=parse_date(asset_data.get("SERVICE_YR_KOC", "")))
                            u_run_hrs = st.number_input("RUN_Hrs", value=int(asset_data.get("RUN_Hrs", 0)))

                        with col3:
                            u_crew = st.number_input("CREW", value=int(asset_data.get("CREW", 0)))
                            u_moved_from = st.text_input("MOVED_FROM", value=str(asset_data.get("MOVED_FROM", "")))
                            current_user = str(asset_data.get("USER", ""))
                            user_index = USERS_LIST.index(current_user) if current_user in USERS_LIST else 0
                            u_user = st.selectbox("USER", options=USERS_LIST, index=user_index)
                            # 🛑 TRANSFER_STATUS selection box has been permanently removed from here

                        with col4:
                            u_kva = st.number_input("KVA", value=int(asset_data.get("KVA", 0)))
                            u_user_id = st.number_input("user_id", value=int(asset_data.get("user_id", 0)))
                            u_area = st.text_input("AREA", value=str(asset_data.get("AREA", "")))
                            u_reason = st.text_area("REASON", value=str(asset_data.get("REASON", "")))

                        # Form boundary submission button
                        submit_button = st.form_submit_button("SUBMIT CHANGES")
                        if submit_button:
                            if chosen_mapping_id is not None:
                                updated_data = {
                                    "SERIAL_NO": u_serial_no,
                                    "MODEL": u_model,
                                    "TYPE": u_type,
                                    "KVA": u_kva,
                                    "user_id": u_user_id,
                                    # 🛑 Removed "TRANSFER_STATUS" mapping payload key completely
                                    "location_mapping_id": chosen_mapping_id,
                                    "MANUF_YR": u_manuf_yr.isoformat() if hasattr(u_manuf_yr, "isoformat") else str(u_manuf_yr),
                                    "SERVICE_YR_KOC": u_service_yr_koc.isoformat() if hasattr(u_service_yr_koc,
                                                                                              "isoformat") else str(
                                        u_service_yr_koc),
                                    "RUN_Hrs": u_run_hrs,
                                    "AREA": u_area,
                                    "APPR_KVA": u_appr_kva,
                                    "USER": u_user,
                                    "CREW": u_crew,
                                    "MOVED_FROM": u_moved_from,
                                    "MOVEMENT_DATE": u_movement_yr.isoformat() if hasattr(u_movement_yr, "isoformat") else str(
                                        u_movement_yr),
                                    "REASON": u_reason,
                                    "updated_by": st.session_state.get('user_email', 'SYSTEM_USER')
                                }

                                try:
                                    with st.spinner("Pushing record modifications..."):
                                        supabase.table(TABLE_NAME).update(updated_data).eq("G-CODE", select_gcode).execute()
                                        st.cache_data.clear()
                                        st.success(f"🎉 Asset {select_gcode} altered successfully!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Transaction rejected by backend database: {e}")
                            else:
                                st.error(
                                    "❌ Could not find a valid matching entry ID inside your master location mapping tables. Check your route options.")
                        else:
                            st.warning("No assets available in the current database view.")
            except Exception as e:
                st.error(f"Operational form execution crashed: {e}")
        else:
            st.warning("Permission Denied: Authorized roles only.")




    with tab5:
        st.subheader("📜 System Operations Audit History Logs")
        if st.session_state.get('user_role') in ['Developer', 'Manager', 'Admin']:
            try:
                # 1. Fetch raw logs from Supabase
                logs_response = supabase.table("ASSET_AUDIT_LOG").select("*").order("changed_at", desc=True).limit(
                    100).execute()
                raw_data = logs_response.data

                if raw_data:
                    # 2. Convert base metadata to a starting DataFrame
                    base_df = pd.DataFrame(raw_data)

                    # 3. Flatten the 'old_data' JSON column safely
                    if "old_data" in base_df.columns:
                        # errors='ignore' ensures it won't crash if some values are null (like on a fresh INSERT)
                        old_data_flat = pd.json_normalize(base_df["old_data"].fillna({}))
                        # Add a prefix so you know these columns represent the OLD state
                        old_data_flat = old_data_flat.add_prefix("OLD_")
                    else:
                        old_data_flat = pd.DataFrame()

                    # 4. Flatten the 'new_data' JSON column safely
                    if "new_data" in base_df.columns:
                        new_data_flat = pd.json_normalize(base_df["new_data"].fillna({}))
                        # Add a prefix so you know these columns represent the NEW state
                        new_data_flat = new_data_flat.add_prefix("NEW_")
                    else:
                        new_data_flat = pd.DataFrame()

                    # 5. Clean up base metadata columns (drop the raw JSON columns)
                    base_cleaned = base_df.drop(columns=["old_data", "new_data"], errors="ignore")

                    # Make timestamps human-readable
                    if "changed_at" in base_cleaned.columns:
                        base_cleaned["changed_at"] = pd.to_datetime(base_cleaned["changed_at"]).dt.strftime(
                            "%Y-%m-%d %H:%M:%S")

                    # 6. Combine everything side-by-side into a single massive DataFrame
                    final_audit_df = pd.concat([base_cleaned, old_data_flat, new_data_flat], axis=1)

                    # 7. Display the beautifully structured DataFrame
                    st.dataframe(final_audit_df, use_container_width=True)

                    # Optional helper: Let them download this history view as a clean Excel/CSV file
                    st.download_button(
                        label="📥 Download Audit History as CSV",
                        data=final_audit_df.to_csv(index=False),
                        file_name="asset_audit_history.csv",
                        mime="text/csv"
                    )

                else:
                    st.info("No transactional record logs found inside the audit database yet.")
            except Exception as e:
                st.error(f"Failed to process log layout: {e}")
        else:
            st.warning("Access Denied: Only platform Administrators can audit operational changes.")
        # Verify user permissions
        if st.session_state.get('user_role') in ['Developer', 'Manager', 'Admin']:

            # --- 1. MANUAL DELETION / PURGE CONTROL PANEL ---
            with st.expander("🚨 DELETE LOGS :"):
                st.warning("⚠️ Actions taken here are permanent and cannot be undone. Proceed with caution.")

                col_p1, col_p2 = st.columns([2, 1])

                with col_p1:
                    purge_option = st.selectbox(
                        "Select a cleanup threshold:",
                        options=[
                            "Select an option...",
                            "Delete logs older than 30 days",
                            "Delete logs older than 60 days",
                            "Delete logs older than 90 days",
                            "Wipe ALL historical logs completely (Full Reset)"
                        ]
                    )

                with col_p2:
                    st.write("##")  # Visual alignment spacer
                    execute_purge = st.button("🔥 Execute Purge Transaction")

                if execute_purge:
                    if purge_option == "Select an option...":
                        st.error("Please select a valid cleanup timeframe threshold first.")
                    else:
                        from datetime import datetime, timedelta

                        try:
                            # Construct appropriate date threshold filter based on user selection
                            if "30 days" in purge_option:
                                cutoff = (datetime.now() - timedelta(days=30)).isoformat()
                                supabase.table("ASSET_AUDIT_LOG").delete().lt("changed_at", cutoff).execute()
                                st.success("✅ Cleaned up log data older than 30 days.")
                            elif "60 days" in purge_option:
                                cutoff = (datetime.now() - timedelta(days=60)).isoformat()
                                supabase.table("ASSET_AUDIT_LOG").delete().lt("changed_at", cutoff).execute()
                                st.success("✅ Cleaned up log data older than 60 days.")
                            elif "90 days" in purge_option:
                                cutoff = (datetime.now() - timedelta(days=90)).isoformat()
                                supabase.table("ASSET_AUDIT_LOG").delete().lt("changed_at", cutoff).execute()
                                st.success("✅ Cleaned up log data older than 90 days.")
                            elif "Full Reset" in purge_option:
                                # To wipe everything, target all IDs greater than 0
                                supabase.table("ASSET_AUDIT_LOG").delete().gt("id", 0).execute()
                                st.success("💥 Database Audit Log completely cleared out!")

                            # Clear frontend reading cache and force UI synchronization
                            st.cache_data.clear()
                            st.rerun()

                        except Exception as e:
                            st.error(f"Failed to execute manual purge request: {e}")

            st.markdown("---")

            # --- 2. LOGS RETRIEVAL AND FLATTENING VIEW ---
            try:
                # Fetch latest data state post any purge modifications
                logs_response = supabase.table("ASSET_AUDIT_LOG").select("*").order("changed_at", desc=True).limit(
                    100).execute()
                raw_data = logs_response.data

                if raw_data:
                    base_df = pd.DataFrame(raw_data)

                    # Flatten the 'old_data' JSON column safely
                    if "old_data" in base_df.columns:
                        old_data_flat = pd.json_normalize(base_df["old_data"].fillna({}))
                        old_data_flat = old_data_flat.add_prefix("OLD_")
                    else:
                        old_data_flat = pd.DataFrame()

                        # Flatten the 'new_data' JSON column safely
                        if "new_data" in base_df.columns:
                            new_data_flat = pd.json_normalize(base_df["new_data"].fillna({}))
                            new_data_flat = new_data_flat.add_prefix("NEW_")
                        else:
                            new_data_flat = pd.DataFrame()

                        # Drop original nested columns
                        base_cleaned = base_df.drop(columns=["old_data", "new_data"], errors="ignore")

                        if "changed_at" in base_cleaned.columns:
                            base_cleaned["changed_at"] = pd.to_datetime(base_cleaned["changed_at"]).dt.strftime(
                                "%Y-%m-%d %H:%M:%S")

                        # Build combined clean tabular side-by-side array sheet
                        final_audit_df = pd.concat([base_cleaned, old_data_flat, new_data_flat], axis=1)

                        st.dataframe(final_audit_df, use_container_width=True)

                        st.download_button(
                            label="📥 Download Filtered Audit Snapshot (CSV)",
                            data=final_audit_df.to_csv(index=False),
                            file_name="asset_audit_report.csv",
                            mime="text/csv"
                        )

                else:
                    st.info("No transactional record logs found inside the audit database yet.")
            except Exception as e:
                st.error(f"Failed to process log layout view structures: {e}")

        else:
            st.warning("Access Denied: Only platform Administrators can inspect or alter operations audit logs.")



#------WORKSHOP-UNIT----
elif selected == "WORKSHOP":
    st.info("🛠️******WELCOME TO WORKSHOP OVERVIEW FOR ASSETS CURRENTS UNDER WORKSHOP REPAIR******")

    df = get_full_dataframe_with_realations()
    # Filter for units currently in the workshop
    df_ws = df[df['LOCATION'] == "WORKSHOP"].copy()

    if not df_ws.empty:
        # Convert MOVEMENT_DATE to datetime and calculate age
        df_ws['MOVEMENT_DATE'] = pd.to_datetime(df_ws['MOVEMENT_DATE'])
        df_ws['Days_in_WS'] = (datetime.now() - df_ws['MOVEMENT_DATE']).dt.days

        # Sort by oldest repair first
        df_ws = df_ws.sort_values(by='Days_in_WS', ascending=False)

        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Units in Workshop", len(df_ws))
        m2.metric("Oldest Repair (Days)", df_ws['Days_in_WS'].max())
        m3.metric("Avg. Repair Time", round(df_ws['Days_in_WS'].mean(), 1))


        # Color-coded highlight for "Stuck" assets (e.g., more than 14 days)
        def color_age(val):
            color = 'red' if val > 14 else 'orange' if val > 7 else 'white'
            return f'color: {color}'


        st.caption("### 📋 Repairs in WORKSHOP (Oldest First)")
        st.dataframe(
            df_ws[['G-CODE', 'MODEL','KVA', 'REASON', 'Days_in_WS', 'MOVEMENT_DATE','STATUS']]
            .style.map(color_age, subset=['Days_in_WS']),
            use_container_width=True
        )
        with st.expander("📝 Update Unit Status"):
            with st.form("status_update"):
                selected_unit = st.selectbox("Select G-CODE", options=df_ws['G-CODE'].tolist())
                new_status = st.selectbox("New Status", ["In-Repair", "Waiting for Parts", "READY"])
                notes = st.text_input("Technical Notes")
                update_btn = st.form_submit_button("Update Status")

                if update_btn:
                    # Update status in Supabase
                    supabase.table("GENSET ASSET").update({"STATUS": f"{new_status}"}).eq("G-CODE",
                                                                                               selected_unit).execute()
                    st.cache_data.clear()
                    st.success(f"Unit {selected_unit} is now marked as {new_status}")
                    st.rerun()
        st.caption("Workshop Reports")
        col1, col2, col3 = st.columns(3)

        with (col1):
            with st.expander('READY IN WORKSHOP'):
                df=supabase.table("GENSET ASSET").select("G-CODE","MODEL","KVA","REASON","STATUS"
                                                         ).eq("STATUS",'READY').execute()
                st.dataframe(df.data)
        with (col2):
            with st.expander('IN REPAIR'):
                df=supabase.table("GENSET ASSET").select("G-CODE","MODEL","KVA","REASON","STATUS"
                                                         ).eq('STATUS','In-Repair').execute()
                st.dataframe(df.data)
        with (col3):
            with st.expander('WAITING'):
                df = supabase.table("GENSET ASSET").select("G-CODE", "MODEL", "KVA", "REASON", "STATUS"
                                                           ).eq('STATUS', 'Waiting for parts').execute()
                st.dataframe(df.data)
    else:
        st.success("No assets currently in the workshop.")

elif selected == "MAINTENANCE":

    # ----enter code with access permission-----


    st.info("🕒 **PREDICTIVE MAINTENANCE & DUE DATES FORECASTING**")
    df_assets = get_full_dataframe_with_realations()

    if user_role.lower() in ['developer', 'Manager', 'Supervisor', 'Engineer',
                             'Mechanical'] and not df_assets.empty:

        # --- 1. DROPDOWN SEARCH & COUNTERS ---
        asset_list = df_assets['G-CODE'].tolist()
        selected_asset = st.selectbox("Search Asset for Service History", options=asset_list)

        if selected_asset:
            asset_data = df_assets[df_assets['G-CODE'] == selected_asset].iloc[0]
            last_pm_date = pd.to_datetime(asset_data.get('PLANNED_PM', datetime.now())).date()
            days_since_pm = (datetime.now().date() - last_pm_date).days

            rem_a = 15 - days_since_pm
            rem_b = 90 - days_since_pm

            c1, c2, c3 = st.columns(3)
            c1.metric("Last Service Date", str(last_pm_date))
            c2.metric("A SERVICE (15d) Countdown", f"{rem_a} Days", delta=rem_a,
                      delta_color="normal" if rem_a > 0 else "inverse")
            c3.metric("B SERVICE (90d) Countdown", f"{rem_b} Days", delta=rem_b,
                      delta_color="normal" if rem_b > 0 else "inverse")

            # (Keep your existing col01 and col02 code here for the unit logs and data entry form)
            col01, col02 = st.columns(2)
            with col01:
                with st.expander("UNIT REPORT:"):
                    try:
                        history_resp = supabase.table("SERVICE_LOGS").select("*").eq("g_code",
                                                                                     selected_asset).order(
                            "service_date", desc=True).execute()
                        df_history = pd.DataFrame(history_resp.data)
                        if not df_history.empty:
                            chart_df = df_history.copy()
                            chart_df['service_date'] = pd.to_datetime(chart_df['service_date'])
                            fig_trend = px.line(chart_df.sort_values('service_date'), x='service_date',
                                                y='run_hours', title="Usage Trend Line")
                            st.plotly_chart(fig_trend, use_container_width=True)
                            st.table(df_history[['service_date', 'service_type', 'run_hours', 'notes']])
                        else:
                            st.info("No logs linked for asset index.")
                    except Exception as e:
                        st.error(f"Error reading records logs: {e}")

            with col02:
                if user_role in ['Developer', 'Manager','Supervisor','TECHNICIAN']:
                    with st.expander("UPDATE SERVICE FORM :", expanded=True):
                        with st.form("service_log_form", clear_on_submit=True):
                            col1, col2 = st.columns(2)

                            with col1:
                                # CHANGED: Now pulls the entire asset list so you can select or type any G-CODE
                                g_code = st.selectbox(
                                    "Select G-CODE for Service",
                                    options=asset_list,
                                    index=asset_list.index(selected_asset) if selected_asset in asset_list else 0
                                )
                                s_date = st.date_input("Service Date", value=datetime.now().date())
                                s_type = st.selectbox("Service Track Target",
                                                      ["A SERVICE (15d)", "B SERVICE (90d)", "BREAKDOWN"])

                            with col2:
                                s_hrs = st.number_input("Current Running Hours Index", min_value=0, step=1)
                                s_notes = st.text_area("Mechanical Notes & Components Log")

                            st.markdown("---")
                            st.write("🔧 Excel-Style Inventory Allocation")
                            st.caption(
                                "Double-click cells to enter details. Click '+' below the table to add more parts.")

                            parts_template = pd.DataFrame([{"Part Name": "", "Quantity Used": 1}])
                            edited_parts_df = st.data_editor(
                                parts_template,
                                num_rows="dynamic",
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Part Name": st.column_config.SelectboxColumn(
                                        "Part Name / Description",
                                        options=["Oil Filter", "Fuel Filter", "Air Filter", "V-Belt",
                                                 "15W40 Engine Oil (Ltrs)", "Coolant"],
                                        required=True,
                                        width="large"
                                    ),
                                    "Quantity Used": st.column_config.NumberColumn(
                                        "Quantity Used",
                                        min_value=1,
                                        step=1,
                                        required=True,
                                        width="small"
                                    )
                                }
                            )

                            if st.form_submit_button("Submit & Cycle Tracking Status"):
                                try:
                                    # Step A: Package data for SERVICE_LOGS
                                    log_entry = {
                                        "g_code": g_code,
                                        "service_date": str(s_date),
                                        "service_type": s_type,
                                        "run_hours": s_hrs,
                                        "notes": s_notes
                                    }

                                    # Write history log record and capture the row ID back
                                    response = supabase.table("SERVICE_LOGS").insert(log_entry).execute()
                                    new_service_id = response.data[0]['id']

                                    # Step B: Read and bulk insert inventory components items
                                    parts_to_insert = []
                                    for _, row in edited_parts_df.iterrows():
                                        if str(row["Part Name"]).strip() != "":
                                            parts_to_insert.append({
                                                "service_log_id": new_service_id,
                                                "part_name": row["Part Name"],
                                                "quantity": int(row["Quantity Used"])
                                            })

                                            if parts_to_insert:
                                                supabase.table("PARTS_USED").insert(parts_to_insert).execute()

                                            # Step C: Dynamically update the correct engine row targeting the selectbox choice
                                            supabase.table(TABLE_NAME).update({
                                                "PLANNED_PM": str(s_date),
                                                "RUN_Hrs": s_hrs
                                            }).eq("G-CODE", g_code).execute()

                                            st.cache_data.clear()
                                            st.success(
                                                f"✅ Service parameters mapped cleanly to asset log registry: {g_code}")
                                            st.rerun()
                                except Exception as e:
                                    st.error(f"Write failure execution string: {e}")
                else:
                    st.warning("access denied to upadate serviced assets")



        # --- 2. THE NEW UPCOMING DUE DATES FORECAST GRAPH (Replaces Old History Timeline) ---
        st.divider()
        st.caption("📊 Fleet Maintenance Forecasting: Upcoming Due Dates")

        try:
            # Clone the full assets table to calculate deadlines safely
            df_forecast = df_assets.copy()

            # Make sure dates are properly formatted
            df_forecast['PLANNED_PM'] = pd.to_datetime(df_forecast['PLANNED_PM'])

            # Drop rows where there is no baseline date to prevent app crashes
            df_forecast = df_forecast.dropna(subset=['PLANNED_PM'])

            # Array to store our calculated calculations
            due_records = []

            for _, row in df_forecast.iterrows():
                gcode = row['G-CODE']
                last_pm = row['PLANNED_PM']

                # Check how many minor A services were done since the last major B service
                # to dynamically determine if the very next task is an A (15 days) or B (90 days)
                try:
                    last_b = supabase.table("SERVICE_LOGS").select("service_date").eq("g_code", gcode).eq(
                        "service_type", "B SERVICE (90d)").order("service_date", desc=True).limit(1).execute()
                    query = supabase.table("SERVICE_LOGS").select("id").eq("g_code", gcode).eq("service_type",
                                                                                               "A SERVICE (15d)")
                    if last_b.data:
                        query = query.gt("service_date", last_b.data[0]['service_date'])
                    a_count = len(query.execute().data)
                except:
                    a_count = 0  # Fallback gracefully if logging references fail

                # Assign cycle interval parameters based on asset history
                if a_count >= 5:
                    next_service_type = "B SERVICE (90d)"
                    days_to_add = 90
                else:
                    next_service_type = "A SERVICE (15d)"
                    days_to_add = 15

                # Calculate exact upcoming target calendar date
                calculated_due_date = last_pm + pd.Timedelta(days=days_to_add)
                days_remaining = (calculated_due_date.date() - datetime.now().date()).days

                due_records.append({
                    "G-CODE": gcode,
                    "Last Service Date": last_pm.strftime("%Y-%m-%d"),
                    "Next Required Task": next_service_type,
                    "Upcoming Due Date": calculated_due_date,
                    "Days Remaining": days_remaining,
                    "Status": "OVERDUE 🚨" if days_remaining < 0 else "Urgent (<=3 Days) ⚠️" if days_remaining <= 3 else "On Schedule ✅"
                })

            df_due_chart = pd.DataFrame(due_records)

            if not df_due_chart.empty:
                # Sort so the engines closest to breaking down or overdue hit the top of your list
                df_due_chart = df_due_chart.sort_values(by="Upcoming Due Date", ascending=True)

                # Build a forward-looking scatter timeline showing exact target due dates
                fig_forecast = px.scatter(
                    df_due_chart,
                    x="Upcoming Due Date",
                    y="G-CODE",
                    color="Status",
                    symbol="Next Required Task",
                    color_discrete_map={"OVERDUE 🚨": "#FF4B4B", "Urgent (<=3 Days) ⚠️": "#FFAA00",
                                        "On Schedule ✅": "#00CC66"},
                    hover_data=["Last Service Date", "Days Remaining", "Next Required Task"],
                    title="Timeline Grid: Target Execution Dates for Fleet Operations",
                )

                # Highlight 'Today' with a vertical baseline reference line so you see exactly what's late
                fig_forecast.add_vline(x=datetime.now().timestamp() * 1000, line_width=2, line_dash="dash",
                                       line_color="black")

                st.plotly_chart(fig_forecast, use_container_width=True)

                # Show a scannable ledger right below it
                with st.expander("📋 Scannable Asset Due Date Tracker"):
                    st.dataframe(df_due_chart, use_container_width=True, hide_index=True)
            else:
                st.info("No timeline data generated.")

        except Exception as e:
            st.error(f"Error generating predictive timeline layout: {e}")


elif selected == "PARTS AND PRODUCTS":
    st.info("****WELCOME TO THE PARTS AND PRODUCTS OVERVIEW****")
    # ----enter code with access permission-----
    # 1. Fetch live consumption ledger from your database link table
    try:
        parts_response = supabase.table("PARTS_USED").select("part_name, quantity").execute()
        df_parts = pd.DataFrame(parts_response.data)

        if not df_parts.empty:
            # 2. Group matching part strings together and sum up quantities
            inventory_summary = df_parts.groupby("part_name")["quantity"].sum().reset_index()
            inventory_summary.columns = ["Part Description", "Total Fleet Consumption To-Date"]

            # 3. Output as a clean, styled ledger sheet
            st.write("### 📊 Lifetime Fleet Inventory Usage Ledger")
            st.dataframe(
                inventory_summary.style.bar(subset=["Total Fleet Consumption To-Date"], color="#b3d9ff", vmin=0),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No parts consumption logs are available yet.")

    except Exception as e:
        st.error(f"Failed to load inventory counts: {e}")
    pass
elif selected == "FIXED ASSETS":
    st.info("****WELCOME TO FIXED ASSETS OTHER ASSETS AND TOOLS****")
    # ----enter code with access permission-----
    pass
elif selected == "FLEET MANAGEMENT":
    st.info("****WELCOME TO FLEET MANAGEMENT UNIT****")
    # ----enter code with access permission-----
    pass


elif selected == "LOCATION_MAPPING":
    st.info("🛠️ **MASTER ROUTING UTILITIES AND INFRASTRUCTURE MANAGEMENT**")

    if user_role in ['Developer', 'Manager', 'Admin']:
        st.write("⚙️ Authorize New Core Location Path Setup")

        # --- 1. THE DATA SUBMISSION FORM BLOCK ---
        with st.form("Admin_route_mapping_tool", clear_on_submit=True):
            new_field = st.selectbox("Assign Field *",
                                     options=FIELD_LIST)
            new_area = st.text_input("Assign Area *").strip().upper()
            new_loc = st.text_input("Assign Location Description *").strip().upper()
            new_contract = st.text_input("Assign Corporate Contract No *").strip().upper()

            submit_route = st.form_submit_button("Authorize Combined Route Entry")

            if submit_route:
                if not new_field or not new_area or not new_loc or not new_contract:
                    st.error("❌ Submission Rejected: All fields marked with an asterisk (*) are strictly required.")
                else:
                    try:
                        route_payload = {
                            "FIELD": new_field,
                            "AREA": new_area,
                            "LOCATION": new_loc,
                            "CONTRACT_NO": new_contract
                        }
                        supabase.table("LOCATION_MAPPING").insert(route_payload).execute()
                        st.cache_data.clear()
                        st.toast("✅ Master hierarchy route entry logged successfully!", icon="🔥")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to map combo path: {e}")

        # --- 2. THE VISUAL DISPLAY BLOCK (💥 MOVED ENTIRELY OUTSIDE THE FORM WITH LEFT INDENTATION) ---
        st.markdown("---")
        st.caption("Active Routing Infrastructure Breadcrumbs")

        current_maps = get_location_mappings()
        if not current_maps.empty:
            # 🔧 Safely generate string paths mapping (fixes the previous TypeError)
            current_maps['display_path'] = (
                    "📍 Field: " + current_maps['FIELD'].astype(str) +
                    " ➔ Area: " + current_maps['AREA'].astype(str) +
                    " ➔ Location: " + current_maps['LOCATION'].astype(str) +
                    " ➔ Contract: " + current_maps['CONTRACT_NO'].astype(str)
            )

            for idx, row in current_maps.iterrows():
                path_label = row['display_path']

                col_txt, col_btn = st.columns([5, 1])
                with col_txt:
                    st.caption(path_label)
                with col_btn:
                    # 🔥 FIX: Added cross-reference index '_idx' to guarantee a unique key name!
                    if st.button("🗑️", key=f"del_map_{row['id']}_{idx}"):
                        success, message = delete_location_mapping(int(row['id']))
                        if success:
                            st.toast(message, icon="🗑️")
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.info("No mapped paths configured in database tables yet.")

    