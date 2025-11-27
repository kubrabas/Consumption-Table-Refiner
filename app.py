import streamlit as st
import pandas as pd
import os
# Importing the DataReader class directly from the Data Core layer
from src.data_core.reader import DataReader 

# --- SESSION STATE INITIALIZATION ---
# Initialize session state variables to manage application flow and data
if 'df_initial' not in st.session_state:
    st.session_state.df_initial = None
if 'df_final' not in st.session_state:
    st.session_state.df_final = None
if 'extra_cols' not in st.session_state:
    st.session_state.extra_cols = []
if 'step' not in st.session_state:
    st.session_state.step = 0 # 0: File Upload, 1: Data Loaded, 2: Final DF Ready

# --- APPLICATION HEADER ---
st.title("Your Table Unification Assistant")
st.markdown("## Let's Get Your Table Ready!")

# ==============================================================================
# STEP 0: FILE UPLOAD AND INITIAL PROCESSING (READING)
# ==============================================================================

if st.session_state.step == 0:
    st.write("Hey buddy! Upload your Excel file to start the cleaning and standardization process.")
    
    uploaded_file = st.file_uploader("Upload Data File (XLSX/XLS)", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # Save the uploaded file temporarily
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Instantiate DataReader and call read_data() directly
            reader = DataReader(temp_path)
            df_processed = reader.read_data()

            # Store the results
            st.session_state.df_initial = df_processed
            
            # Message for the user, confirming successful reading
            st.session_state.standardization_message = ""
            st.session_state.extra_cols = [] # No standardization/analysis done yet

            # Move to the next step
            st.session_state.step = 1 

            # Clean up the temporary file
            os.remove(temp_path) 
            st.rerun() 

        except ValueError as e:
            st.error(f"Buddy, there was a ValueError: {e}")
            st.session_state.step = 0
            
        except Exception as e:
            st.error(f"Oops! An unexpected error occurred: {e}")
            st.session_state.step = 0
            


# ==============================================================================
# STEP 1: DISPLAY RAW DATA PREVIEW AND PROMPT FOR ANALYSIS
# ==============================================================================

if st.session_state.step == 1:
    st.subheader("Data Received. Initial Preview.")
    
    # Hitap ve Mesaj
    st.info(f"I received your data file. Here is the raw data loaded directly from your file:")
    
    # Display the message from the processor
    st.write(st.session_state.standardization_message)
    
    # Display the head of the raw DataFrame
    st.dataframe(st.session_state.df_initial.head(), use_container_width=True)
    
    st.write("---")
    st.write("Now, let's get into the standardization and unit conversion rules.")
    
    # Placeholder for the next action button (to proceed to Step 2: Analysis)
    if st.button("Proceed to Standardization"):
        # This button will soon trigger the AnalysisLogic class.
        st.write("Analysis step coming soon...")