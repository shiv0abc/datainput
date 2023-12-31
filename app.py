import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

con = st.connection("snowflake")

st.title("PoCDataInput")

authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'],config['cookie']['key'],  config['cookie']['expiry_days'])

# hashed_passwords = stauth.Hasher(["password1", "password2"]).generate()
# print(hashed_passwords)

name, authentication_status, username = authenticator.login("Login", "main")


if authentication_status == True:
    # logout button
    with st.sidebar:
        st.markdown(
    f'''
        <style>
            .sidebar .sidebar-content {{
                width: 500px;
            }}
        </style>
    ''',
    unsafe_allow_html=True
)
        st.subheader(f"Welcome, {name}")
        authenticator.logout("Logout", "sidebar")
        

        materialcode = st.text_input("MaterialCode", key="materialcode")
        if len(list(materialcode))>0:
            if materialcode.isdigit() == False:
                st.error("Please enter only digits")
            df = con.cursor().execute("SELECT * FROM TEST1DB.PUBLIC.APPTBL WHERE MATERIALCODE LIKE '"+materialcode+"%'").fetchall()
            if len(df) > 0:
                st.table(df)
            
        projectcategory = st.selectbox(
            'ProjectCategory',
            ("Select",)+('savings', 'costup', 'costavoidance','noinitiative'), key="projectcategory")

        subcategory_dict = {"savings": ["PN_price_negotiation","BulkManufacturing"], 
                    "costup":["PN_price_negotiation"],
                    "noinitiative":["noinitiative"],
                    "costavoidance":["PN_price_negotiation"]}
        
        subcategory = None

        if projectcategory:
            if projectcategory == "savings":
                subcategory = st.selectbox('subcategory',["Select"] + subcategory_dict["savings"])
            if projectcategory == "costup":
                subcategory = st.selectbox('subcategory',["Select"] + subcategory_dict["costup"])
            if projectcategory == "noinitiative":
                subcategory = st.selectbox('subcategory',["Select"] + subcategory_dict["noinitiative"])
            if projectcategory == "costavoidance":
                subcategory = st.selectbox('subcategory',["Select"] + subcategory_dict["costavoidance"])

        projectdescription = st.text_area("projectdescription","It Cannot Be Blank", key="projectdescription")

        if len(list(projectdescription)) == 0:
            st.error("Please enter description. It cannot be blank")
        else:
            if len(list(projectdescription)) <10:
                st.error("Please describe in detail")
        comment = st.text_area("Please provide additional comments if any", key="comment")

        npr = st.number_input("NewPriceRequestedBySupplier",min_value = 0.00,max_value=10000.00,step=0.01,format="%.2f", key="npr")

        def clear_fields():
            with con.cursor() as cur:
                cur.execute("INSERT INTO APPTBL(MaterialCode ,ProjectCategory, SubCategory, ProjectDescription ,AdditionalComment ,NewPriceRequestedBySupplier) values"+f"({materialcode},'{projectcategory}','{subcategory}','{projectdescription}','{comment}',{npr})")
            st.success("Data inserted successfully")
            df = con.cursor().execute("SELECT * FROM TEST1DB.PUBLIC.APPTBL")

            st.session_state.materialcode = ""
            st.session_state.projectcategory = "Select"
            st.session_state.projectdescription = ""
            st.session_state.comment = ""
            st.session_state.npr = 0.00

        submit = st.button("submitbutton",type="primary", on_click=clear_fields)

        df = con.cursor().execute("SELECT * FROM TEST1DB.PUBLIC.APPTBL")
        #df = con.query("SELECT * FROM TEST1DB.PUBLIC.APPTBL")

    # @st.cache_data()
    # def convert_to_csv(df):
    #     dfc = df.fetchall()
    #     dfc.columns = list(df.columns)
    #     # IMPORTANT: Cache the conversion to prevent computation on every rerun
    #     return dfc.to_csv(index=False).encode('utf-8')

    # col1, col2 = st.columns(2)
    # with col1:
    #     reload = st.button("reload",type="primary")
    #     if reload:
    #         df = con.cursor().execute("SELECT * FROM TEST1DB.PUBLIC.APPTBL")
    #with col2:
        # csv = convert_to_csv(df)
        # st.button(
        #     label="Download data as CSV",
        #     # data=csv,
        #     # file_name='data.csv',
        #     # mime='text/csv',
        # )
    st.table(df)

if authentication_status == False:
    st.error("Incorrect username/password")

if authentication_status == None:
    st.info("Please login")


# [connections.snowflake]
# account = "hyocgxp-kx57838"
# user = "SARVESHK76"
# password = "Ml762046"
# role = "ACCOUNTADMIN"
# warehouse = "DEMO_WAREHOUSE"
# database = "DEMO"
# schema = "PUBLIC"
# client_session_keep_alive = true