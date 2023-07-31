from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

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
    try:
        with open('secrets.txt', 'r') as file:
            openai_api_key = file.readline()
    except:
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
    #deal trends
    st.write("Deal trends:")
    historical_deals = pd.read_csv("src/main df of all deals.csv", index_col=0)

    specified_stages = ["Seed", "Seed+", "pre-Seed", "Pre-Seed", "Pre-seed", "Pre Series A", "Series A", "Series B", "Series C"] #, "Series D", "Series E"]
    filtered_data_specified_stages = historical_deals[historical_deals['stage'].isin(specified_stages)]

    # Convert the 'date' column to datetime
    filtered_data_specified_stages['date'] = pd.to_datetime(filtered_data_specified_stages['date'])

    # Convert 'amount_raised' to a numeric type, coercing errors to NaN
    filtered_data_specified_stages['amount_raised'] = pd.to_numeric(filtered_data_specified_stages['amount_raised'], errors='coerce')

    # Define 4-week periods
    filtered_data_specified_stages['period'] = (filtered_data_specified_stages['date'].dt.to_period('M'))

    # Group by period and stage, summing the amount raised
    grouped_data_specified_stages = filtered_data_specified_stages.groupby(['period', 'stage'])['amount_raised'].sum().unstack().fillna(0)

    # Convert period index back to string
    grouped_data_specified_stages.index = grouped_data_specified_stages.index.astype(str)

    # Create the streamlit bar chart
    st.bar_chart(grouped_data_specified_stages)

    st.write("All deals:")
    st.dataframe(historical_deals)
