import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, date
import numpy as np
import base64
import os
import time

min_date = date(1900, 1, 1)
max_date = datetime.today().date()

# =====================================================================
# 1. PAGE INITIALIZATION & DATABASE CONFIGURATION (MUST BE FIRST)
# =====================================================================
st.set_page_config(
    page_title="Field Operations",
    layout="wide"
)

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(URL, KEY)


supabase = get_supabase_client()


# -----------------------------------------------------------------
# DYNAMIC USER REGISTRY LOADING
# -----------------------------------------------------------------
@st.cache_data(ttl=600)  # Caches for 10 minutes, clears on update
def load_user_registry():
    try:
        res = supabase.table("USER_REGISTRY").select("user_name").order("user_name", ascending=True).execute()
        if res.data and len(res.data) > 0:
            return ['----'] + [row['user_name'] for row in res.data]
        return ['----', 'ESP-KOC', 'JO-ESP', 'WORKSHOP', 'BURGUN-YRD', 'MOBILE', 'OFF-HIRE']  # Sensible fallback
    except Exception as e:
        return ['----', 'ESP-KOC', 'JO-ESP', 'WORKSHOP','BURGUN','MOBILE','OFF-HIRE','ABDALY-FARM','READY','DESALTER-PROJECT',
                'FIELD_OP.REPAIR','GAS-MITIGATION','MISHRIF','PDI','WS-POWER']  # Fault safe fallback


# Globally populated list used by all asset dropdown forms (DO NOT OVERWRITE BELOW)
USER_LIST = load_user_registry()


@st.cache_data(show_spinner=False)
def inject_custom_css(css_file_path: str = "style.css"):
    try:
        with open(css_file_path, "r") as f:
            css_style = f.read()
        return f"<style>{css_style}</style>"
    except FileNotFoundError:
        return ""


# --- DATABASE CACHING UTILITIES ---
@st.cache_data(ttl=15)
def get_assets_df() -> pd.DataFrame:
    try:
        res = supabase.table("ASSETS").select("*").order("id").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Error connecting to assets database context: {e}")
        return pd.DataFrame()


def log_audit_event(g_code: str, action: str, status: str, description: str, old_data: dict = None,
                    new_data: dict = None):
    try:
        current_operator = st.session_state.get("auth_user_email", "SYSTEM_AUTO")
        log_payload = {
            "g_code": str(g_code).strip().upper(),
            "action_type": str(action).upper(),
            "transfer_status": str(status) if status and status != '----' else "N/A",
            "details": str(description),
            "old_values": old_data,
            "new_values": new_data,
            "changed_by": current_operator
        }
        supabase.table("AUDIT_LOGS").insert(log_payload).execute()
    except Exception as audit_err:
        st.error(f"⚠️ Log Insert Failure: {audit_err}")


def get_audit_logs_df() -> pd.DataFrame:
    try:
        res = supabase.table("AUDIT_LOGS").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
        return pd.DataFrame()


def delete_old_audit_logs(days_retention=30, purge_all=False):
    try:
        if purge_all:
            response = supabase.table("AUDIT_LOGS").delete().neq("g_code", "").execute()
        else:
            from datetime import datetime, timedelta, timezone
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_retention)
            cutoff_iso = cutoff_date.isoformat()
            response = supabase.table("AUDIT_LOGS").delete().lt("created_at", cutoff_iso).execute()
        return {"status": "success", "row_count": len(response.data) if response.data else 0}
    except Exception as err:
        return {"status": "error", "message": str(err)}


#Application Base Matrix Profiles
TRANS_LIST = ['----', 'NEW GENERATOR', 'DISPATCH', 'RECEIVED', 'INTERNAL-SHIFT']


# Zebra Striping Engine Function Matrix
def style_zebra_rows(df):
    styles = pd.DataFrame('', index=df.index, columns=df.columns)
    styles.iloc[0::2, :] = 'background-color: #f0f9ff;'
    return styles


# =====================================================================
# 2. PERSISTENT SECURITY STATE INITIALIZATION KEYS
# =====================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_user_email" not in st.session_state:
    st.session_state["auth_user_email"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

# =====================================================================
# 3. IDENTITY GATEWAY SECURITY ROUTING
# =====================================================================
if not st.session_state["authenticated"]:
    st.markdown(
        """
        <style>
            .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important; }
            .block-container { padding-top: 5rem !important; }
            .login-card-container { background-color: #ffffff; border-radius: 14px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); overflow: hidden; border: 1px solid #e0e4ec; }
            .login-blue-header { background: linear-gradient(90deg, #4da3ff, #80bfff); padding: 2rem 1.5rem; text-align: center; color: #ffffff !important; }
            .header-title-container { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 0.4rem; }
            .header-logo { height: 45px; width: auto; object-fit: contain; }
            .login-blue-header h2 { color: #ffffff !important; margin: 0 !important; font-weight: 700 !important; font-size: 1.6rem !important; letter-spacing: 0.5px; line-height: 1.2; }
            .login-blue-header p { color: #f0f5ff !important; margin: 0 !important; font-size: 0.9rem !important; opacity: 0.9; padding-top: 0.5rem; }
            .login-form-body { padding: 2rem; }
        </style>
        """, unsafe_allow_html=True
    )


    def get_base64_image(img_path):
        if os.path.exists(img_path):
            with open(img_path, "rb") as img_file:
                return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
        return "https://via.placeholder.com/150"


    logo_file_path = "logo.png"
    img_base64 = get_base64_image(logo_file_path)

    _, login_container_col, _ = st.columns([1, 1.8, 1])
    with login_container_col:
        st.markdown('<div class="login-card-container">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="login-blue-header">
                <div class="header-title-container">
                    <img src="{img_base64}" class="header-logo" alt="Corporate Logo">
                    <h2>Field Operations Digital Assets Monitoring System</h2>
                </div>
                <p>Enterprise Digital Asset Management Registry Identity Authentication Portal</p>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown('<div class="login-form-body">', unsafe_allow_html=True)

        with st.form(key="gateway_security_login_form"):
            email_input = st.text_input("Account Corporate Email Address:", placeholder="username@company.com").strip()
            password_input = st.text_input("Account Secret Credentials Key:", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.form_submit_button("VALIDATE SECURITY CREDENTIALS", use_container_width=True):
                if not email_input or not password_input:
                    st.error("❌ Credentials validation failure: Input parameters cannot be blank.")
                else:
                    with st.spinner("Processing authorization handshakes..."):
                        try:
                            auth_res = supabase.auth.sign_in_with_password(
                                {"email": email_input, "password": password_input})
                            target_uid = auth_res.user.id
                            profile_query = supabase.table("user_profiles").select("role").eq("id",
                                                                                              target_uid).execute()

                            if profile_query.data:
                                user_assigned_role = profile_query.data[0]["role"]
                                st.session_state["authenticated"] = True
                                st.session_state["auth_user_email"] = auth_res.user.email
                                st.session_state["user_role"] = user_assigned_role
                                st.success(f"🎉 Welcome back! Role: {user_assigned_role}")
                                st.rerun()
                            else:
                                st.error(
                                    "❌ Access Denied: Your email is in Auth, but missing a row in 'user_profiles' table.")
                        except Exception as auth_fail:
                            st.error(f"❌ Authentication Denied: {str(auth_fail)}")
        st.markdown('</div></div>', unsafe_allow_html=True)

else:
    # =====================================================================
    # 4. DATA INITIALIZATION & ENVIRONMENT VIEW LAYOUT OVERLAYS (GATEWAY PROTECTED)
    # =====================================================================
    @st.cache_data(ttl=30)
    def get_mappings_df() -> pd.DataFrame:
        try:
            res = supabase.table("asset_mappings").select("*").order("type").execute()
            df = pd.DataFrame(res.data)
            if df.empty:
                return pd.DataFrame(columns=['id', 'type', 'model', 'kva'])
            return df
        except Exception as e:
            st.error(f"Error loading engineering model specification profiles: {e}")
            return pd.DataFrame(columns=['id', 'type', 'model', 'kva'])


    @st.cache_data(ttl=10)
    def get_routing_matrix_df() -> pd.DataFrame:
        try:
            res = supabase.table("field_routing_matrix").select("*").order("field_name").execute()
            df = pd.DataFrame(res.data)
            if df.empty:
                return pd.DataFrame(columns=['id', 'field_name', 'area_name', 'location_name'])
            return df
        except Exception as e:
            st.error(f"Error fetching structural routing profiles: {e}")
            return pd.DataFrame(columns=['id', 'field_name', 'area_name', 'location_name'])


    mappings_df = get_mappings_df()
    TYPE_LIST = ['----'] + sorted(mappings_df['type'].unique().tolist()) if not mappings_df.empty else ['----']
    routing_df = get_routing_matrix_df()
    LIVE_FIELD_OPTIONS = ['----'] + sorted(routing_df['field_name'].unique().tolist()) if not routing_df.empty else [
        '----']
    MAPPED_LOCATIONS_POOL = ['----'] + sorted(
        routing_df['location_name'].dropna().unique().tolist()) if not routing_df.empty else ['----']

    st.markdown(inject_custom_css("style.css"), unsafe_allow_html=True)
    st.markdown(
        """
        <style>
            header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; height: 3.5rem; z-index: 999; }
            .block-container { padding-top: 4.5rem !important; padding-bottom: 1rem; padding-left: 2rem; padding-right: 2rem; }
            .custom-topbar {
                position: fixed; top: 0; left: 0; right: 0; height: 50px; background-color: #1e3a8a;
                color: #ffffff; display: flex; align-items: center; justify-content: center;
                padding: 0 2rem; z-index: 9999; box-shadow: 0px 2px 5px rgba(0,0,0,0.2); font-family: sans-serif;
            }
            .topbar-brand { font-size: 1.2rem; font-weight: bold; letter-spacing: 1px; text-align: center; }
        </style>
        <div class="custom-topbar"><div class="topbar-brand">FIELD OPERATIONS DIGITAL ASSETS MONITORING SYSTEM</div></div>
        """, unsafe_allow_html=True
    )

    user_clearance_role = st.session_state["user_role"]
    if user_clearance_role in ["MANAGER", "DEVELOPER", "SUPERVISOR", "ENGINEER"]:
        allowed_views = ["GENERAL_ASSETS", "ASSET MANAGEMENT", "AUDIT LOGS", "WORKSHOP", "STORES & PARTS",
                         "MAINTENANCE", "FLEET MANAGEMENT", "REMOTE TELEMETRY", "REPORTS", "SETTINGS"]
    else:
        allowed_views = ["GENERAL_ASSETS", "ASSET MANAGEMENT"]

    # =====================================================================
    # 5. SIDEBAR CONTROLLER WRAPPER
    # =====================================================================
    st.sidebar.title("GENSET FIELD_OPERATIONS")
    st.sidebar.markdown(
        f"👤 **Identity:** `{st.session_state['auth_user_email']}`  \n🛡️ **Role:** `{user_clearance_role}`")

    navigation_target = st.sidebar.radio("Choose an operational viewport module:", options=allowed_views,
                                         label_visibility="visible")

    st.sidebar.divider()
    if st.sidebar.button("🔄 Refresh page", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🚪 Log-out", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except:
            pass
        st.session_state["authenticated"] = False
        st.session_state["auth_user_email"] = None
        st.session_state["user_role"] = None
        st.rerun()

    # =====================================================================
    # 1. GENERAL ASSETS RUNTIME VIEWPORT
    # =====================================================================
    if navigation_target == "GENERAL_ASSETS":
        df = get_assets_df()
        if not df.empty:
            try:
                user_counts = df['USER'].value_counts()
                v_ESP = user_counts.get('ESP-KOC', 0)
                v_WHP = user_counts.get('WORKSHOP', 0)
                v_JO = user_counts.get('JO-ESP', 0)
                v_BYRD = user_counts.get('BURGUN-YRD', 0)
                v_MBL = user_counts.get('MOBILE', 0)
                v_OFF = user_counts.get('OFF-HIRE', 0)
                v_abd = user_counts.get('ABDALY-FARM', 0)
                v_RDY = user_counts.get('READY', 0)
                v_DST = user_counts.get('DESALTER-PROJECT', 0)
                v_FD = user_counts.get('FIELD_OP.REPAIR', 0)
                v_GAS = user_counts.get('GAS-MITIGATION', 0)
                v_MHF = user_counts.get('MISHRIF', 0)
                v_PDI = user_counts.get('PDI', 0)
                v_WPP = user_counts.get('WS-POWER', 0)
                v_TT = len(df)

                st.caption("QUICK ASSET ANALYSIS BY CURRENT USER")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric('ESP-KOC', int(v_ESP), delta='+', delta_color="blue", border=True)
                    st.metric('WORKSHOP', int(v_WHP), delta='+', delta_color="blue", border=True)
                    st.metric('JO-ESP', int(v_JO), delta='+', delta_color="blue", border=True)
                with col2:
                    st.metric('BURGUN-YRD', int(v_BYRD), delta='+', delta_color="blue", border=True)
                    st.metric('MOBILE', int(v_MBL), delta='+', delta_color="blue", border=True)
                    st.metric('OFF-HIRE', int(v_OFF), delta='+', delta_color="blue", border=True)
                with col3:
                    st.metric('ABDALY-FARM', int(v_abd), delta='+', delta_color="blue", border=True)
                    st.metric('READY', int(v_RDY), delta='+', delta_color="blue", border=True)
                    st.metric('DESALTER-PROJECT', int(v_DST), delta='+', delta_color="blue", border=True)
                with col4:
                    st.metric('FIELD-OP/REPAR', int(v_FD), delta='+', delta_color="blue", border=True)
                    st.metric('GAS-MITIGATION', int(v_GAS), delta='+', delta_color="blue", border=True)
                    st.metric('MISHRIF', int(v_MHF), delta='+', delta_color="blue", border=True)
                with col5:
                    st.metric('PDI', int(v_PDI), delta='+', delta_color="blue", border=True)
                    st.metric('WS-POWER', int(v_WPP), delta='+', delta_color="blue", border=True)
                    st.metric('TOTAL', int(v_TT), delta='+', delta_color="blue", border=True)
            except Exception as e:
                st.error(f"Error parsing status metrics: {e}")
        else:
            st.info("No corporate equipment assets found inside database inventory.")

    # =====================================================================
    # 2. ASSET MANAGEMENT ACTIONS ENGINE
    # =====================================================================
    elif navigation_target == "ASSET MANAGEMENT":
        df = get_assets_df()
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ['ASSETS_VIEW', 'ADD_ASSET', 'UPDATE_ASSET', 'DELETE_ASSET', 'AUDIT LOGS'])

        with tab1:
            if not df.empty:
                designed_assets_df = df.style.apply(style_zebra_rows, axis=None)
                st.dataframe(designed_assets_df, use_container_width=True, hide_index=True)
            else:
                st.info("No equipment inventory assets found inside database registries.")

        with tab2:
            st.caption("Step 1: Select Engine Specification Profile Matrix")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                u_type = st.selectbox('Select Manufacturer TYPE:', options=TYPE_LIST, key="add_type_outside")
            with m_col2:
                add_filtered = mappings_df[mappings_df['type'] == u_type] if u_type != '----' else pd.DataFrame()
                add_allowed_models = ['----'] + sorted(
                    add_filtered['model'].unique().tolist()) if not add_filtered.empty else ['----']
                u_model = st.selectbox('Select Engine MODEL:', options=add_allowed_models, key="add_model_outside")
            with m_col3:
                add_matched_row = add_filtered[
                    add_filtered['model'] == u_model] if u_model != '----' else pd.DataFrame()
                calculated_kva = int(add_matched_row.iloc[0]['kva']) if not add_matched_row.empty else 0
                u_kva = st.number_input('Assigned Rating (KVA):', min_value=0, value=calculated_kva, step=10,
                                        key="add_kva_outside")

            st.markdown("---")
            st.caption("Step 2: select field")

            cascade_col1, cascade_col2, cascade_col3 = st.columns(3)
            with cascade_col1:
                u_field = st.selectbox('FIELD Grouping Placement:', options=LIVE_FIELD_OPTIONS, key="add_field_cascade")
            with cascade_col2:
                field_matched_df = routing_df[
                    routing_df['field_name'] == u_field] if u_field != '----' else pd.DataFrame()
                ALLOWED_AREAS = ['----'] + sorted(
                    field_matched_df['area_name'].unique().tolist()) if not field_matched_df.empty else ['----']
                u_area = st.selectbox('AREA Registry Code:', options=ALLOWED_AREAS, key="add_area_cascade")
            with cascade_col3:
                area_matched_df = field_matched_df[
                    field_matched_df['area_name'] == u_area] if u_area != '----' else pd.DataFrame()
                ALLOWED_LOCATIONS = ['----'] + sorted(
                    area_matched_df['location_name'].unique().tolist()) if not area_matched_df.empty else ['----']
                u_location = st.selectbox('Target TO_LOCATION Profile Node:', options=ALLOWED_LOCATIONS,
                                          key="add_location_cascade")

            with st.form('ASSET_ADD_LOGISTICS_FORM', clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    u_transfer = st.selectbox('TRANSFER_STATUS:', options=TRANS_LIST, key="add_transfer")
                    u_from_location = st.selectbox('FROM_LOCATION:', options=MAPPED_LOCATIONS_POOL, key="add_from_loc")
                    g_code = st.text_input('G-CODE Identifier:', value='', key="add_gcode")
                with col2:
                    u_serial = st.text_input('SERIAL_NO:', value='', key="add_serial")
                    u_manuf_date = st.date_input('MANUF_YR:', min_value=min_date, max_value=max_date, key="add_manuf")
                    u_service_yr = st.date_input('KOC_SERVICE_YR:', min_value=min_date, max_value=max_date,
                                                 key="add_service")
                with col3:
                    u_run_hr = st.number_input('RUN_HRS LOG:', min_value=0, key="add_run_hrs")
                    u_appr_kva = st.number_input('APPR_KVA:', min_value=0, key="add_appr")
                    u_user = st.selectbox('ASSIGNED USER:', options=USER_LIST, key="add_user")

                m_col_left, m_col_right = st.columns([1, 3])
                with m_col_left:
                    u_move_date = st.date_input('MOVE_DATE:', min_value=min_date, max_value=max_date, key="add_move_dt")
                with m_col_right:
                    u_reason = st.text_area("REASON / REMARKS:", value='', key="add_reason", height=68)

                if st.form_submit_button("SAVE NEW ASSET TO DATABASE", use_container_width=True):
                    if not g_code.strip():
                        st.error("❌ Database validation rejected: G-CODE field cannot be blank.")
                    else:
                        new_data = {
                            'TRANSFER_STATUS': u_transfer if u_transfer != '----' else None,
                            'FIELD': u_field if u_field != '----' else None,
                            'AREA': u_area if u_area != '----' else None,
                            'TO_LOCATION': u_location if u_location != '----' else None,
                            'FROM_LOCATION': u_from_location if u_from_location != '----' else None,
                            'G-CODE': g_code.strip().upper(),
                            'SERIAL_NO': u_serial.strip().upper(),
                            'MODEL': u_model if u_model != '----' else None,
                            'TYPE': u_type if u_type != '----' else None,
                            'GEN_KVA': u_kva,
                            'MANUF_YR': u_manuf_date.isoformat(),
                            'KOC_SERVICE_YR': u_service_yr.isoformat(),
                            'RUN_HRS': u_run_hr,
                            'APPR_KVA': u_appr_kva,
                            'USER': u_user if u_user != '----' else None,
                            'MOVE_DATE': u_move_date.isoformat(),
                            'REASON': u_reason,
                        }
                        try:
                            supabase.table("ASSETS").insert(new_data).execute()
                            st.success(f"🎉 Asset '{g_code.upper()}' recorded successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as err:
                            st.error(f"Supabase Transmission Error: {err}")

        with tab3:
            st.subheader("Modify Existing Field Asset")
            if not df.empty:
                asset_options = sorted(df['G-CODE'].dropna().unique().tolist())
                selected_gcode = st.selectbox("Select Asset G-CODE to Update:", options=asset_options,
                                              key="select_gcode_updater")

                with st.spinner(f"Retrieving live record for {selected_gcode}..."):
                    try:
                        live_res = supabase.table("ASSETS").select("*").eq("G-CODE", selected_gcode).execute()
                        if live_res.data:
                            asset_row = live_res.data[0]
                        else:
                            st.error(f"Asset {selected_gcode} could not be located.")
                            st.stop()
                    except Exception as db_err:
                        st.error(f"Failed to fetch live asset data: {db_err}")
                        st.stop()


                def get_index(opt_list, val):
                    v = str(val).strip() if pd.notna(val) and val is not None else '----'
                    return opt_list.index(v) if v in opt_list else 0


                st.markdown("##### Dynamic Operational Cascade Routing Workflow")
                up_cascade_col1, up_cascade_col2, up_cascade_col3 = st.columns(3)

                with up_cascade_col1:
                    db_field = asset_row.get('FIELD', '----')
                    up_field = st.selectbox('Modify FIELD Registry:', options=LIVE_FIELD_OPTIONS,
                                            index=get_index(LIVE_FIELD_OPTIONS, db_field),
                                            key=f"up_field_cascade_{selected_gcode}")
                with up_cascade_col2:
                    up_field_matched_df = routing_df[
                        routing_df['field_name'] == up_field] if up_field != '----' else pd.DataFrame()
                    UP_ALLOWED_AREAS = ['----'] + sorted(
                        up_field_matched_df['area_name'].unique().tolist()) if not up_field_matched_df.empty else [
                        '----']
                    db_area = asset_row.get('AREA', '----')
                    up_area = st.selectbox('Modify AREA Registry:', options=UP_ALLOWED_AREAS,
                                           index=get_index(UP_ALLOWED_AREAS, db_area),
                                           key=f"up_area_cascade_{selected_gcode}")
                with up_cascade_col3:
                    up_area_matched_df = up_field_matched_df[
                        up_field_matched_df['area_name'] == up_area] if up_area != '----' else pd.DataFrame()
                    UP_ALLOWED_LOCATIONS = ['----'] + sorted(
                        up_area_matched_df['location_name'].unique().tolist()) if not up_area_matched_df.empty else [
                        '----']
                    db_loc = asset_row.get('TO_LOCATION', '----')
                    up_location = st.selectbox('Modify TO_LOCATION Registry:', options=UP_ALLOWED_LOCATIONS,
                                               index=get_index(UP_ALLOWED_LOCATIONS, db_loc),
                                               key=f"up_to_loc_cascade_{selected_gcode}")

                st.markdown("---")
                lock_engine_specs = asset_row.get('TRANSFER_STATUS') in ["DISPATCH", "RECEIVED", "INTERNAL-SHIFT"]

                db_type = asset_row.get('TYPE', '----')
                db_model = asset_row.get('MODEL', '----')
                db_kva = int(asset_row.get('GEN_KVA', 0)) if asset_row.get('GEN_KVA') is not None else 0

                type_key = f"form_type_{selected_gcode}"
                model_key = f"form_model_{selected_gcode}"

                if type_key not in st.session_state:
                    st.session_state[type_key] = db_type if db_type in TYPE_LIST else '----'
                current_type = st.session_state[type_key]
                up_filtered = mappings_df[
                    mappings_df['type'] == current_type] if current_type != '----' else pd.DataFrame()
                up_allowed_models = ['----'] + sorted(
                    up_filtered['model'].unique().tolist()) if not up_filtered.empty else ['----']

                if model_key not in st.session_state:
                    st.session_state[model_key] = db_model if (
                                current_type == db_type and db_model in up_allowed_models) else '----'

                with st.form(key=f"ASSET_UPDATE_FORM_GROUP_{selected_gcode}"):
                    st.markdown("##### Configuration Fields")
                    config_col1, config_col2, config_col3 = st.columns(3)
                    with config_col1:
                        up_type = st.selectbox('Manufacturer TYPE:', options=TYPE_LIST,
                                               index=TYPE_LIST.index(st.session_state[type_key]), key=type_key,
                                               disabled=lock_engine_specs)
                    with config_col2:
                        up_model = st.selectbox('Engine MODEL:', options=up_allowed_models,
                                                index=up_allowed_models.index(st.session_state[model_key]),
                                                key=model_key, disabled=lock_engine_specs)
                    with config_col3:
                        up_matched = up_filtered[
                            up_filtered['model'] == up_model] if up_model != '----' else pd.DataFrame()
                        fallback_kva = int(up_matched.iloc[0]['kva']) if not up_matched.empty else 0
                        initial_kva = db_kva if (up_type == db_type and up_model == db_model) else fallback_kva
                        up_kva = st.number_input('Assigned Rating (KVA):', min_value=0, value=initial_kva, step=10,
                                                 key=f"up_kva_widget_{selected_gcode}", disabled=lock_engine_specs)

                    st.markdown("---")
                    st.markdown("##### Independent Tracking Variables & Deployment Metrics")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        up_transfer = st.selectbox('TRANSFER_STATUS Workflow:', options=TRANS_LIST,
                                                   index=get_index(TRANS_LIST, asset_row.get('TRANSFER_STATUS')),
                                                   key=f"up_trans_status_{selected_gcode}")
                        up_user = st.selectbox('USER assignment:', options=USER_LIST,
                                               index=get_index(USER_LIST, asset_row.get('USER')),
                                               key=f"up_user_{selected_gcode}")

                        PURPOSE_LIST = ['----', 'REPLACEMENT', 'NEW INSTALLATION', 'OFF-HIRE BACKLOAD']
                        db_purpose = str(asset_row.get('PURPOSE', '')).strip().upper()
                        up_purpose = st.selectbox(
                            'Deployment PURPOSE:',
                            options=PURPOSE_LIST,
                            index=PURPOSE_LIST.index(db_purpose) if db_purpose in PURPOSE_LIST else 0,
                            key=f"up_purpose_{selected_gcode}"
                        )

                    with col2:
                        up_from_location = st.selectbox('FROM_LOCATION profile:', options=MAPPED_LOCATIONS_POOL,
                                                        index=get_index(MAPPED_LOCATIONS_POOL,
                                                                        asset_row.get('FROM_LOCATION')),
                                                        key=f"up_from_loc_{selected_gcode}")
                        up_serial = st.text_input('SERIAL_NO verification:',
                                                  value=str(asset_row.get('SERIAL_NO', '')) if asset_row.get(
                                                      'SERIAL_NO') is not None else '',
                                                  key=f"up_serial_{selected_gcode}", disabled=lock_engine_specs)
                        try:
                            current_appr_kva = int(float(asset_row.get('APPR_KVA', 0)))
                        except:
                            current_appr_kva = 0
                        up_appr_kva = st.number_input('APPR_KVA verification:', min_value=0, value=current_appr_kva,
                                                      key=f"up_appr_{selected_gcode}", disabled=lock_engine_specs)

                        try:
                            current_crew = int(float(asset_row.get('CREW', 0)))
                        except:
                            current_crew = 0
                        up_crew = st.number_input(
                            'CREW Count Allocated:',
                            min_value=0,
                            value=current_crew,
                            step=1,
                            key=f"up_crew_{selected_gcode}"
                        )

                    with col3:
                        def safe_date(val):
                            if pd.isna(val) or not val: return max_date
                            if isinstance(val, (datetime, date)): return val
                            try:
                                return datetime.strptime(str(val).split()[0], "%Y-%m-%d").date()
                            except:
                                return max_date


                        up_manuf_date = st.date_input('MANUF_YR:', value=safe_date(asset_row.get('MANUF_YR')),
                                                      key=f"up_manuf_{selected_gcode}", disabled=lock_engine_specs)
                        up_service_yr = st.date_input('KOC_SERVICE_YR:',
                                                      value=safe_date(asset_row.get('KOC_SERVICE_YR')),
                                                      key=f"up_service_{selected_gcode}", disabled=lock_engine_specs)
                        try:
                            current_run_hrs = int(float(asset_row.get('RUN_HRS', 0)))
                        except:
                            current_run_hrs = 0
                        up_run_hr = st.number_input('RUN_HRS:', min_value=0, value=current_run_hrs,
                                                    key=f"up_run_hrs_{selected_gcode}")
                        up_move_date = st.date_input('MOVE_DATE:', value=safe_date(asset_row.get('MOVE_DATE')),
                                                     key=f"up_move_dt_{selected_gcode}")

                        try:
                            current_gc = int(float(asset_row.get('GC', 0)))
                        except:
                            current_gc = 0
                        up_gc = st.number_input(
                            'GC Fields:',
                            min_value=0,
                            value=current_gc,
                            step=1,
                            key=f"up_gc_{selected_gcode}"
                        )

                    st.markdown("---")
                    up_reason = st.text_area("REASON / TRANSFER REMARKS:",
                                             value=str(asset_row.get('REASON', '')) if asset_row.get(
                                                 'REASON') is not None else '', key=f"up_reason_{selected_gcode}")

                    if st.form_submit_button("CLICK TO UPDATE ASSET", use_container_width=True,
                                             key=f"up_btn_{selected_gcode}"):
                        if up_run_hr < current_run_hrs:
                            st.error("❌ Updated hours cannot run lower than current data entries.")
                        else:
                            try:
                                before_q = supabase.table("ASSETS").select("*").eq('G-CODE', selected_gcode).execute()
                                old_snapshot = before_q.data[0] if before_q.data else {}
                            except:
                                old_snapshot = {}

                            updated_payload = {
                                'TRANSFER_STATUS': up_transfer if up_transfer != '----' else old_snapshot.get(
                                    'TRANSFER_STATUS'),
                                'FIELD': up_field if up_field != '----' else old_snapshot.get('FIELD'),
                                'AREA': up_area if up_area != '----' else old_snapshot.get('AREA'),
                                'TO_LOCATION': up_location if up_location != '----' else old_snapshot.get(
                                    'TO_LOCATION'),
                                'FROM_LOCATION': up_from_location if up_from_location != '----' else old_snapshot.get(
                                    'FROM_LOCATION'),
                                'SERIAL_NO': up_serial,
                                'MODEL': up_model if up_model != '----' else old_snapshot.get('MODEL'),
                                'TYPE': up_type if up_type != '----' else old_snapshot.get('TYPE'),
                                'GEN_KVA': up_kva,
                                'MANUF_YR': up_manuf_date.isoformat(),
                                'KOC_SERVICE_YR': up_service_yr.isoformat(),
                                'RUN_HRS': up_run_hr,
                                'APPR_KVA': up_appr_kva,
                                'USER': up_user if up_user != '----' else old_snapshot.get('USER'),
                                'MOVE_DATE': up_move_date.isoformat(),
                                'REASON': up_reason,
                                'PURPOSE': up_purpose if up_purpose != '----' else None,
                                'CREW': up_crew,
                                'GC': up_gc
                            }

                            try:
                                supabase.table("ASSETS").update(updated_payload).eq('G-CODE', selected_gcode).execute()
                                after_q = supabase.table("ASSETS").select("*").eq('G-CODE', selected_gcode).execute()
                                new_snapshot = after_q.data[0] if after_q.data else updated_payload

                                log_audit_event(selected_gcode, "UPDATE", str(up_transfer),
                                                f"Advanced runtime parameter metrics: {current_run_hrs:,} -> {up_run_hr:,} hrs.",
                                                old_snapshot, new_snapshot)
                                st.success("Asset successfully synchronized across network registries!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as update_err:
                                st.error(f"Supabase Execution Sync Fault: {update_err}")

        with tab5:
            st.caption("📋 UPDATES REPORT FOR GENSET FIELD SECTIONS:")
            logs_df = get_audit_logs_df()
            if not logs_df.empty:
                logs_df['created_at'] = pd.to_datetime(logs_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')


                def extract_metric(row_json, key_name):
                    if isinstance(row_json, dict) and key_name in row_json:
                        val = row_json[key_name]
                        return val if val is not None and val != "----" else "—"
                    return "—"


                logs_df['From Location'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'FROM_LOCATION'))
                logs_df['To Location'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'TO_LOCATION'))
                logs_df['Reason'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'REASON'))
                logs_df['KVA Rating'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'GEN_KVA'))
                logs_df['Running Hours'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'RUN_HRS'))

                search_gcode = st.text_input("🔍 Quick-Filter Ledger by Asset ID (G-CODE):", placeholder="e.g., G-009",
                                             key="tab5_audit_ledger_search").strip().upper()
                filtered_df = logs_df[logs_df['g_code'].str.upper().str.contains(search_gcode,
                                                                                 na=False)] if search_gcode else logs_df.copy()

                display_df = filtered_df.rename(columns={'created_at': 'Timestamp', 'changed_by': 'Login Credentials',
                                                         'g_code': 'Asset ID (G-CODE)', 'action_type': 'Action'})
                target_columns = ['Timestamp', 'Asset ID (G-CODE)', 'From Location', 'To Location', 'Running Hours',
                                  'Reason', 'KVA Rating', 'Login Credentials']

                designed_logs_df = display_df[target_columns].style.apply(style_zebra_rows, axis=None)
                st.dataframe(designed_logs_df, use_container_width=True, hide_index=True)
            else:
                st.info("No audit transactions logged inside tracking structures yet.")

    # =====================================================================
    # 3. SETTINGS MATRIX PLATFORM
    # =====================================================================
    elif navigation_target == "SETTINGS":
        st.title("⚙️ System Operational Settings Configuration")
        cfg_tab1, cfg_tab2, cfg_tab3, cfg_tab4 = st.tabs(
            ["Active Models Mapping", "Upsert Model Profiles", "🛠️ MANAGE FIELD LOGISTICS REGISTRIES", "USER UPDATE"])

        with cfg_tab1:
            st.caption("Active Mapping Rules Matrix (Loaded from Database)")
            if not mappings_df.empty:
                st.dataframe(mappings_df[['type', 'model', 'kva']], use_container_width=True, hide_index=True)

        with cfg_tab2:
            st.subheader("Manage Specifications Matrix Rule")
            with st.form("EDIT_MAPPING_MATRIX_FORM", clear_on_submit=True):
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    cfg_type = st.text_input("Manufacturer Type Name (e.g., PERKINS):").strip().upper()
                with m_col2:
                    cfg_model = st.text_input("Engine Model Code (e.g., 2506A):").strip().upper()
                with m_col3:
                    cfg_kva = st.number_input("Standard Default KVA Rating:", min_value=0, value=100, step=10)

                if st.form_submit_button("UPSERT CONFIGURATION PROFILE"):
                    if not cfg_type or not cfg_model:
                        st.error("Both Parameters are required.")
                    else:
                        try:
                            supabase.table("asset_mappings").upsert(
                                {"type": cfg_type, "model": cfg_model, "kva": cfg_kva},
                                on_conflict="type,model"
                            ).execute()
                            st.success("Matrix rule updated successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to apply matrix update: {e}")

        with cfg_tab3:
            st.subheader("Dynamic Field/Area/Location Cascading Matrix Registry")
            st.caption("Add or delete options mapping paths to configure dropdown availability parameters seamlessly.")

            st.markdown("##### Active Logistical Configuration Routing Path Ledger:")
            if not routing_df.empty:
                display_routing = routing_df.copy().rename(
                    columns={'field_name': 'FIELD Option', 'area_name': 'AREA Option',
                             'location_name': 'TO_LOCATION Option'})
                st.dataframe(display_routing[['id', 'FIELD Option', 'AREA Option', 'TO_LOCATION Option']],
                             use_container_width=True, hide_index=True)
            else:
                st.info("No cascading routing rules generated inside database structures yet.")

            st.markdown("---")
            act_col1, act_col2 = st.columns(2)

            with act_col1:
                st.markdown("➕ **Inject New Cascading Route Validation Options**")
                with st.form("ADD_NEW_FIELD_ROUTE_FORM", clear_on_submit=True):
                    in_field = st.text_input("Target FIELD Identifier Name:",
                                             placeholder="e.g., SABRIYA_YARD").strip().upper()
                    in_area = st.text_input("Target AREA Identifier Code:", placeholder="e.g., SBY").strip().upper()
                    in_loc = st.text_input("Target TO_LOCATION Identifier Node:",
                                           placeholder="e.g., MN-0025").strip().upper()

                    if st.form_submit_button("REGISTER ROUTE PATH OPTION", use_container_width=True):
                        if not in_field or not in_area or not in_loc:
                            st.error("Validation Halt: All path node identities must be completely specified.")
                        else:
                            try:
                                supabase.table("field_routing_matrix").insert(
                                    {"field_name": in_field, "area_name": in_area, "location_name": in_loc}).execute()
                                st.success(
                                    f"Successfully pinned structural logistics pathway path entry node layout mapping!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Failed to record logistical pathway matrix configuration payload: {ex}")

            with act_col2:
                st.markdown("🗑️ **Prune Existing Matrix Route Profile**")
                if not routing_df.empty:
                    routing_df['label_str'] = "FIELD: " + routing_df['field_name'] + " ➡️ AREA: " + routing_df[
                        'area_name'] + " ➡️ LOC: " + routing_df['location_name']
                    id_map = dict(zip(routing_df['label_str'], routing_df['id']))

                    selected_route_str = st.selectbox("Select Target Path Sequence Configuration to Purge:",
                                                      options=sorted(id_map.keys()), key="route_purge_selectbox")
                    target_route_id = id_map[selected_route_str]

                    if st.button("🔥 DISMANTLE SPECIFIED LOGISTICAL PATHWAY", use_container_width=True):
                        try:
                            supabase.table("field_routing_matrix").delete().eq("id", int(target_route_id)).execute()
                            st.success(
                                "Logistical pathway component successfully dropped out of database configuration profiles!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Purge Execution Denied: {ex}")
                else:
                    st.info("No routing matrices available to drop.")

        with cfg_tab4:
            with st.expander("USER SETTINGS", expanded=True):
                st.subheader("⚙️ User Assignment Registry Control")
                st.caption("Add or decommission asset operators/users without modifying application source code.")

                reg_col1, reg_col2 = st.columns(2)

                with reg_col1:
                    st.markdown("##### Add New Registry Entry")
                    new_reg_user = st.text_input("Operator / User Name:", key="new_user_reg_input").strip().upper()
                    if st.button("➕ Register User", use_container_width=True):
                        if not new_reg_user or new_reg_user == '----':
                            st.warning("Please type a valid user identification string.")
                        else:
                            try:
                                supabase.table("USER_REGISTRY").insert({'user_name': new_reg_user}).execute()
                                st.success(f"'{new_reg_user}' integrated successfully!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as err:
                                st.error(f"Failed to write record: {err}")

                with reg_col2:
                    st.markdown("##### Delete Registry Entry")
                    # Force dynamic evaluation from dynamic function context
                    current_live_users = load_user_registry()
                    deletion_options = [u for u in current_live_users if u != '----']
                    user_to_delete = st.selectbox("Select User to Remove:", options=deletion_options,
                                                  key="delete_user_reg_select")

                    if st.button("❌ Drop User Profile", use_container_width=True):
                        if user_to_delete:
                            try:
                                supabase.table("USER_REGISTRY").delete().eq('user_name', user_to_delete).execute()
                                st.success(f"'{user_to_delete}' purged from central systems.")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as err:
                                st.error(f"Failed to drop database link: {err}")

    # =====================================================================
    # 4. SYSTEM ADMINISTRATIVE AUDIT MONITOR LOGS
    # =====================================================================
    elif navigation_target == "AUDIT LOGS":
        st.title("⚙️ System Administrative Control Settings")
        logs_df = get_audit_logs_df()

        if not logs_df.empty:
            logs_df['created_at'] = pd.to_datetime(logs_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')


            def extract_metric(row_json, key_name):
                if isinstance(row_json, dict) and key_name in row_json:
                    val = row_json[key_name]
                    return val if val is not None and val != "----" else "—"
                return "—"


            logs_df['From Location'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'FROM_LOCATION'))
            logs_df['To Location'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'TO_LOCATION'))
            logs_df['Reason'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'REASON'))
            logs_df['KVA Rating'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'GEN_KVA'))
            logs_df['Running Hours'] = logs_df['new_values'].apply(lambda x: extract_metric(x, 'RUN_HRS'))

            search_gcode = st.text_input("🔍 Quick-Filter Ledger by Asset ID (G-CODE):", placeholder="e.g., G-009",
                                         key="standalone_audit_ledger_search").strip().upper()
            filtered_df = logs_df[
                logs_df['g_code'].str.upper().str.contains(search_gcode, na=False)] if search_gcode else logs_df.copy()

            display_df = filtered_df.rename(
                columns={'created_at': 'Timestamp', 'changed_by': 'Login Credentials', 'g_code': 'Asset ID (G-CODE)',
                         'action_type': 'Action'})
            target_columns = ['Timestamp', 'Asset ID (G-CODE)', 'From Location', 'To Location', 'Running Hours',
                              'Reason', 'KVA Rating', 'Login Credentials']

            designed_logs_df = display_df[target_columns].style.apply(style_zebra_rows, axis=None)
            st.dataframe(designed_logs_df, use_container_width=True, hide_index=True)
        else:
            st.info("No audit transactions logged inside tracking structures yet.")

        st.markdown("---")
        st.error("⚠️ CRITICAL ADMINISTRATIVE ACTIONS: PURGE ENGINE AUDIT LEDGER")

        purge_mode = st.radio(
            "Select Purge Strategy:",
            options=["Retain Recent Logs (By Date)", "💥 COMPLETE SYSTEM WIPE (Delete Everything Automatically)"],
            index=0,
            key="admin_purge_strategy_choice_standalone"
        )

        purge_all_flag = False
        retention_days = 30

        if "Retain Recent Logs" in purge_mode:
            retention_days = st.number_input(
                "Select Log Retention Window (Days to Keep):",
                min_value=1, max_value=365, value=30, step=1,
                key="admin_retention_days_input_standalone"
            )
        else:
            purge_all_flag = True
            st.warning(
                "‼️ WARNING: Choosing this option will erase every row in the AUDIT_LOGS table. This action is permanent.")

        confirm_purge = st.checkbox("I explicitly authorize the irreversible destruction of these data registries.",
                                    value=False, key="ui_lock_purge_gate_standalone")

        if st.button("🔥 EXECUTE SYSTEM PURGE MANDATE", use_container_width=True, disabled=not confirm_purge,
                     key="execute_purge_btn_standalone"):
            with st.spinner("Wiping database tracking logs..."):
                purge_result = delete_old_audit_logs(days_retention=retention_days, purge_all=purge_all_flag)
                if purge_result["status"] == "success":
                    st.cache_data.clear()
                    st.success(f"Successfully cleared out {purge_result['row_count']} logs from the database!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Purge process failure: {purge_result.get('message')}")

    # =====================================================================
    # 5. UNIMPLEMENTED PLACEHOLDER ROUTING TARGETS
    # =====================================================================
    elif navigation_target == "WORKSHOP":
        st.info("Workshop processing terminal interface modules pending development configurations.")
    elif navigation_target == "STORES & PARTS":
        st.info("Stores and raw components logistics management ledger pending implementation sync.")
    elif navigation_target == "MAINTENANCE":
        st.info("Maintenance schedules workflow manager pending engineering configuration.")
    elif navigation_target == "FLEET MANAGEMENT":
        st.info("Fleet operational telemetry maps overview profiles pending compilation.")
    elif navigation_target == "REMOTE TELEMETRY":
        st.info("Scada/IoT streaming pipeline processing endpoints interface metrics offline.")
    elif navigation_target == "REPORTS":
        st.info("System reports compilation generation platform routing setup offline.")