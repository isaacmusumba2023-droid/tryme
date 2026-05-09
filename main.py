import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from supabase import create_client
from datetime import datetime
import os


#page setting to

st.markdown(
    """
    <style>
        /* Remove padding from the main block-container */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        /* Specifically target the header to remove its height if not needed */
        header {
            visibility: hidden;
            height: 0px;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.set_page_config(
    initial_sidebar_state="expanded",
)
# 1. Initialize the login state if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

users = {
    "ISAAC":"1234isaac",
    "CHRISTOPHER":"5467chris",
    "MICHEAL":"8910mich"
}

# 2. Check if the user is logged in
if not st.session_state['logged_in']:
    # --- THIS IS THE LOGIN PAGE ---
    with st.container():
        with st.form(key="login_form", clear_on_submit=True):
            st.info("WELCOME TO REAL TIME ASSETS MANAGEMENT")
            name_1 = st.text_input("Enter your name").upper()  # Force uppercase to match dict
            passwd_1 = st.text_input("Enter password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if name_1 in users and users[name_1] == passwd_1:
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = name_1
                    st.rerun()  # Refresh the app to show the main program
                else:
                    st.error("Invalid credentials")
else:
    # --- THIS IS YOUR ACTUAL PROGRAM ---
    st.sidebar.write(f"Welcome to Genset field operations , {st.session_state['user_name']}!")
    #main code
    st.set_page_config(
        page_title="field options",
        page_icon="home.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # connection to supabase

    SUPABASE_URL = "https://zakswtxavrnvghpypmuz.supabase.co"
    SUPABASE_KEY = "sb_publishable_a0FSAnDcjWOpzLkYNDCwfg_moO6MV9A"
    TABLE_NAME = "GENSET ASSET"


    # calling style.css
    def local_css(file_name):
        if os.path.exists(file_name):
            with open(file_name) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


    local_css("style.css")
    # loading values
    g_code = ["G-002", "G-003", "G-004", "G-006", "G-007", "G-008", "G-009", "G-011", "G-012", "G-013", "G-014",
              "G-015", "G-017", "G-018", "G-019"
        , "G-020", "G-021", "G-022", "G-023", "G-024", "G-026", "G-027", "G-028", "G-029", "G-030"]
    MDL = ["3406", "3412", "C13", "C15", "C18", "C3.3", "CUMMINS", "TAD-1342GE", "TAD-1343GE", "TAD-1344GE",
           "TAD-1641GE", "TAD-532GE",
           "TAD-734GE", "TAD-840GE", "TWD-1643GE", "TWD-1645GE"]
    TYP = ["CAT", "VOLVO", "CUMMINS", "BAUDOUIN"]
    AR = ["SK", "EK", "RA"]
    FLD = ["NORTH", "SEK", "WAFRA", "WEST","MISHRIF","WORKSHOP"]
    ZR = ["ESP-KOC", "OFF-HIRE", "WORKSHOP", "PDI"]
    # parts sectioned
    cat_make = ['---click here---', 3406, 3412, "C32", "6M16G2DO/S", "6M16G6G4DO/S", "C13", 'C15', 'C18', 'C3.2']
    cat_kva = ['---click here---', 60, 100, 135, 200, 201, 250, 320, 400, 500, 545, 600, 625, 650, 770, 810, 1100, 1500]
    vol_make = ['---click here---', 'TAD1341GE', 'TAD1342GE', 'TAD1343GE', 'TAD1344GE', 'TAD1641GE', 'TAD1642GE',
                'TAD532GE', 'TAD734GE',
                'TAD840GE', 'TAD841GE', 'TWD1643GE', 'TWD1645GE']
    vol_kva = ['---click here---', 105, 200, 201, 225, 246, 250, 251, 252, 300, 316, 320, 330, 364, 400, 412, 413, 416,
               500, 509, 546, 574, 595, 635, 705]
    cum_make = ['---click here---', 'CUMMINS']
    cum_kva = ['---click here---', 13]
    bau_make = ['---click here---', 'BAUDOUIN']
    bau_kva = ['---click here---', 200, 250]
    CONTRACT_OPTIONS=['--select--','70006301','70005701']
    USER_OPTIONS=['ESP-KOC','JO-ESP','WORKSHOP','PDI','OFF-HIRE','MOBILE','BURGAN YARD','WHSP-POWER','ABDALY FARM',
                  'DESALTER PROJECT','MISHRIF','NEW GENERATOR','FIELD_OP REPAIR','READY']
    # loaded values
    with st.sidebar:
        st.sidebar.image('img.png', width=80)
        selected = option_menu(
            menu_title="GENSET_FIELD",
            options=["OVER_VIEW", "ASSET_FIELD", "PART_NUMBERS", "MATERIALS_PDI", "WORKSHOP", "FLEET MANAGEMENT",
                     "RISK MANAGEMENT", "STORES", "GENERAL_ASSETS"],
            icons=["binoculars", "boxes", "gear-wide-connected", "geo", "tools", "speedometer 2", "radioactive",
                   "bar-chart", "recycle"],
            menu_icon="person-gear",
            default_index=0,
            styles={
                "container": {"background-Color": "#cceeff", "header-font": "algerian"},
                "nav-link": {
                    "font-size": "12px",
                    "text-align": "left",
                    "color": "#000000",
                    "font-weight": "Arial",
                    "margin": "0px",
                    "--hover-color": "#b3d9ff"
                },
                "nav-link-selected": {"background-color": "#b3d9ff"},
            }
        )
    # page setup
    if selected == "ASSET_FIELD":
        st.info("WELCOME TO FIELD_OPERATIONS_ASSETS UPDATES")


        @st.cache_resource
        def init_connection():
            return create_client(SUPABASE_URL, SUPABASE_KEY)


        supabase = init_connection()
        # selections
        menu = ["View Assets", "Filter & Download", "Add New Asset", "Update Asset"]
#        choice = st.selectbox("Menu", menu)
        tab1,tab2,tab3,tab4=st.tabs(["View Assets", "Filter & Download", "Add New Asset", "Update Asset"])



        # help to get data
        def fetch_data():
            response = supabase.table(TABLE_NAME).select("*").execute()
            return pd.DataFrame(response.data)


        # view assets
        with tab1:
            st.subheader("Current Field Assets")
            try:
                df = fetch_data()
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True, height=600)
                    st.info(f"Total Assets: {len(df)}")
                else:
                    st.warning("No assets found in the database.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
        # FILTER$DOWNLOAD
        with tab2:
            st.info("🔍 Filter & Download Assets")
            try:
                df = fetch_data()
                if not df.empty:
#                    st.write("### Apply Filters")
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        # Get unique locations, handling potential None values
                        locations = sorted([str(loc) for loc in df["LOCATION"].unique() if loc is not None])
                        selected_location = st.multiselect("Filter by Location", options=locations)
                    with col_f2:
                        # Get unique users, handling potential None values
                        users = sorted([str(u) for u in df["USER"].unique() if u is not None])
                        selected_user = st.multiselect("Filter by User", options=users)
                    # Apply filters
                    filtered_df = df.copy()
                    if selected_location:
                        filtered_df = filtered_df[filtered_df["LOCATION"].astype(str).isin(selected_location)]
                    if selected_user:
                        filtered_df = filtered_df[filtered_df["USER"].astype(str).isin(selected_user)]
                    st.write("### Filtered Results")
                    st.dataframe(filtered_df, use_container_width=True)
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
                st.error(f"Error fetching data: {e}")
        with tab3:
            st.subheader("Add New Asset")
            with st.form("add_new_asset", clear_on_submit=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    g_code = st.text_input("G-CODE")
                    serial_no = st.text_input("SERIAL_NO")
                    model = st.selectbox("MODEL", options=MDL)
                    asset_type = st.selectbox("TYPE", options=TYP)
                    contract=st.selectbox('CONTRACT_NO :',options=['--select--',70006301,70005701])
                with col2:
                    kva = st.number_input("KVA", min_value=0, step=1)
                    user_id = st.number_input("user_id", min_value=0, step=1)
                    manuf_yr = st.date_input("MANUF_YR")
                    service_yr_koc = st.date_input("SERVICE_YR_KOC")
                with col3:
                    run_hrs = st.number_input("RUN_Hrs", min_value=0, step=1)
                    area = st.selectbox("AREA", options=AR)
                    appr_kva = st.number_input("APPR_KVA", min_value=0, step=1)
                    location = st.text_input("LOCATION")
                    field = st.selectbox("FIELD", options=FLD)
                with col4:
                    user = st.selectbox("USER", options=ZR)
                    crew = st.number_input("CREW", min_value=0, step=1)
                    movement_date = st.date_input("MOVEMENT_DATE")
                    moved_from = st.text_input("MOVED_FROM")
                    reason = st.text_area("REASON")

                submit = st.form_submit_button("Add Asset")

                if submit:
                    # Prepare data for insertion
                    new_data = {
                        "G-CODE": g_code,
                        "SERIAL_NO": serial_no,
                        "MODEL": model,
                        "TYPE": asset_type,
                        "KVA": kva,
                        "user_id": user_id,
                        "CONTRACT_NO": contract,
                        "MANUF_YR": str(manuf_yr),
                        "SERVICE_YR_KOC": str(service_yr_koc),
                        "RUN_Hrs": run_hrs,
                        "AREA": area,
                        "APPR_KVA": appr_kva,
                        "LOCATION": location,
                        "FIELD": field,
                        "USER": user,
                        "CREW": crew,
                        "MOVEMENT_DATE": str(movement_date),
                        "MOVED_FROM": moved_from,
                        "REASON": reason,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    try:
                        response = supabase.table(TABLE_NAME).insert(new_data).execute()
                        st.success("✅ Asset added successfully!")
                    except Exception as e:
                        st.error("❌ Error adding asset")
                        with st.expander("View Error Details"):
                            st.write(f"Type: {type(e).__name__}")
                            st.write(f"Message: {str(e)}")
                            if hasattr(e, 'details'):
                                st.write(f"Details: {e.details}")
        # updating added assets
        with tab4:
            st.subheader("Edit Existing Asset")

            try:
                df = fetch_data()
                if not df.empty:
                    # Select asset to update
                    asset_list = df["G-CODE"].tolist()
                    selected_gcode = st.selectbox("Select G-CODE to update", asset_list)

                    # Get current data for the selected asset
                    asset_data = df[df["G-CODE"] == selected_gcode].iloc[0]

                    with st.form("update_form"):
                        col1, col2,col3= st.columns(3)

                        with col1:
                            current_contract=str(asset_data.get("CONTRACT_NO","--SELECT--"))
                            if current_contract not in CONTRACT_OPTIONS:
                                temp_option=CONTRACT_OPTIONS + [current_contract]
                            else:
                                temp_option=CONTRACT_OPTIONS
                            u_contract = st.selectbox("CONTRACT_NO", options=temp_option,index=temp_option.index(current_contract))

                            u_serial_no = st.text_input("SERIAL_NO", value=str(asset_data.get("SERIAL_NO", "")))

                            u_model = st.text_input("MODEL", value=str(asset_data.get("MODEL", "")))

                            u_type = st.text_input("TYPE", value=str(asset_data.get("TYPE", "")))

                            u_kva = st.number_input("KVA", value=int(asset_data.get("KVA", 0)))

                            u_user_id = st.number_input("user_id", value=int(asset_data.get("user_id", 0)))

                        with col2:

                            # Handle date conversion for Streamlit date_input
                            def parse_date(date_str):
                                try:
                                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                                except:
                                    return datetime.now().date()


                            u_manuf_yr = st.date_input("MANUF_YR", value=parse_date(asset_data.get("MANUF_YR", "")))
                            u_service_yr_koc = st.date_input("SERVICE_YR_KOC",
                                                             value=parse_date(asset_data.get("SERVICE_YR_KOC", "")))
                            u_run_hrs = st.number_input("RUN_Hrs", value=int(asset_data.get("RUN_Hrs", 0)))


                            u_area = st.text_input("AREA", value=str(asset_data.get("AREA", "")))
                            u_appr_kva = st.number_input("APPR_KVA", value=int(asset_data.get("APPR_KVA", 0)))
                            u_location = st.text_input("LOCATION", value=str(asset_data.get("LOCATION", "")))
                        with col3:
                            #adding options for field during update
                            current_field=str(asset_data.get("FIELD", ""))
                            f_options=FLD if current_field in FLD else FLD + [current_field]
                            u_field = st.selectbox("FIELD",options=f_options,index=f_options.index(current_field))

                            #adding select options for USER
                            current_user=str(asset_data.get("USER", ""))
                            u_options=USER_OPTIONS if current_user in USER_OPTIONS else USER_OPTIONS + [current_user]
                            u_user = st.selectbox("USER", options=u_options,index=u_options.index(current_user))
                            #read me again mr.isaac

                            u_crew = st.number_input("CREW", value=int(asset_data.get("CREW", 0)))
                            u_moved_from = st.text_input("MOVED_FROM", value=str(asset_data.get("MOVED_FROM", "")))
                            u_reason = st.text_area("REASON", value=str(asset_data.get("REASON", "")))


                        update_submit = st.form_submit_button("Update Asset")

                        if update_submit:
                            updated_data = {
                                "SERIAL_NO": u_serial_no,
                                "CONTRACT_NO": u_contract,
                                "MODEL": u_model,
                                "TYPE": u_type,
                                "KVA": u_kva,
                                "user_id": u_user_id,
                                "MANUF_YR": str(u_manuf_yr),
                                "SERVICE_YR_KOC": str(u_service_yr_koc),
                                "RUN_Hrs": u_run_hrs,
                                "AREA": u_area,
                                "APPR_KVA": u_appr_kva,
                                "LOCATION": u_location,
                                "FIELD": u_field,
                                "USER": u_user,
                                "CREW": u_crew,
                                "MOVED_FROM": u_moved_from,
                                "REASON": u_reason
                            }

                            try:
                                response = supabase.table(TABLE_NAME).update(updated_data).eq("G-CODE",
                                                                                              selected_gcode).execute()
                                st.success(f"✅ Asset {selected_gcode} updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error("❌ Error updating asset")
                                with st.expander("View Error Details"):
                                    st.write(f"Type: {type(e).__name__}")
                                    st.write(f"Message: {str(e)}")
                                    if hasattr(e, 'details'):
                                        st.write(f"Details: {e.details}")
                else:
                    st.warning("No assets available to update.")
            except Exception as e:
                st.error(f"Error: {e}")

    # DISPLAY MODEL
    elif selected == "OVER_VIEW":
        st.info("OVER ALL DATA & LOCATIONS")
        SUPABASE_URL = "https://zakswtxavrnvghpypmuz.supabase.co"
        SUPABASE_KEY = "sb_publishable_a0FSAnDcjWOpzLkYNDCwfg_moO6MV9A"
        TABLE_NAME = "GENSET ASSET"
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        resource_w = supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,TYPE,KVA,RUN_Hrs,"
                                                           "AREA,LOCATION,MOVED_FROM,REASON").eq('LOCATION',
                                                                                                 'WORKSHOP').execute()
        resource_KOC = supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,TYPE,KVA,RUN_Hrs,"
                                                             "AREA,LOCATION,MOVED_FROM,REASON").eq('USER',
                                                                                                   'ESP-KOC').execute()
        resource_PDI = supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,TYPE,KVA,RUN_Hrs,"
                                                             "AREA,LOCATION,MOVED_FROM,REASON").eq('LOCATION',
                                                                                                   'PDI').execute()
        resourse_use =supabase.table("GENSET ASSET").select("*").eq('USER','NEW GENSET').execute()
        resourse_jo = supabase.table("GENSET ASSET").select("*").eq('USER','JO-ESP').execute()
        resourse_wksp = supabase.table("GENSET ASSET").select("*").eq('USER','WORKSHOP_POWER').execute()
        resourse_mobile = supabase.table("GENSET ASSET").select("*").eq('USER','MOBILE').execute()
        resourse_offhire = supabase.table("GENSET ASSET").select("*").eq('USER','OFF-HIRE').execute()
        resourse_kva= supabase.table("GENSET ASSET").select('*').gte('KVA',200).execute()
        kva_below=supabase.table("GENSET ASSET").select('*').lt('KVA',200).execute()
        ready=supabase.table("GENSET ASSET").select('*').eq('USER','READY').execute()
        burgan=supabase.table("GENSET ASSET").select('*').eq('USER','BURGAN').execute()

        df_WORKSHOP = resource_w.data
        df_KOC = resource_KOC.data
        df_PDI = resource_PDI.data
        df_new=resourse_use.data
        df_jo=resourse_jo.data
        df_wksp=resourse_wksp.data
        df_mobile=resourse_mobile.data
        df_offhire=resourse_offhire.data
        df_kva=resourse_kva.data
        df_below=kva_below.data
        df_ready=ready.data
        df_burgan=burgan.data

        V_1 = len(df_WORKSHOP)
        V_2 = len(df_KOC)
        V_3 = len(df_PDI)
        V_4 = len(df_new)
        V_5 = len(df_jo)
        V_6 = len(df_wksp)
        V_7 = len(df_mobile)
        V_8 = len(df_offhire)
        V_9 = len(df_kva)
        V_10 = len(df_below)
        V_11 = len(df_ready)
        V_12 = len(df_burgan)

        with st.container():
            col1, col2, col3,col4,col5,col6= st.columns(6)
            with col1:
                st.metric('WORKSHOP', V_1, '+',border=True,height=120,delta_color='green')
                st.metric('READY-GENSET',V_11,'+',border=True,height=120,delta_color='green')
            with col2:
                st.metric('ESP-KOC', V_2, '+',border=True,height=120,delta_color='green')
                st.metric('MOBILE', V_7, '+', border=True, height=120, delta_color='green')
            with col3:
                st.metric('UNDER PDI', V_3, '+',border=True,height=120,delta_color='green')
                st.metric('OFF-HIRE', V_8, '+', border=True, height=120, delta_color='green')
            with col4:
                st.metric('NEW_GENSET', V_4, '+',border=True,height=120,delta_color='green')
                st.metric('KVA=>200', V_9, '+', border=True, height=120, delta_color='green')
            with col5:
                st.metric('JO-ESP', V_5, '+',border=True,height=120,delta_color='green')
                st.metric('KVA<200', V_10, '+', border=True, height=120, delta_color='green')
            with col6:
                st.metric('WORKSHOP_POWER', V_6, '+',border=True,height=120,delta_color='green')
                st.metric('BURGAN', V_12, '+', border=True, height=120, delta_color='green')

        "---"
        with st.expander("DATA_VISUALIZATION"):
            # Simple native replacement for your matplotlib block:
            chart_data = pd.DataFrame({
                'Location': ['WORKSHOP', 'ESP-KOC', 'PDI', 'JO-ESP', 'WKSP_POWER'],
                'Quantity': [V_1, V_2, V_3, V_5, V_6]
            })
            st.bar_chart(chart_data, x='Location', y='Quantity', color="#1a8cff")


    elif selected == "PART_NUMBERS":
        st.info("WELCOME TO FIELD_OPERATIONS_PART_NUMBERS MANAGEMENT SYSTEM")
        "----"
        option = ["CATERPILLAR", "VOLVO", "CUMMINS", "BAUDOUIN"]
        selection = st.segmented_control("SELECT_GENSET-TYPE"
                                         , options=option,key="nav_index"
                                         )
        if selection == "CATERPILLAR":
            make_cat = st.selectbox("SELECT_MAKE", options=cat_make)
            if make_cat == cat_make[1]:
                kva_selected = st.selectbox("SELECT_KVA(320)", options=cat_kva)
                if kva_selected == cat_kva[7]:
                    df = {"PARTS": ['WATER PUMP', 'GASKET', 'FUEL TRANSFER PUMP', 'BREATHER', 'BREATHER HOUSING', 'FAN',
                                    'SOLENOID', 'GOVERNOR'
                        , 'PUMP KIT', 'RADIATOR-CAP', 'BALL BEARING', 'SEAL', 'THERMOSTAT', 'FITTINGS', 'FITTINGS',
                                    'OIL FILLING CAP', 'BALL BEARING'],
                          'DESCRIPTION': ['WATER PUMP WITH O-RING', 'GASKET(Thermostat', 'PUMP GP FUEL TRANSFER',
                                          'BREATHER-AS', 'CLAMP-BREATHER HOUSING'
                              , 'FAN', 'SOLENOID-SHUT OFF', 'WOODWARD GOVERNOR', 'KIT-WATER PUMP SPCALSO',
                                          'RADIATOR-CAP', 'BALL BEARING -L'
                              , 'SEAL- LIP TYPE', 'THERMOSTAT', 'PRESSURE RELIFE(1/8-27 PTF)', 'FITTING-GREASE',
                                          'CAP-OIL FILLING', 'BALL BEARING-R'],
                          'PART NO': ['352-0203', '7C-0307', '1W-1700', '9Y-2988', '2N-8109', '142-1931', '1255774',
                                      '1315455', '433-9952'
                              , '153-1403', '3L-1425', '5S-2106', '2477133', '4B-4550', '2D-4867', '6N-2985',
                                      '8H-9789']}
                    st.dataframe(df, height=700)
            elif make_cat == cat_make[7]:
                kva_selected = st.selectbox("SELECT_KVA(500)", options=cat_kva)
                if kva_selected == cat_kva[9]:
                    df = {'PARTS': ['SEAL V-RING', 'SEAL VALVE COVER', 'SEAL TURBO OIL LINE', 'SEAL TURBO LINE',
                                    'THERMOSTAT HOUSING SEAL', 'SEAL O-RING'
                        , 'SEAL O-RING', 'SEAL LIP TYPE', 'WATER PUMP', 'O-RING(W/P)', 'PRIMING PUMP', 'PUMP GP',
                                    'FUEL HOSE', 'FUEL HOSE'
                        , 'BALL BEARING', 'BALL BEARING', 'BALL BEARING', 'SPIDER', 'CHECK VALVE', 'FUEL BYPASS VALVE',
                                    'FUEL FILTER HOUSING'
                        , 'GASKET', 'RADIATOR CAP', 'RADIATOR CAP', 'THERMOSTAT O-RING', 'RADIATOR HOSE-B',
                                    'RADIATOR HOSE-T', 'EXPANSION TANK'
                        , 'GASKET-TURBO', 'RELAY', 'BELT TIGHTENER', 'PWM-CONTROL', 'ENGINE ECM', 'EYE ROD ADJUSTER',
                                    'EXHAUST BELLOW CLAMP'
                        , 'ALTERNATOR PULLEY', 'TURBO HIGH TEMP BOLT', 'TURBO HIGH TEMP NUT', 'AIR HOSE', 'STRAP'],
                          'DESCRIPTION': ['SEAL V-RING', 'SEAL VALVE COVER(TAPPET COVER)', 'SEAL TURBO OIL LINE',
                                          'SEAL TURBO LINE', 'THERMOSTAT HOUSING SEAl',
                                          'FUEL PUMP O-RING', 'SEAL O-RING', 'SEAL LIP TYPE',
                                          'WATER PUMP WITHOUT GASKET', 'O-RING(WATER PUMP)', 'PRIMING PUMP',
                                          'FUEL TRANSFER PUMP GP', 'FUEL SEPERATOR TO FUEL PUMP', 'F.PUMP TO F.FILTER',
                                          'BALL BEARING-H', 'BALL BEARING-L',
                                          'FOR BELT TIGHTENER*2', 'FAN UNIT SPIDER', 'CHECK VALVE', 'FUEL BYPASS VALVE',
                                          'FUEL FILTER HOUSING',
                                          'TAPPET PRESSURE PLATE GASKET', 'RADIATOR CAP', 'RADIATOR CAP C51',
                                          'THERMOSTAT O-RING',
                                          'RADIATOR RUBBER HOSE-BOTTOM', 'RADIATOR HOSE TOP', 'RADIATOR TANK',
                                          'TURBO CHARGER GASKET', 'RELAY'
                              , 'BELT TIGHTENER (FAN PULLEY)', 'CONTROL GROUP', 'ENGINE ECM', 'ROD-ALTERNATOR',
                                          'EXHAUST BELLOW CLAMP', 'ALTERNATOR PULLEY',
                                          'TURBO HIGH TEMP BOLT', 'TURBO HIGH TEMP NUT', 'AIR HOSE', 'STRAP'],
                          'PART NO': ['8C-5238', '2429537', '198-6068', '160-7037', '3S-9643', '107-5769', '9F-4446',
                                      '5S-2106', '10R-8660', '4687363',
                                      '137-5541', '384-8612', '7N-4045', '1-meter hose', '8H-9789', '3L-1425',
                                      '297-4677', '217-6022', '2812725'
                              , '139-6873', '191-5055', '272-0390', '266-8550', '391-6399', '167-4407', '264-7112',
                                      '264-7111'
                              , '4616246', '1S-4295', '3E-6477', '309-8037', '5125720', '20R-8181', '6L-5874',
                                      '220-5619', '1W-1456'
                              , '2N-2765', '2N-2766', '286-0607', '248-7330']}
                    st.dataframe(df, hide_index=True, height=700)
            elif make_cat == cat_make[2]:
                kva_selected = st.selectbox("SELECT_KVA(810)", options=cat_kva)
                if kva_selected == cat_kva[15]:
                    df = {'PARTS': ['FUEL PUMP', 'FUEL LINE-1 RR', 'FUEL LINE-2 RR', 'FUEL LINE-3 RR', 'FUEL LINE-4 RR',
                                    'FUEL LINE-5 RR', 'FUEL LINE-6 RR', 'FUEL LINE-1 LR', 'FUEL LINE-2 LR',
                                    'FUEL LINE-3 LR',
                                    'FUEL LINE-4 LR', 'FUEL LINE-5 LR', 'FUEL LINE-6 LR', 'EXHAUST BELLOW', 'SEAL',
                                    'BEARING'],
                          'DESCRIPTION': ['FUEL PUMP', 'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR',
                                          'RIGHT FROM RADIATOR',
                                          'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR',
                                          'LEFT FROM RADIATOR',
                                          'LEFT FROM RADIATOR', 'LEFT FROM RADIATOR', 'LEFT FROM RADIATOR',
                                          'LEFT FROM RADIATOR',
                                          'LEFT FROM RADIATOR', 'EXHAUST BELLOW (G-510,513)', 'SEAL O-RING',
                                          'BALL-BEARING']
                        , 'PART NO': ['105-7573', '4P-9641', '4P-9643', '4P-9645', '4P-9647', '4P-9649', '4P-9651',
                                      '111-4122', '111-4124', '111-4126', '111-4128', '111-4130', '111-4132',
                                      '211-1009',
                                      '9F-4446', '8H-9789']}
                    st.dataframe(df, hide_index=True, height=700)
            elif make_cat == cat_make[6]:
                kva_selected = st.selectbox("SELECT_KVA(400)", options=cat_kva)
                if kva_selected == cat_kva[8]:
                    df = {
                        'PARTS': ['THERMOSTAT', 'THERMOSTAT O-RING TOP', 'THERMOSTAT O-RING BOTTOM', 'THERMOSTAT VENT',
                                  'THERMOSTAT O-RING SIDE'
                            , 'BALL BEARING-L', 'SEAL', 'BALL BEARING-H', 'SEAL', 'FITTINGS', 'PULLY-ALT',
                                  'FUEL TRNS PUMP',
                                  'WATER PUMP'
                            , 'OIL FILLING CAP', 'EXHAUST BELLOW', 'BALL BEARING-TENSOR', 'BELT TIGHTENER'],
                        'DESCRIPTION': ['THERMOSTAT', 'THERMOSTAT TOP', 'THERMOSTAT BOTTOM', 'THERMOSTAT VENT',
                                        'THERMOSTAT O-RING SIDE', 'BALL BEARING-L'
                            , 'SEAL LIP TYPE', 'BALL BEARING-H', 'SEAL O-RING', 'FITTING-GREASE', 'ALTERNATOR-PULLY',
                                        'FUEL TRANSFER PUMP GP', 'WATER PUMP GP'
                            , 'CAP-AS OIL FILLING', 'EXHAUST BELLOW', 'BALL BEARING FOR BELT TIGHTENER',
                                        'BELT TIGHTENER GP (FAN PULLEY'],
                        'PART NO': ['247-7133', '3S-9643', '227-5075', '239-8135', '7L-6580', '3L-1425', '5S-2106',
                                    '8H-9789', '9F-4446'
                            , '2D-4867', '296-8176', '384-8611', '352-0205', '068-4497', '227-3019', '297-4677',
                                    '309-8037']}
                    st.dataframe(df, hide_index=True, height=700)
            elif make_cat == cat_make[8]:
                kva_selected = st.selectbox("SELECT_KVA(600)", options=cat_kva)
                if kva_selected == cat_kva[11]:
                    dt = {'PARTS': ['OIL FILING CAP', 'SEAL', 'FAN SPIDER', 'BALL BEARING', 'WATER PUMP',
                                    'WATER PUMP KIT', 'TAPPET COVER SEAL'
                        , 'BELT TIGHTENER GP', 'BELT TENSIONER BEARING', 'EXHAUST BELLOW'],
                          'DESCRIPTION': ['OIL FILING CAP', 'SEAL V-RING', 'SPIDER -ASSY FAN', 'BALL BEARING',
                                          'WATER PUMP WITHOUT GASKET',
                                          'O-RING KIT', 'SEAL-VALVE (Tappet cover)', 'BELT TIGHTENER GP(FAN PULLEY)',
                                          'BALL BEARING FOR BELT TIGHTENER GP',
                                          'EXHAUST BELLOW'],
                          'PART NO': ['5L-2952', '8C-5238', '217-6022', '333-2408', '10R-8660', '4687363', '2429537',
                                      '309-8037', '297-4677',
                                      '227-3019'], }
                    st.dataframe(dt, hide_index=True, height=700)
            elif make_cat == cat_make[9]:
                kva_selected = st.selectbox("SELECT_KVA(60)", options=cat_kva)
                if kva_selected == cat_kva[1]:
                    df = {'PARTS': ['WATER PUMP', 'GASKET', 'INJECTOR HOSE', 'COOLANT PIPE', 'OIL COOLER TUBE',
                                    'OIL COOLER TUBE'
                        , 'WOODWARD GOVERNOR', 'OIL FILING CAP', 'FUEL HOSE', 'RADIATOR HOSE-INLET',
                                    'RADIATOR HOSE-OUTLET',
                                    'FILTER GP FUEL', 'PUMP GP FUEL TRANSFER'],
                          'DESCRIPTION': ['WATER PUMP GP', 'GASKET(WATER PUMP)', 'INJECTOR HOSE',
                                          'COOLANT PIPE WITH O-RING',
                                          'OIL COOLER TUBE(LOWER)', 'OIL COOLER TUBE(UPPER)', 'WOODWARD GOVERNOR',
                                          'OIL FILING CAP', 'FUEL HOSE',
                                          'RADIATOR HOSE-INLET', 'RADIATOR HOSE-OUTLET', 'FILTER GP FUEL',
                                          'PUMP GP FUEL TRANSFER(HAND)'],
                          'PART NO': ['355-2252', '225-8019', '232-1794', '2744707', '3482V102', '3482V101', '272-2223'
                              , '136-3608', '232-1794', '258-5355', '258-5356', '4668433', '201-0877']}
                    st.dataframe(df, hide_index=True, height=700)
            elif make_cat == cat_make[3]:
                kva = st.selectbox("SELECT_KVA(1100)", options=cat_kva)
                if kva == cat_kva[-2]:
                    df = {'PARTS': ['WATER PUMP', 'WATER PUMP KIT'],
                          'DESCRIPTION': ['WATER PUMP', 'WATER PUMP KIT'],
                          'PART NO': ['352-0202', '434-7542']}
                    st.dataframe(df, hide_index=True, height=700)
            elif make_cat == cat_make[4]:
                kva = st.selectbox("SELECT_KVA(250)", options=cat_kva)
                if kva == cat_kva[6]:
                    df = {"PARTS": [],
                          "DESCRIPTION": [],
                          "PART NO": []}
                    st.dataframe(df, hide_index=True, height=700)


        elif selection == "VOLVO":
            st.selectbox("SELECT_MAKE", options=vol_make)
        elif selection == "CUMMINS":
            st.selectbox("SELECT_MAKE", options=cum_make)
        elif selection == "BAUDOUIN":
            st.selectbox("SELECT_MAKE", options=bau_make)
    elif selected == "WORKSHOP":
        st.info("GENERATORS_UNDER_WORKSHOP")
        SUPABASE_URL = "https://zakswtxavrnvghpypmuz.supabase.co"
        SUPABASE_KEY = "sb_publishable_a0FSAnDcjWOpzLkYNDCwfg_moO6MV9A"
        TABLE_NAME = "GENSET ASSET"
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        resource = supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,TYPE,KVA,RUN_Hrs,"
                                                         "AREA,LOCATION,MOVED_FROM,REASON").eq('LOCATION',
                                                                                               'WORKSHOP').execute()
        df = resource.data
        st.dataframe(df, hide_index=True, height=500)
        D = len(df)
        st.metric('TOTAL NUMBER', D, "+")

    elif selected == "FLEET MANAGEMENT":
        st.info("FLEET_MANAGEMENT AND PLANNING" + ':tractor:')
    elif selected == 'GENERAL_ASSETS':
        st.info("General assets trucking system")
        SUPABASE_URL = "https://zakswtxavrnvghpypmuz.supabase.co"
        SUPABASE_KEY = "sb_publishable_a0FSAnDcjWOpzLkYNDCwfg_moO6MV9A"
        TABLE_NAME = "ASSETs"
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # to read data from table
        response = supabase.table('ASSETS').select("*").execute()
        df = response.data

        st.dataframe(df, use_container_width=True)

        # adding assets
        with st.expander("Add New Asset"):

            with st.form(key="my_form", clear_on_submit=True):
                st.info('ASSET UPLOAD')
                col1, col2 = st.columns(2)
                with col1:
                    nn_1 = st.text_input("Enter Asset Name:")
                    description = st.text_input("Enter Description:")
                    rating = st.text_input("Enter Rating:")
                with col2:
                    location = st.selectbox("Enter Location:", options=['PDI', 'BURGUN', 'WORKSHOP', 'NK', 'EK', 'SK'])
                    quantity = st.number_input("Enter Quantity:", min_value=0, step=1)
                    status = st.selectbox("Select Status:", options=['Active', 'Inactive'])
                submit = st.form_submit_button(label="Submit")
                if submit:
                    if nn_1 != '':
                        new_data = {
                            'ASSET_NAME': nn_1,
                            'DESCRIPTION': description,
                            'RATING': rating,
                            'LOCATION': location,
                            'QUANTITY': quantity,
                            'STATUS': status
                        }
                        response = supabase.table('ASSETS').insert(new_data).execute()
                        st.success(f"Asset {nn_1} has been added")
                    else:
                        st.error("Enter Asset Name")
        with st.expander("Edit uploaded Asset"):

            with st.form(key="my_form_2", clear_on_submit=True):

                st.info('ASSET UPLOAD')
                col1, col2 = st.columns(2)
                with col1:

                    nn_1 = st.text_input("Enter Asset Name:")
                    description = st.text_input("Enter Description:")
                    rating = st.text_input("Enter Rating:")
                with col2:
                    location = st.selectbox("Enter Location:", options=['PDI', 'BURGUN', 'WORKSHOP', 'NK', 'EK', 'SK'])
                    quantity = st.number_input("Enter Quantity:", min_value=0, step=1)
                    status = st.selectbox("Select Status:", options=['Active', 'Inactive'])
                    submit = st.form_submit_button(label="Submit")
                    if submit:
                        if nn_1 != '':
                            new_data = {
                                'ASSET_NAME': nn_1,
                                'DESCRIPTION': description,
                                'RATING': rating,
                                'LOCATION': location,
                                'QUANTITY': quantity,
                                'STATUS': status
                            }
                            response = supabase.table('ASSETS').update(new_data).eq('ASSET_NAME', ['Lst']).execute()
                            st.success(f"Asset {nn_1} has been UPDATED")

#end of code area

    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()