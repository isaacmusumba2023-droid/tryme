import streamlit as st
import pandas as pd
import plotly.express as px

from streamlit_option_menu import option_menu
from supabase import create_client, Client
from datetime import datetime, timedelta
import os



st.set_page_config(
    page_title="field options",
    page_icon="home.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
#connection to supabase

SUPABASE_URL = "https://zakswtxavrnvghpypmuz.supabase.co"
SUPABASE_KEY = "sb_publishable_a0FSAnDcjWOpzLkYNDCwfg_moO6MV9A"
TABLE_NAME = "GENSET ASSET"
# calling style.css
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
#loading values
g_code=["G-002","G-003","G-004","G-006","G-007","G-008","G-009","G-011","G-012","G-013","G-014","G-015","G-017","G-018","G-019"
        ,"G-020","G-021","G-022","G-023","G-024","G-026","G-027","G-028","G-029","G-030"]
MDL=["3406","3412","C13","C15","C18","C3.3","CUMMINS","TAD-1342GE","TAD-1343GE","TAD-1344GE","TAD-1641GE","TAD-532GE",
     "TAD-734GE","TAD-840GE","TWD-1643GE","TWD-1645GE"]
TYP=["CAT","VOLVO","CUMMINS","BAUDOUIN"]
AR=["SK","EK","RA"]
FLD=["NORTH","SEK","WAFRA","WEST"]
ZR=["ESP-KOC","OFF-HIRE","WORKSHOP","PDI"]
#parts sectioned
cat_make=['---click here---',3406,3412,"C32","6M16G2DO/S","6M16G6G4DO/S","C13",'C15','C18','C3.2']
cat_kva=['---click here---',60,100,135,200,201,250,320,400,500,545,600,625,650,770,810,1100,1500]
vol_make=['---click here---','TAD1341GE','TAD1342GE','TAD1343GE','TAD1344GE','TAD1641GE','TAD1642GE','TAD532GE','TAD734GE',
          'TAD840GE','TAD841GE','TWD1643GE','TWD1645GE']
vol_kva=['---click here---',105,200,201,225,246,250,251,252,300,316,320,330,364,400,412,413,416,500,509,546,574,595,635,705]
cum_make=['---click here---','CUMMINS']
cum_kva=['---click here---',13]
bau_make=['---click here---','BAUDOUIN']
bau_kva=['---click here---',200,250]
#loaded values
with st.sidebar:
    st.sidebar.image('img.png', width=80)
    selected=option_menu(
        menu_title="GENSET_FIELD",
        options=["ASSET_FIELD","PART_NUMBERS","MATERIALS_PDI","WORKSHOP","FLEET MANAGEMENT","RISK MANAGEMENT","STORES","GENERAL_ASSETS"],
        icons=["boxes","gear-wide-connected","geo","tools","speedometer 2","radioactive","bar-chart","recycle"],
        menu_icon="person-gear",
        default_index=0,
        styles={
            "container":{"background-Color":"#cceeff","header-font":"algerian"},
            "nav-link":{
                "font-size":"12px",
                "text-align":"left",
                "color":"#000000",
                "font-weight":"Arial",
                "margin":"0px",
                "--hover-color":"#b3d9ff"
            },
            "nav-link-selected":{"background-color":"#b3d9ff"},
        }
    )
#pagesetup
if selected=="ASSET_FIELD":
    st.info("WELCOME TO FIELD_OPERATIONS_ASSETS UPDATES")
    "---"
    @st.cache_resource
    def init_connection():
        return create_client(SUPABASE_URL, SUPABASE_KEY)


    supabase = init_connection()
    #selections
    menu = ["View Assets", "Filter & Download", "Add New Asset", "Update Asset"]
    choice = st.selectbox("Menu", menu)
    #help to get data
    def fetch_data():
        response = supabase.table(TABLE_NAME).select("*").execute()
        return pd.DataFrame(response.data)
    #view assets
    if choice == "View Assets":
        st.subheader("Current Field Assets")
        try:
            df = fetch_data()
            if not df.empty:
                st.dataframe(df, use_container_width=True,hide_index=True,height=600)
                st.info(f"Total Assets: {len(df)}")
            else:
                st.warning("No assets found in the database.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    #FILTER$DOWNLOAD
    elif choice == "Filter & Download":
        st.subheader("🔍 Filter & Download Assets")
        try:
            df = fetch_data()
            if not df.empty:
                st.write("### Apply Filters")
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
    elif choice == "Add New Asset":
        st.subheader("Add New Asset")
        with st.form("add_new_asset",clear_on_submit=True):
            col1, col2,col3,col4 = st.columns(4)
            with col1:
                g_code = st.text_input("G-CODE")
                serial_no = st.text_input("SERIAL_NO")
                model = st.selectbox("MODEL", options=MDL)
                asset_type = st.selectbox("TYPE", options=TYP)
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
     #updating added assets
    elif choice == "Update Asset":
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
                    col1, col2 = st.columns(2)

                    with col1:
                        u_serial_no = st.text_input("SERIAL_NO", value=str(asset_data.get("SERIAL_NO", "")))
                        u_model = st.text_input("MODEL", value=str(asset_data.get("MODEL", "")))
                        u_type = st.text_input("TYPE", value=str(asset_data.get("TYPE", "")))
                        u_kva = st.number_input("KVA", value=int(asset_data.get("KVA", 0)))
                        u_user_id = st.number_input("user_id", value=int(asset_data.get("user_id", 0)))


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

                    with col2:
                        u_area = st.text_input("AREA", value=str(asset_data.get("AREA", "")))
                        u_appr_kva = st.number_input("APPR_KVA", value=int(asset_data.get("APPR_KVA", 0)))
                        u_location = st.text_input("LOCATION", value=str(asset_data.get("LOCATION", "")))
                        u_field = st.text_input("FIELD", value=str(asset_data.get("FIELD", "")))
                        u_user = st.text_input("USER", value=str(asset_data.get("USER", "")))
                        u_crew = st.number_input("CREW", value=int(asset_data.get("CREW", 0)))
                        u_moved_from = st.text_input("MOVED_FROM", value=str(asset_data.get("MOVED_FROM", "")))
                        u_reason = st.text_area("REASON", value=str(asset_data.get("REASON", "")))

                    update_submit = st.form_submit_button("Update Asset")

                    if update_submit:
                        updated_data = {
                            "SERIAL_NO": u_serial_no,
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



elif selected=="PART_NUMBERS":
    st.info("WELCOME TO FIELD_OPERATIONS_PART_NUMBERS MANAGEMENT SYSTEM")
    "----"
    option=["CATERPILLAR","VOLVO","CUMMINS","BAUDOUIN"]
    selection=st.segmented_control("SELECT_GENSET-TYPE"
                                   ,options=option,
                                   )
    if selection=="CATERPILLAR":
        make_cat=st.selectbox("SELECT_MAKE",options=cat_make)
        if make_cat==cat_make[1]:
            kva_selected=st.selectbox("SELECT_KVA(320)",options=cat_kva)
            if kva_selected==cat_kva[7]:
                df={"PARTS":['WATER PUMP','GASKET','FUEL TRANSFER PUMP','BREATHER','BREATHER HOUSING','FAN','SOLENOID','GOVERNOR'
            ,'PUMP KIT','RADIATOR-CAP','BALL BEARING','SEAL','THERMOSTAT','FITTINGS','FITTINGS','OIL FILLING CAP','BALL BEARING'],
                'DESCRIPTION':['WATER PUMP WITH O-RING','GASKET(Thermostat','PUMP GP FUEL TRANSFER','BREATHER-AS','CLAMP-BREATHER HOUSING'
                               ,'FAN','SOLENOID-SHUT OFF','WOODWARD GOVERNOR','KIT-WATER PUMP SPCALSO','RADIATOR-CAP','BALL BEARING -L'
                               ,'SEAL- LIP TYPE','THERMOSTAT','PRESSURE RELIFE(1/8-27 PTF)','FITTING-GREASE','CAP-OIL FILLING','BALL BEARING-R'],
                'PART NO':['352-0203','7C-0307','1W-1700','9Y-2988','2N-8109','142-1931','1255774','1315455','433-9952'
                           ,'153-1403','3L-1425','5S-2106','2477133','4B-4550','2D-4867','6N-2985','8H-9789']}
                st.dataframe(df,height=700)
        elif make_cat==cat_make[7]:
            kva_selected=st.selectbox("SELECT_KVA(500)",options=cat_kva)
            if kva_selected==cat_kva[9]:
                df={'PARTS':['SEAL V-RING','SEAL VALVE COVER','SEAL TURBO OIL LINE','SEAL TURBO LINE','THERMOSTAT HOUSING SEAL','SEAL O-RING'
                        ,'SEAL O-RING','SEAL LIP TYPE','WATER PUMP','O-RING(W/P)','PRIMING PUMP','PUMP GP','FUEL HOSE','FUEL HOSE'
                         ,'BALL BEARING','BALL BEARING','BALL BEARING','SPIDER','CHECK VALVE','FUEL BYPASS VALVE','FUEL FILTER HOUSING'
                         ,'GASKET','RADIATOR CAP','RADIATOR CAP','THERMOSTAT O-RING','RADIATOR HOSE-B','RADIATOR HOSE-T','EXPANSION TANK'
                         ,'GASKET-TURBO','RELAY','BELT TIGHTENER','PWM-CONTROL','ENGINE ECM','EYE ROD ADJUSTER','EXHAUST BELLOW CLAMP'
                         ,'ALTERNATOR PULLEY','TURBO HIGH TEMP BOLT','TURBO HIGH TEMP NUT','AIR HOSE','STRAP'],
                'DESCRIPTION':['SEAL V-RING','SEAL VALVE COVER(TAPPET COVER)','SEAL TURBO OIL LINE','SEAL TURBO LINE','THERMOSTAT HOUSING SEAl',
                               'FUEL PUMP O-RING','SEAL O-RING','SEAL LIP TYPE','WATER PUMP WITHOUT GASKET','O-RING(WATER PUMP)','PRIMING PUMP',
                               'FUEL TRANSFER PUMP GP','FUEL SEPERATOR TO FUEL PUMP','F.PUMP TO F.FILTER','BALL BEARING-H','BALL BEARING-L',
                               'FOR BELT TIGHTENER*2','FAN UNIT SPIDER','CHECK VALVE','FUEL BYPASS VALVE','FUEL FILTER HOUSING',
                               'TAPPET PRESSURE PLATE GASKET','RADIATOR CAP','RADIATOR CAP C51','THERMOSTAT O-RING',
                               'RADIATOR RUBBER HOSE-BOTTOM','RADIATOR HOSE TOP','RADIATOR TANK','TURBO CHARGER GASKET','RELAY'
                               ,'BELT TIGHTENER (FAN PULLEY)','CONTROL GROUP','ENGINE ECM','ROD-ALTERNATOR','EXHAUST BELLOW CLAMP','ALTERNATOR PULLEY',
                               'TURBO HIGH TEMP BOLT','TURBO HIGH TEMP NUT','AIR HOSE','STRAP'],
                'PART NO':['8C-5238','2429537','198-6068','160-7037','3S-9643','107-5769','9F-4446','5S-2106','10R-8660','4687363',
                           '137-5541','384-8612','7N-4045','1-meter hose','8H-9789','3L-1425','297-4677','217-6022','2812725'
                           ,'139-6873','191-5055','272-0390','266-8550','391-6399','167-4407','264-7112','264-7111'
                           ,'4616246','1S-4295','3E-6477','309-8037','5125720','20R-8181','6L-5874','220-5619','1W-1456'
                           ,'2N-2765','2N-2766','286-0607','248-7330']}
                st.dataframe(df,hide_index=True,height=700)
        elif make_cat==cat_make[2]:
            kva_selected = st.selectbox("SELECT_KVA(810)", options=cat_kva)
            if kva_selected==cat_kva[15]:
                df = {'PARTS': ['FUEL PUMP', 'FUEL LINE-1 RR', 'FUEL LINE-2 RR', 'FUEL LINE-3 RR', 'FUEL LINE-4 RR',
                                'FUEL LINE-5 RR','FUEL LINE-6 RR', 'FUEL LINE-1 LR', 'FUEL LINE-2 LR', 'FUEL LINE-3 LR',
                                'FUEL LINE-4 LR', 'FUEL LINE-5 LR','FUEL LINE-6 LR', 'EXHAUST BELLOW', 'SEAL', 'BEARING'],
                      'DESCRIPTION': ['FUEL PUMP', 'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR',
                                      'RIGHT FROM RADIATOR','RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR', 'LEFT FROM RADIATOR',
                                      'LEFT FROM RADIATOR', 'LEFT FROM RADIATOR', 'LEFT FROM RADIATOR','LEFT FROM RADIATOR',
                                      'LEFT FROM RADIATOR', 'EXHAUST BELLOW (G-510,513)','SEAL O-RING', 'BALL-BEARING']
                    , 'PART NO': ['105-7573', '4P-9641', '4P-9643', '4P-9645', '4P-9647', '4P-9649', '4P-9651',
                                  '111-4122', '111-4124', '111-4126', '111-4128','111-4130','111-4132','211-1009',
                                  '9F-4446', '8H-9789']}
                st.dataframe(df, hide_index=True,height=700)
        elif make_cat==cat_make[6]:
            kva_selected = st.selectbox("SELECT_KVA(400)", options=cat_kva)
            if kva_selected==cat_kva[8]:
                df = {'PARTS': ['THERMOSTAT', 'THERMOSTAT O-RING TOP', 'THERMOSTAT O-RING BOTTOM', 'THERMOSTAT VENT',
                                'THERMOSTAT O-RING SIDE'
                    , 'BALL BEARING-L', 'SEAL', 'BALL BEARING-H', 'SEAL', 'FITTINGS', 'PULLY-ALT', 'FUEL TRNS PUMP',
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
                st.dataframe(df, hide_index=True,height=700)
        elif make_cat==cat_make[8]:
            kva_selected = st.selectbox("SELECT_KVA(600)", options=cat_kva)
            if kva_selected==cat_kva[11]:

                dt={'PARTS':['OIL FILING CAP','SEAL','FAN SPIDER','BALL BEARING','WATER PUMP','WATER PUMP KIT','TAPPET COVER SEAL'
                         ,'BELT TIGHTENER GP','BELT TENSIONER BEARING','EXHAUST BELLOW'],
                'DESCRIPTION':['OIL FILING CAP','SEAL V-RING','SPIDER -ASSY FAN','BALL BEARING','WATER PUMP WITHOUT GASKET',
                'O-RING KIT','SEAL-VALVE (Tappet cover)','BELT TIGHTENER GP(FAN PULLEY)','BALL BEARING FOR BELT TIGHTENER GP',
                               'EXHAUST BELLOW'],
                'PART NO':['5L-2952','8C-5238','217-6022','333-2408','10R-8660','4687363','2429537','309-8037','297-4677',
                           '227-3019'],}
                st.dataframe(dt, hide_index=True,height=700)
        elif make_cat==cat_make[9]:
            kva_selected = st.selectbox("SELECT_KVA(60)", options=cat_kva)
            if kva_selected==cat_kva[1]:
                df={'PARTS':['WATER PUMP','GASKET','INJECTOR HOSE','COOLANT PIPE','OIL COOLER TUBE','OIL COOLER TUBE'
                         ,'WOODWARD GOVERNOR','OIL FILING CAP','FUEL HOSE','RADIATOR HOSE-INLET','RADIATOR HOSE-OUTLET',
                         'FILTER GP FUEL','PUMP GP FUEL TRANSFER'],
                'DESCRIPTION':['WATER PUMP GP','GASKET(WATER PUMP)','INJECTOR HOSE','COOLANT PIPE WITH O-RING',
                'OIL COOLER TUBE(LOWER)','OIL COOLER TUBE(UPPER)','WOODWARD GOVERNOR','OIL FILING CAP','FUEL HOSE',
                               'RADIATOR HOSE-INLET','RADIATOR HOSE-OUTLET','FILTER GP FUEL','PUMP GP FUEL TRANSFER(HAND)'],
                'PART NO':['355-2252','225-8019','232-1794','2744707','3482V102','3482V101','272-2223'
                    ,'136-3608','232-1794','258-5355','258-5356','4668433','201-0877']}
                st.dataframe(df, hide_index=True,height=700)
        elif make_cat==cat_make[3]:
            kva = st.selectbox("SELECT_KVA(1100)", options=cat_kva)
            if kva==cat_kva[-2]:
                df={'PARTS':['WATER PUMP','WATER PUMP KIT'],
                'DESCRIPTION':['WATER PUMP','WATER PUMP KIT'],
                'PART NO':['352-0202','434-7542']}
                st.dataframe(df, hide_index=True,height=700)
        elif make_cat==cat_make[4]:
            kva = st.selectbox("SELECT_KVA(250)", options=cat_kva)
            if kva==cat_kva[6]:
                df={"PARTS":[],
                    "DESCRIPTION":[],
                    "PART NO":[]}
                st.dataframe(df, hide_index=True,height=700)


    elif selection=="VOLVO":
        st.selectbox("SELECT_MAKE",options=vol_make)
    elif selection=="CUMMINS":
        st.selectbox("SELECT_MAKE",options=cum_make)
    elif selection=="BAUDOUIN":
        st.selectbox("SELECT_MAKE",options=bau_make)
elif selected=="WORKSHOP":
    st.info("GENERATORS_UNDER_WORKSHOP")
    SUPABASE_URL = "https://zakswtxavrnvghpypmuz.supabase.co"
    SUPABASE_KEY = "sb_publishable_a0FSAnDcjWOpzLkYNDCwfg_moO6MV9A"
    TABLE_NAME = "GENSET ASSET"
    supabase=create_client(SUPABASE_URL,SUPABASE_KEY)

    resource=supabase.table("GENSET ASSET").select("G-CODE,SERIAL_NO,MODEL,TYPE,KVA,RUN_Hrs,"
                                                   "AREA,LOCATION,MOVED_FROM,REASON").eq('LOCATION','WORKSHOP').execute()
    df=resource.data
    st.dataframe(df, hide_index=True,height=500)
    D=len(df)
    st.metric('TOTAL NUMBER',D,"+")

elif selected=="FLEET MANAGEMENT":
    st.info("FLEET_MANAGEMENT AND PLANNING" + ':tractor:')
    @st.cache_data
    def loading_intial_data():
        data={
            "ENGINE ID":['G-029','G-003','G-004','G-007','G-005'],
            "Last_service Date":[
                (datetime.now()-timedelta(days=5)).date(),
                (datetime.now()-timedelta(days=16)).date(),
                (datetime.now()-timedelta(days=85)).date(),
                (datetime.now()-timedelta(days=95)).date(),
                (datetime.now()-timedelta(days=2)).date(),],
            "TYPE":["DIESEL","GASOLINE","DIESEL","GASOLINE","WATER"]
        }
        return pd.DataFrame(data)
    df=loading_intial_data()
    #automation logic
    def calculate_status(last_date):
        today=datetime.now().date()
        days_since=(today-last_date).days
        if days_since>=90:
            return "CRITICAL(90+Days overdue",":red_circle:"
        elif days_since>=15:
            return "Warning(15+Days overdue",":yellow_circle:"
        else:
            return "Operational",":green_circle:"
    df[["status",'Icon']]=df['Last_service Date'].apply(lambda x:pd.Series(calculate_status(x)))
    df['DaysSince Service']=df['Last_service Date'].apply(lambda x:(datetime.now().date()-x).days)

    col1,col2,col3=st.columns(3)
    with col1:
        st.metric('Total Engines',len(df))
    with col2:
        urgent=len(df[df['status'].str.contains('Critical')])
        st.metric('Critical alert',urgent,delta=-urgent,delta_color='inverse')
    with col3:
        st.metric('Fleet Health',f"{len(df[df['Icon']==":grean_circle:"])/len(df)*100:.0f}%")

    st.divider()
    #interactive table with style
    st.info("Fleet control system")
    def color_rows(val):
        if "Critical" in str(val):
            return 'backgroung-color:#ff4b4b:color:white'
        if "Warning" in str(val):
            return 'background-color:#ffa500:color:black'
        return()
    st.dataframe(df.style.applymap(color_rows,subset=["status"]),use_container_width=True,hide_index=True,height=300)


    # --- 1. DATA PREPARATION ---
    # (I am using your sample structure here)
    data = {
        'Engine_ID': ['ENG-101', 'ENG-202', 'ENG-303', 'ENG-404', 'ENG-505'],
        'Last_Service': ['2026-04-10', '2026-04-01', '2026-01-15', '2026-04-17', '2026-04-05'],
        'Service_Type': ['15-Day', '15-Day', '90-Day', '15-Day', '90-Day']
    }

    df = pd.DataFrame(data)

    # Convert to datetime and strip any time/timezone info for clean comparison
    df['Last_Service'] = pd.to_datetime(df['Last_Service']).dt.normalize()

    # Calculate Next Service Date
    df['Next_Service'] = df.apply(
        lambda x: x['Last_Service'] + pd.Timedelta(days=15 if x['Service_Type'] == '15-Day' else 90),
        axis=1
    )

    # Calculate days remaining (using today's date as a normalized timestamp)
    today_timestamp = pd.Timestamp(datetime.now().date()).normalize()
    df['Days_Remaining'] = (df['Next_Service'] - today_timestamp).dt.days

    # --- 2. VISUALIZATION ---
    fig = px.scatter(
        df,
        x='Next_Service',
        y='Days_Remaining',
        text='Engine_ID',
        color='Days_Remaining',
        color_continuous_scale='RdYlGn',
        title='Fleet Maintenance Schedule',
        labels={'Next_Service': 'Service Date', 'Days_Remaining': 'Days Remaining'}
    )

    # THE ULTIMATE FIX:
    # We use the exact same 'today_timestamp' we used for the calculation
    # This guarantees the data types match the X-axis exactly.
    fig.add_vline(
        x=today_timestamp.timestamp() * 1000,  # Convert to milliseconds for Plotly compatibility
        line_dash="dash",
        line_color="red",
        annotation_text="TODAY"
    )

    # Clean up layout
    fig.update_traces(marker=dict(size=12), textposition='top center')
    fig.update_layout(xaxis_type='date')  # Explicitly tell Plotly this is a date axis

    # --- 3. STREAMLIT DISPLAY ---
    st.plotly_chart(fig, use_container_width=True)
elif selected=='GENERAL_ASSETS':
    st.info("General assets trucking system")
    url = "https://zakswtxavrnvghpypmuz.supabase.co"
    key = "sb_publishable_a0FSAnDcjWOpzLkYNDCwfg_moO6MV9A"
    supabase = create_client(url, key)
    # to reade data from table
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