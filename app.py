import streamlit as st
from PIL import Image
from extraction import process_image
import pandas as pd

st.title("Document Classification & Field Extraction")

uploaded_file = st.file_uploader("Upload a document image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    doc_type, fields = process_image(image)
    
    st.write("**Document Type:**", doc_type)
    
    # Display fields as a dataframe
    df = pd.DataFrame(fields.items(), columns=["Field", "Value"])
    st.table(df)
    
    # Allow download
    if st.button("Download as Excel"):
        output = pd.DataFrame([fields])
        output.to_excel("extracted_data.xlsx", index=False)
        with open("extracted_data.xlsx", "rb") as f:
            st.download_button("Download Excel", f, file_name="extracted_data.xlsx")
