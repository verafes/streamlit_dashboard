import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

@st.cache_data
def load_and_prepare_data():
    import plotly.data as px_data
    df = px_data.gapminder()

    missing_before = df.isnull().sum().sum()
    df['gdp_total'] = df['gdpPercap'] * df['pop']
    df['decade'] = (df['year'] // 10) * 10
    df['income_category'] = pd.cut(
        df['gdpPercap'],
        bins=[0, 1000, 5000, 15000, float('inf')],
        labels=['Low Income', 'Lower Middle', 'Upper Middle', 'High Income']
    )
    df['data_quality'] = 'Complete'
    df = df.sort_values(['country', 'year']).reset_index(drop=True)

    cleaning_info = {
        'missing_values_before': missing_before,
        'missing_values_after': df.isnull().sum().sum(),
        'rows_processed': len(df),
        'columns_added': ['gdp_total', 'decade', 'income_category', 'data_quality'],
        'cleaning_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return df, cleaning_info

# Streamlit App
st.set_page_config(page_title="Gapminder Dashboard", layout="wide")

st.title("🌍 Global Development Dashboard (Gapminder)")
st.markdown("Visualize global life expectancy, GDP, and population trends.")

df, cleaning_info = load_and_prepare_data()

if df is not None:

    # Sidebar filters
    with st.sidebar:
        year = st.slider("Select Year", min_value=1952, max_value=2007, step=5, value=2007)
        country = st.selectbox("Select Country", sorted(df['country'].unique()))

    # Filtered data
    df_year = df[df['year'] == year]
    df_country = df[df['country'] == country]

    # Layout: Top metrics
    st.subheader(f"Summary for {year}")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(px.bar(
            df_year.groupby("continent", as_index=False).mean(numeric_only=True),
            x="continent", y="gdpPercap",
            title="Average GDP Per Capita by Continent",
            labels={"gdpPercap": "GDP Per Capita"},
            color="continent"
        ), use_container_width=True)

    with col2:
        st.plotly_chart(px.pie(
            df_year, names="continent", values="pop",
            title="Population Share by Continent"
        ), use_container_width=True)

    # Line chart of country's metrics
    st.subheader(f"📈 Trends for {country}")
    st.plotly_chart(px.line(
        df_country,
        x="year", y="lifeExp",
        title="Life Expectancy Over Time",
        markers=True
    ), use_container_width=True)

    # Data preview
    with st.expander("🔍 View Raw Data"):
        st.dataframe(df_year)

else:
    st.warning("Failed to load data.")
