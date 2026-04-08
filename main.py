import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="field options",
    page_icon="home.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# calling style.css
def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('style.css')

cat_make=['---click here---',3406,3412,"C32","6M16G2DO/S","6M16G6G4DO/S","C13",'C15','C18','C3.2']
cat_kva=['---click here---',60,100,135,200,201,250,320,400,500,545,600,625,650,770,810,1100,1500]
vol_make=['---click here---','TAD1341GE','TAD1342GE','TAD1343GE','TAD1344GE','TAD1641GE','TAD1642GE','TAD532GE','TAD734GE',
          'TAD840GE','TAD841GE','TWD1643GE','TWD1645GE']
vol_kva=['---click here---',105,200,201,225,246,250,251,252,300,316,320,330,364,400,412,413,416,500,509,546,574,595,635,705]
cum_make=['---click here---','CUMMINS']
cum_kva=['---click here---',13]
bau_make=['---click here---','BAUDOUIN']
bau_kva=['---click here---',200,250]

with st.sidebar:
    st.sidebar.image('img.png', width=80)
    selected=option_menu(
        menu_title="GENSET_FIELD",
        options=["ASSET_FIELD","PART_NUMBERS","MATERIALS_PDI","WORKSHOP","FLEET MANAGEMENT","RISK MANAGEMENT","STORES","KPI_TRACKING"],
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
if selected=="ASSET_FIELD":
    st.info("GENSET ASSETS UPDATE")
elif selected=="PART_NUMBERS":
    st.info("GENSET PART_NUMBERS UPDATE")
    option = ["CATERPILLAR", "VOLVO", "CUMMINS", "BAUDOUIN"]
    selection = st.segmented_control("SELECT_GENSET-TYPE"
                                     , options=option,
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
                          , 'FAN', 'SOLENOID-SHUT OFF', 'WOODWARD GOVERNOR', 'KIT-WATER PUMP SPCALSO', 'RADIATOR-CAP',
                                      'BALL BEARING -L'
                          , 'SEAL- LIP TYPE', 'THERMOSTAT', 'PRESSURE RELIFE(1/8-27 PTF)', 'FITTING-GREASE',
                                      'CAP-OIL FILLING', 'BALL BEARING-R'],
                      'PART NO': ['352-0203', '7C-0307', '1W-1700', '9Y-2988', '2N-8109', '142-1931', '1255774',
                                  '1315455', '433-9952'
                          , '153-1403', '3L-1425', '5S-2106', '2477133', '4B-4550', '2D-4867', '6N-2985', '8H-9789']}
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
                                      'FUEL PUMP O-RING', 'SEAL O-RING', 'SEAL LIP TYPE', 'WATER PUMP WITHOUT GASKET',
                                      'O-RING(WATER PUMP)', 'PRIMING PUMP',
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
                                  '137-5541', '384-8612', '7N-4045', '1-meter hose', '8H-9789', '3L-1425', '297-4677',
                                  '217-6022', '2812725'
                          , '139-6873', '191-5055', '272-0390', '266-8550', '391-6399', '167-4407', '264-7112',
                                  '264-7111'
                          , '4616246', '1S-4295', '3E-6477', '309-8037', '5125720', '20R-8181', '6L-5874', '220-5619',
                                  '1W-1456'
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
                      'DESCRIPTION': ['FUEL PUMP', 'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR',
                                      'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR', 'RIGHT FROM RADIATOR',
                                      'LEFT FROM RADIATOR',
                                      'LEFT FROM RADIATOR', 'LEFT FROM RADIATOR', 'LEFT FROM RADIATOR',
                                      'LEFT FROM RADIATOR',
                                      'LEFT FROM RADIATOR', 'EXHAUST BELLOW (G-510,513)', 'SEAL O-RING', 'BALL-BEARING']
                    , 'PART NO': ['105-7573', '4P-9641', '4P-9643', '4P-9645', '4P-9647', '4P-9649', '4P-9651',
                                  '111-4122', '111-4124', '111-4126', '111-4128', '111-4130', '111-4132', '211-1009',
                                  '9F-4446', '8H-9789']}
                st.dataframe(df, hide_index=True, height=700)
        elif make_cat == cat_make[6]:
            kva_selected = st.selectbox("SELECT_KVA(400)", options=cat_kva)
            if kva_selected == cat_kva[8]:
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
                st.dataframe(df, hide_index=True, height=700)
        elif make_cat == cat_make[8]:
            kva_selected = st.selectbox("SELECT_KVA(600)", options=cat_kva)
            if kva_selected == cat_kva[11]:
                dt = {'PARTS': ['OIL FILING CAP', 'SEAL', 'FAN SPIDER', 'BALL BEARING', 'WATER PUMP', 'WATER PUMP KIT',
                                'TAPPET COVER SEAL'
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
                    , 'WOODWARD GOVERNOR', 'OIL FILING CAP', 'FUEL HOSE', 'RADIATOR HOSE-INLET', 'RADIATOR HOSE-OUTLET',
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
#part numbers out
elif selected=="MATERIALS_PDI":
    st.info("GENSET MATERIALS_PDI UPDATE")
elif selected=="WORKSHOP":
    st.info("GENSET WORKSHOP UPDATE ACTIVITIES FROM PDI")
elif selected=="FLEET MANAGEMENT":
    st.info("GENSET_FLEET MANAGEMENT UPDATE ACTIVITIES")
elif selected=="RISK MANAGEMENT":
    st.info("GENSET_RISK MANAGEMENT UPDATE ACTIVITIES")
elif selected=="STORES":
    st.info("GENSET_STORES UPDATE REQUESTS")
elif selected=="KPI_TRACKING":
    st.info("GENSET_KPI_TRACKING UPDATE FIELD"+"icon= box")
