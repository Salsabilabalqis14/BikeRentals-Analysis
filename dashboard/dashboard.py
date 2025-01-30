import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

sns.set(style='dark')

def aggregate_data(df, group_by_col, mapping=None, agg_cols=None):
    if mapping:
        df[group_by_col] = df[group_by_col].replace(mapping)
    
    agg_cols = agg_cols or {"casual": "sum", "registered": "sum", "cnt": "sum"}
    grouped_df = df.groupby(group_by_col).agg(agg_cols).reset_index()
    return grouped_df.sort_values(by="cnt", ascending=False)

def load_data(file_path):
    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

def plot_bar_chart(x, y, title, colors, xlabel='', ylabel='', figsize=(10, 6)):
    plt.figure(figsize=figsize)
    sns.barplot(x=x, y=y, palette=colors)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    st.pyplot(plt)

def plot_line_chart(x, y, title, xlabel='', ylabel='', figsize=(12, 5)):
    plt.figure(figsize=figsize)
    sns.lineplot(x=x, y=y, marker='o', color='green')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    st.pyplot(plt)

def plot_grouped_bar_chart(x, casual, registered, total, labels, title, bar_width=0.25, figsize=(12, 5)):
    x_idx = np.arange(len(x))
    plt.figure(figsize=figsize)
    plt.bar(x_idx - bar_width, casual, width=bar_width, label="Casual", color="blue")
    plt.bar(x_idx, registered, width=bar_width, label="Registered", color="orange")
    plt.bar(x_idx + bar_width, total, width=bar_width, label="Total", color="green")
    
    plt.xticks(x_idx, labels)
    plt.legend(title="User Type")
    plt.title(title)
    plt.tight_layout()
    st.pyplot(plt)


df = load_data("dashboard/dataset.csv")

# Sidebar
min_date, max_date = df["dteday"].min(), df["dteday"].max()
with st.sidebar:
    st.image("logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date, max_value=max_date, value=[min_date, max_date]
    )

# Filter dataset by date
filtered_df = df[(df["dteday"] >= str(start_date)) & (df["dteday"] <= str(end_date))]

# Data aggregation
daily_rentals_df = aggregate_data(filtered_df, "dteday", agg_cols={"casual": "sum", "registered": "sum", "cnt": "sum"})

season_mapping = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
byseason_df = aggregate_data(filtered_df, "season", mapping=season_mapping)

month_mapping = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
bymonth_df = aggregate_data(filtered_df, "mnth", mapping=month_mapping)

weekday_mapping = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
byweekday_df = aggregate_data(filtered_df, "weekday", mapping=weekday_mapping)

byhour_df = aggregate_data(filtered_df, "hr")

holiday_mapping = {0: 'No', 1: 'Yes'}
byholiday_df = aggregate_data(filtered_df, "holiday", mapping=holiday_mapping)

workingday_mapping = {0: 'No', 1: 'Yes'}
byworkingday_df = aggregate_data(filtered_df, "workingday", mapping=workingday_mapping)

weathersit_mapping = {1: 'Clear', 2: 'Misty', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Snow'}
byweathersit_df = aggregate_data(filtered_df, "weathersit", mapping=weathersit_mapping, agg_cols={"cnt": "sum"})

# Dashboard
st.header('Bike Rentals Dashboard :sparkles:', divider="gray")

st.subheader('Daily Rentals')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Casual Users", daily_rentals_df["casual"].sum())
with col2:
    st.metric("Registered Users", daily_rentals_df["registered"].sum())
with col3:
    st.metric("Total Users", daily_rentals_df["cnt"].sum())

plot_line_chart(daily_rentals_df["dteday"], daily_rentals_df["cnt"], "Daily Rentals")

st.subheader('Bike Rentals by Season')
colors = ['lightblue'] * len(byseason_df)
colors[np.argmax(byseason_df["cnt"])] = 'orange'
plot_bar_chart(byseason_df["season"], byseason_df["cnt"], "Rentals by Season", colors)

st.subheader('Bike Rentals by Month')
colors = ['lightblue'] * len(bymonth_df)
colors[np.argmax(bymonth_df["cnt"])] = 'orange'
plot_bar_chart(bymonth_df["mnth"], bymonth_df["cnt"], "Rentals by Month", colors)

st.subheader('Bike Rentals by Day of the Week')
plot_grouped_bar_chart(
    byweekday_df["weekday"], 
    byweekday_df["casual"], 
    byweekday_df["registered"], 
    byweekday_df["cnt"], 
    byweekday_df["weekday"], 
    "Rentals by Day of the Week"
)

st.subheader('Bike Rentals by Hour')
plot_line_chart(byhour_df["hr"], byhour_df["cnt"], "Rentals by Hour")

colholiday, colweekday = st.columns(2)
with colholiday:
    st.subheader('Bike Rentals on Holidays')
    holiday_labels = ["Holiday" if h == "Yes" else "Non-Holiday" for h in byholiday_df["holiday"]]
    plot_grouped_bar_chart(
        holiday_labels,
        byholiday_df["casual"],
        byholiday_df["registered"],
        byholiday_df["cnt"],
        holiday_labels,
        "Rentals on Holidays",
        figsize=(6,5)
    )

with colweekday:
    st.subheader('Bike Rentals on Weekdays')
    workingday_labels = ["Working Day" if w == "Yes" else "Weekend" for w in byworkingday_df["workingday"]]
    plot_grouped_bar_chart(
        workingday_labels,
        byworkingday_df["casual"],
        byworkingday_df["registered"],
        byworkingday_df["cnt"],
        workingday_labels,
        "Rentals on Working Days",
        figsize=(6,5)
    )

st.subheader('Bike Rentals by Weather Condition')
colors = ['lightblue'] * len(byweathersit_df)
colors[np.argmax(byweathersit_df["cnt"])] = 'orange'
plot_bar_chart(byweathersit_df["weathersit"], byweathersit_df["cnt"], "Rentals by Weather Condition", colors)

st.caption('Copyright (c) Salsabila Balqis 2025')