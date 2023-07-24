import streamlit as st
import pandas as pd

from src import ctvc_scraping as scraping
from src import ctvc_compiling as compiling

#setup
st.title("CTVC Newsletter Scraper")

tab1, tab2 = st.tabs(["New Newsletter", "Past Newsletters"])

with tab1:

    with st.form("newsletter URL"):
        url = st.text_input('CTVC URL')
        submitted = st.form_submit_button("Submit")

    openai_api_key = st.secrets['openai_key']

    @st.cache_data
    def scrape_and_compile(url,openai_api_key):
        #scrape
        scrape_output = scraping.scrape_data(url)
        if scrape_output == None:
            return None
        #compile 
        llm = compiling.set_up_llm(openai_api_key)
        extracted_output = compiling.extract_deals(llm,scrape_output['deals'])
        extracted_output += compiling.extract_exits(llm,scrape_output['exits'])
        return compiling.ctvc_to_df(extracted_output,scrape_output['date'],scrape_output['links'])

    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    if submitted:   
        df = scrape_and_compile(url,openai_api_key)
        if df is None:
            st.write("No deals found")
            st.stop()
        st.write(df)
        csv = convert_df(df)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name= f"ctvc_deals.csv",
            mime='text/csv',
        )
    #st.write(df)

with tab2:
    historical_deals = pd.read_csv("src/main df of all deals.csv",index_col=0)
    st.write(historical_deals)
# full_df = pd.read_csv("all data.csv")
# expander = st.expander("all deals")
# expander.write(full_df)
    
# scrape_output = scraping.scrape_data(url)
# st.write(len(scrape_output['deals']))
# st.write(len(scrape_output['exits']))
# for deal in scrape_output['deals']:
#     st.write(deal)
# for exit in scrape_output['exits']:
#     st.write(exit)
# st.write(scrape_output['links'])
