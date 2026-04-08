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