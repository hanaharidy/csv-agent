import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="CSV Agent", page_icon="📊")
st.title("📊 CSV Data Analyst Agent")
st.write("Upload any CSV and ask questions about it!")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Preview of your data")
    st.dataframe(df.head())
    uploaded_file.seek(0)

    question = st.text_input("Ask a question about your data",
                             placeholder="e.g. How many flowers are in each species?")

    if question:
        if st.button("🔍 Analyze"):
            with st.spinner("Agent is thinking..."):
                response = requests.post(
                    "http://localhost:8000/analyze",
                    files={"file": (uploaded_file.name,
                                   uploaded_file.getvalue(), "text/csv")},
                    data={"question": question}
                )

            if response.status_code == 200:
                result = response.json()
                st.success("Done!")

                st.markdown("### 🤖 Agent's Answer")
                st.write(result["answer"])

                st.markdown("### 📊 Auto Chart")
                numeric_cols = df.select_dtypes(include='number').columns
                categorical_cols = df.select_dtypes(include='object').columns

                if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                    cat_col = categorical_cols[0]
                    num_col = numeric_cols[0]
                    chart_data = df.groupby(cat_col)[num_col].mean()

                    fig, ax = plt.subplots(figsize=(8, 4))
                    chart_data.plot(kind='bar', ax=ax, color='steelblue',
                                   edgecolor='white')
                    ax.set_title(f"Average {num_col} by {cat_col}")
                    ax.set_xlabel(cat_col)
                    ax.set_ylabel(f"Average {num_col}")
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                elif len(numeric_cols) >= 2:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    df[numeric_cols[:4]].mean().plot(kind='bar', ax=ax,
                                                     color='steelblue')
                    ax.set_title("Average values per column")
                    plt.tight_layout()
                    st.pyplot(fig)

                st.info(f"Dataset: **{result['rows']} rows** × "
                        f"**{len(result['columns'])} columns**")
            else:
                st.error("Something went wrong. Is the backend running?")