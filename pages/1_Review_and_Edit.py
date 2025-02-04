import streamlit as st
import pandas as pd

# Step 2: Review and Edit Page
def display_hazard_form(index, assessment):
    """Helper function to display hazard form fields"""
    with st.expander(f"Hazard {index}", expanded=False):
        fields = {
            "Hazard": st.text_input(f"Hazard Name for Hazard {index}", value=assessment['Hazard']),
            "Severity": st.radio(f"Severity for Hazard {index}", 
                options=["High", "Medium", "Low"], 
                index=["High", "Medium", "Low"].index(assessment['Severity'])),
            "Probability": st.radio(f"Probability for Hazard {index}", 
                options=["High", "Medium", "Low"],
                index=["High", "Medium", "Low"].index(assessment['Probability'])),
            "Persons at Risk": st.text_input(f"Persons at Risk for Hazard {index}", 
                value=assessment['Persons at Risk']),
            "Controls to Minimise Risk": st.text_area(f"Controls to Minimise Risk for Hazard {index}", 
                value=assessment['Controls to Minimise Risk'])
        }
        return fields

def review_and_edit():
    st.title("Step 2: Review and Edit Your Information")

    if 'user_data' not in st.session_state:
        st.error("No user data found. Please go back to the information gathering step.")
        return

    user_data = st.session_state['user_data']
    
    # Display form fields
    with st.form("user_data_form"):
        updated_user_data = {
            'name': st.text_input("Your Name", value=user_data['name']),
            'company': st.text_input("Company Name", value=user_data['company']),
            'category': st.selectbox("Business Category", 
                ["Construction", "Event Management", "Healthcare", "Education", "Hospitality", "Retail", "Other"],
                index=["Construction", "Event Management", "Healthcare", "Education", "Hospitality", "Retail", "Other"].index(user_data['category'])),
            'activity': st.text_input("Describe your Business Activity", value=user_data['activity']),
            'address': st.text_area("Address", value=user_data.get('address', '')),
            'stand_no': st.text_input("Stand Number", value=user_data.get('stand_no', '')),
            'date': st.date_input("Select Date", value=pd.to_datetime("today").date()),
            'Assessor_Signature': st.file_uploader("Assessor's Signature", type=["png", "jpg", "jpeg"]),
        }

        if 'ai_response' in st.session_state:
            st.subheader("Risk Assessment Details")
    
            updated_assessments = [
                display_hazard_form(i+1, assessment)
                for i, assessment in enumerate(st.session_state['ai_response']["assessments"])
            ]
            
            submit_button = st.form_submit_button("Save")
            if submit_button:
                if not all(updated_user_data.values()):
                    st.error("Please fill all required fields.")
                else:
                    st.session_state['user_data'] = updated_user_data
                    st.session_state['ai_response']['assessments'] = updated_assessments
                    st.success("Changes saved! You can proceed to the next step.")
                    st.switch_page("pages/2_Generate_PDF.py")

# Call the review and edit function
review_and_edit()
