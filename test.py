import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency
sns.set(style='dark')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Variabel start_date dan end_date
start_date = "2024-01-01"
end_date = "2024-12-31"

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
try:
    all_df = pd.read_csv("all_data.csv")
except FileNotFoundError:
    st.error("File 'all_data.csv' not found!")

all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard")

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk Terlaris", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=30)

st.pyplot(fig)

# Review Score
st.subheader("Review Score")
col1,col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index,
            y=review_score.values,
            order=review_score.index,
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
            )

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2, tab3 = st.tabs(["State", "Order Status", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values,
                data=state,
                palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
                    )

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Most Common Order Status: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index,
                y=order_status.values,
                order=order_status.index,
                palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index]
                )

    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab3:
    map_plot.plot()

    with st.expander("See Explanation"):
        st.write('Sesuai dengan grafik yang sudah dibuat, ada lebih banyak pelanggan di bagian tenggara dan selatan. Informasi lainnya, ada lebih banyak pelanggan di kota-kota yang merupakan ibu kota (São Paulo, Rio de Janeiro, Porto Alegre, dan lainnya).')
