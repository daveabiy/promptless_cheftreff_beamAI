import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from IPython.display import display
from PIL import Image

def display_pdf_as_images(file_path):
    pages = convert_from_path(file_path)
    for page in pages:
        st.image(page, use_container_width=True)
        
# Main Streamlit App
def main():
    st.title("PDF Viewer and Output Comparison")

    # CSV File Path Input
    csv_file_path = st.sidebar.text_input("CSV File Path", "data/Testdata_Hackathon_results_gpt4.csv")

    # Check if the CSV file exists
    if os.path.exists(csv_file_path):
        # Load the CSV file
        df = pd.read_csv(csv_file_path)

        # User selects a file by ID
        file_id = st.sidebar.selectbox("Select File ID", df['File ID'].unique())

        # Filter the selected file's data
        selected_row = df[df['File ID'] == file_id].iloc[0]
        pdf_file = 'data/'+selected_row['pdf']  # Use the 'pdf' column for the file path
        expected_output = selected_row['Expected Output']
        extracted_output = selected_row['Extracted Text']
        score = selected_row['score']

        # Layout: Left column for PDF, right column for outputs
        col1, col2 = st.columns([2, 3])

        # Display PDF in the left column
        with col1:
            st.write("### PDF Viewer: ")
            if os.path.exists(pdf_file):
                display_pdf_as_images(pdf_file)
            else:
                st.write("PDF file not found.")

        # Display outputs in the right column
        with col2:
            st.write("### Expected Output")
            st.text_area("Expected Output", expected_output, height=200)

            st.write("### Extracted Output")
            st.text_area("Extracted Output", extracted_output, height=200)

            st.write("### Score")
            st.write(f"Score: {score}")
    else:
        st.write("CSV file not found. Please check the path.")

if __name__ == "__main__":
    main()
