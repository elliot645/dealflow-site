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

    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a UI on top of a dataframe to let viewers filter columns

        Args:
            df (pd.DataFrame): Original dataframe

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        modify = st.checkbox("Add filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                left.write("↳")
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        _min,
                        _max,
                        (_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]

        return df

    historical_deals = pd.read_csv("src/main df of all deals.csv",index_col=0)
    st.dataframe(filter_dataframe(historical_deals))


