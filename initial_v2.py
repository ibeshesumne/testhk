# Hong Kong api to download Jewellry volume and value 
# Version 2 - With y-axis scaling options

import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Define all available series
all_series = ['2', '8', '9', '12', '18', '30', '32', '35', '49', '3', '4', '5', '6', '7', '13', '14', '19', '23', '51', '36', '37', '38', '39', '40']

# Define the series dictionary
series_dict = {
    "2": "Food, drink, tobacco (ex super)",
    "8": "Supermarkets",
    "9": "Fuels",
    "12": "Clothing, footwear and others",
    "18": "Consumer durable goods",
    "30": "Department stores",
    "32": "Jewellery, watches and clocks, and others",
    "35": "Other consumer goods",
    "49": "Supermarkets and supermarket sections of department stores",
    "3": "Fish, livestock and poultry, fresh or frozen",
    "4": "Fruits and vegetables, fresh",
    "5": "Bread, pastry, confectionery and biscuits",
    "6": "Other food not elsewhere classified",
    "7": "Alcoholic drinks and tobacco",
    "13": "Wearing apparel",
    "14": "Footwear, allied products and other clothing accessories",
    "19": "Motor vehicles and parts",
    "23": "Furniture and fixtures",
    "36": "Books, newspapers, stationery and gifts",
    "37": "Chinese drugs and herbs",
    "38": "Optical shops",
    "39": "Medicines and cosmetics",
    "40": "Other consumer goods not elsewhere",
    "51": "Electrical goods and other consumer durable goods not elsewhere"
}

# Define a function to fetch and process the data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data(series):
    url = "https://www.censtatd.gov.hk/api/post.php"
    parameters = {
        "cv": {
            "OUTLET_TYPE": [series]
        },
        "sv": {
            "VOL_IDX_RS": ["Raw_1dp_idx_n"]
        },
        "period": {
            "start": "197901"
        },
        "id": "620-67003",
        "lang": "en"
    }
    data = {'query': json.dumps(parameters)}
    r = requests.post(url, data=data, timeout=20)
    response_data = r.json()
    df = pd.DataFrame(response_data['dataSet'])
    df = df[~df['freq'].str.contains('Y')]
    df = df[~df['OUTLET_TYPEDesc'].str.contains('Total')]
    df = df[df['svDesc'].str.contains('Index')]
    df = df.drop(['sv', 'sd_value'], axis=1)
    data_df = df[['period', 'figure']].copy()
    data_df.loc[:, 'period'] = pd.to_datetime(data_df['period'], format='%Y%m').dt.strftime('%Y-%m-%d')
    data_df = data_df.sort_values(by='period')
    data_df = data_df.rename(columns={'figure': f'{series}_volume_index'})
    data_df[f'{series}_volume_index_yoy'] = data_df[f'{series}_volume_index'].pct_change(12) * 100
    data_df['period'] = pd.to_datetime(data_df['period'])
    data_df.set_index('period', inplace=True)
    return data_df

# Define a function to fetch all data
@st.cache_data(ttl=3600)
def fetch_all_data():
    all_data = {}
    for series in all_series:
        try:
            all_data[series] = fetch_data(series)
        except Exception as e:
            st.warning(f"Failed to fetch data for series {series}: {str(e)}")
    return all_data

# Define a function to plot the data
def plot_data(data_df, series):
    series_description = series_dict[series]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data_df.index, data_df[f'{series}_volume_index'], label=f'{series_description} volume Index')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_title(f'{series_description} volume Index')
    ax.set_xlabel('Year')
    ax.set_ylabel('Index')
    ax.legend()
    plt.xticks(rotation=45)
    plt.grid(True, color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    st.pyplot(fig)

    fig, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(data_df.index, data_df[f'{series}_volume_index_yoy'], label='Volume Index YoY Change')
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.set_title(f'Year on Year Change in {series_description} volume index')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Percentage Change')
    ax2.legend()
    plt.xticks(rotation=45)
    plt.grid(True, color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    st.pyplot(fig)

# Define a function to plot all categories with y-axis option
def plot_definitions(y_axis_type):
    # Fetch all data first
    all_data = fetch_all_data()
    
    # Calculate global min/max for common y-axis
    if y_axis_type == "Common Y-Axis":
        volume_min = float('inf')
        volume_max = float('-inf')
        yoy_min = float('inf')
        yoy_max = float('-inf')
        
        for series, data_df in all_data.items():
            vol_col = f'{series}_volume_index'
            yoy_col = f'{series}_volume_index_yoy'
            if vol_col in data_df.columns:
                volume_min = min(volume_min, data_df[vol_col].min())
                volume_max = max(volume_max, data_df[vol_col].max())
            if yoy_col in data_df.columns:
                yoy_min = min(yoy_min, data_df[yoy_col].min())
                yoy_max = max(yoy_max, data_df[yoy_col].max())
        
        # Add some padding
        volume_min = volume_min * 0.9
        volume_max = volume_max * 1.1
        yoy_min = yoy_min * 1.1 if yoy_min < 0 else yoy_min * 0.9
        yoy_max = yoy_max * 1.1 if yoy_max > 0 else yoy_max * 0.9
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📊 Volume Index", "📈 Year-on-Year Change"])
    
    with tab1:
        st.markdown("### Volume Index Trends")
        if y_axis_type == "Common Y-Axis":
            st.info(f"📏 All charts use common Y-axis range: {volume_min:.0f} to {volume_max:.0f}")
        # Use 2 columns layout for better readability
        for i in range(0, len(all_series), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(all_series):
                    series = all_series[i + j]
                    if series in all_data:
                        with cols[j]:
                            try:
                                data_df = all_data[series]
                                series_description = series_dict[series]
                                fig, ax = plt.subplots(figsize=(10, 5))
                                ax.plot(data_df.index, data_df[f'{series}_volume_index'], 
                                       label=f'{series_description}', linewidth=2.5, color='#1f77b4')
                                ax.xaxis.set_major_locator(mdates.YearLocator())
                                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                                ax.set_title(f'{series_description}', fontsize=12, fontweight='bold')
                                ax.set_xlabel('Year', fontsize=10)
                                ax.set_ylabel('Index', fontsize=10)
                                ax.legend(fontsize=9)
                                plt.xticks(rotation=45, fontsize=9)
                                plt.grid(True, color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
                                
                                # Set y-axis limits if common y-axis is selected
                                if y_axis_type == "Common Y-Axis":
                                    ax.set_ylim(volume_min, volume_max)
                                
                                plt.tight_layout()
                                st.pyplot(fig)
                            except Exception as e:
                                st.error(f"Error loading {series_description}: {str(e)}")
    
    with tab2:
        st.markdown("### Year-on-Year Percentage Change")
        if y_axis_type == "Common Y-Axis":
            st.info(f"📏 All charts use common Y-axis range: {yoy_min:.1f}% to {yoy_max:.1f}%")
        # Use 2 columns layout for better readability
        for i in range(0, len(all_series), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(all_series):
                    series = all_series[i + j]
                    if series in all_data:
                        with cols[j]:
                            try:
                                data_df = all_data[series]
                                series_description = series_dict[series]
                                fig, ax = plt.subplots(figsize=(10, 5))
                                ax.plot(data_df.index, data_df[f'{series}_volume_index_yoy'], 
                                       label='YoY Change', linewidth=2.5, color='#ff7f0e')
                                ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)
                                ax.xaxis.set_major_locator(mdates.YearLocator())
                                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                                ax.set_title(f'{series_description} YoY', fontsize=12, fontweight='bold')
                                ax.set_xlabel('Year', fontsize=10)
                                ax.set_ylabel('Percentage Change (%)', fontsize=10)
                                ax.legend(fontsize=9)
                                plt.xticks(rotation=45, fontsize=9)
                                plt.grid(True, color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
                                
                                # Set y-axis limits if common y-axis is selected
                                if y_axis_type == "Common Y-Axis":
                                    ax.set_ylim(yoy_min, yoy_max)
                                
                                plt.tight_layout()
                                st.pyplot(fig)
                            except Exception as e:
                                st.error(f"Error loading {series_description}: {str(e)}")

# Define the Streamlit app
def main():
    st.title('Hong Kong Monthly Retail Sales Data')
    
    # Add menu option for view type
    view_type = st.radio(
        "Choose view:",
        ["Select Individual Category", "View All Categories"],
        horizontal=True
    )
    
    st.divider()
    
    if view_type == "Select Individual Category":
        series = st.selectbox('Select a series to plot', all_series)
        data_df = fetch_data(series)
        plot_data(data_df, series)

        # Display the latest data points
        st.dataframe(data_df.tail())
    else:
        # View all categories - add submenu for y-axis selection
        st.subheader("📊 Chart Display Options")
        y_axis_option = st.radio(
            "Select Y-axis scaling:",
            ["Individual Y-Axis", "Common Y-Axis"],
            horizontal=True,
            help="Individual Y-Axis scales each chart independently. Common Y-Axis uses the same scale for all charts to allow direct comparison."
        )
        
        st.divider()
        
        # Draw charts based on selection
        plot_definitions(y_axis_option)
        
        # Show latest data for each category in expanders
        st.subheader("📋 Latest Data")
        for series in all_series:
            try:
                data_df = fetch_data(series)
                series_description = series_dict[series]
                with st.expander(f"🔍 {series_description}"):
                    st.dataframe(data_df.tail(), use_container_width=True)
            except Exception as e:
                st.error(f"Error loading {series_dict[series]}: {str(e)}")

    # Display attribution and caution
    st.markdown("""
    **Attribution and caution:** 
    1. All data for series is sourced from the Hong Kong government [census and statistics department](https://www.censtatd.gov.hk/en/web_table.html?id=620-67003).
    2. The year on year changes and charts are generated by code and may be subject to error and miscalculation. No liability is assumed for computed data and generated charts.
    """)
    
    # Print the series dictionary in a formatted way
    st.sidebar.markdown("### Series Descriptions:")
    for key, value in series_dict.items():
        st.sidebar.markdown(f"<small>{key} : {value}</small>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

