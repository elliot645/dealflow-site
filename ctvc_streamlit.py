import streamlit as st
import pandas as pd

import ctvc_scraping as scraping
import ctvc_compiling as compiling

#setup

st.title("CTVC Newsletter Scraping!!")
url = st.text_input('CTVC URL')
openai_api_key = ''

@st.cache_data
def scrape_and_compile(url,openai_api_key):
    #scrape
    scrape_output = scraping.scrape_data(url)
    #compile
    llm = compiling.set_up_llm(openai_api_key)
    extracted_output = compiling.extract_deals(llm,scrape_output['deals'])
    extracted_output += compiling.extract_exits(llm,scrape_output['exits'])
    return compiling.ctvc_to_df(extracted_output,scrape_output['date'],scrape_output['links'])

if st.button('get data'):
    # scrape_output,extracted_output = scrape_and_compile(url,openai_api_key)
    # st.write(scrape_output)
    # st.write(extracted_output)
    st.write(scrape_and_compile(url,openai_api_key))
