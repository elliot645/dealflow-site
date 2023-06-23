import streamlit as st
import pandas as pd

import ctvc_scraping as scraping
import ctvc_compiling as compiling



#setup

st.title("CTVC Newsletter Scraping!!")

with st.form("newsletter URL"):
    url = st.text_input('CTVC URL')
    submitted = st.form_submit_button("Submit")

openai_api_key = st.secrets['openai_key']

@st.cache_data
def scrape_and_compile(url,openai_api_key):
    #scrape
    scrape_output = scraping.scrape_data(url)
    #compile
    llm = compiling.set_up_llm(openai_api_key)
    extracted_output = compiling.extract_deals(llm,scrape_output['deals'])
    extracted_output += compiling.extract_exits(llm,scrape_output['exits'])
    return compiling.ctvc_to_df(extracted_output,scrape_output['date'],scrape_output['links'])

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

if submitted:   
    # scrape_output,extracted_output = scrape_and_compile(url,openai_api_key)
    # st.write(scrape_output)
    # st.write(extracted_output)
    df = scrape_and_compile(url,openai_api_key)
    csv = convert_df(df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='ctvc_deals.csv',
        mime='text/csv',
    )
    st.write(df)
