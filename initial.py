# Hong Kong api to download Jewellry volume and value 

import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

# Define a function to plot all categories
def plot_definitions():
    # Define which series are "value items" - you can modify this list
    value_items = ['32', '19', '23', '18', '51']  # Jewellery, Motor vehicles, Furniture, Consumer durable goods, Electrical goods
    
    st.subheader("Value Items (Actual Volume Index)")
    cols = st.columns(len(value_items))
    
    for idx, series in enumerate(value_items):
        with cols[idx]:
            try:
                data_df = fetch_data(series)
                series_description = series_dict[series]
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(data_df.index, data_df[f'{series}_volume_index'], 
                       label=f'{series_description}', linewidth=2)
                ax.xaxis.set_major_locator(mdates.YearLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.set_title(f'{series_description}', fontsize=10)
                ax.set_xlabel('Year', fontsize=8)
                ax.set_ylabel('Index', fontsize=8)
                ax.legend(fontsize=6)
                plt.xticks(rotation=45, fontsize=7)
                plt.grid(True, color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error loading {series_description}: {str(e)}")
    
    st.subheader("Value Items (YoY Change)")
    cols2 = st.columns(len(value_items))
    
    for idx, series in enumerate(value_items):
        with cols2[idx]:
            try:
                data_df = fetch_data(series)
                series_description = series_dict[series]
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(data_df.index, data_df[f'{series}_volume_index_yoy'], 
                       label='YoY Change', linewidth=2, color='orange')
                ax.xaxis.set_major_locator(mdates.YearLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.set_title(f'{series_description} YoY', fontsize=10)
                ax.set_xlabel('Year', fontsize=8)
                ax.set_ylabel('Percentage Change', fontsize=8)
                ax.legend(fontsize=6)
                plt.xticks(rotation=45, fontsize=7)
                plt.grid(True, color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
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
        ["Select Individual Category", "View All Value Items"],
        horizontal=True
    )
    
    st.divider()
    
    if view_type == "Select Individual Category":
        series = st.selectbox('Select a series to plot', ['2', '8', '9', '12', '18', '30', '32', '35', '49', '3', '4', '5', '6', '7', '13', '14', '19', '23', '51', '36', '37', '38', '39', '40'])
        data_df = fetch_data(series)
        plot_data(data_df, series)

        # Display the latest data points
        st.dataframe(data_df.tail())
    else:
        # View all value items
        plot_definitions()
        
        # Show latest data for each value item
        st.subheader("Latest Data for Value Items")
        value_items = ['32', '19', '23', '18', '51']
        for series in value_items:
            try:
                data_df = fetch_data(series)
                series_description = series_dict[series]
                st.markdown(f"**{series_description}**")
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
