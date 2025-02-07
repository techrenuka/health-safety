import streamlit as st
import os
import json
from utils.ai_handler import get_ai_recommendation
from utils.pdf_generator import generate_pdf

st.set_page_config(
    page_title="Event Risk Assessment Generator",
    page_icon="🔍"
)

# Initialize session state more efficiently
for key in ["user_data", "ai_response"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "user_data" else None

st.title("Event Risk Assessment Generator")

# Step 1: User Input Form
with st.form("risk_form"):

    form_fields = {
        "name": st.text_input("Your Name", ""),
        "company_name": st.text_input("Company Name", ""),
        "business_category": st.selectbox("Business Category", 
            ["Construction", "Hospitality", "Retail", "Events"]),
        "business_activity": st.text_area("Describe Business Activity", ""),
        "potential_hazards": st.text_area("Please Describe Any Potential Hazards That Your Business May Pose At The Event")
    }
    submit_button = st.form_submit_button("Submit")




if submit_button:
    if not all(form_fields.values()):
        st.error("Please fill all required fields.")
    else:
        with st.spinner("Generating risk assessment..."):
            try:
                ai_response = get_ai_recommendation(form_fields)
                
                if isinstance(ai_response, dict) and "error" in ai_response:
                    st.error(f"AI Error: {ai_response['error']}")
                else:
                    # Store data in session state
                    st.session_state.update({
                        "ai_response": ai_response,
                        "form_data": form_fields,
                        "user_data": {
                            'name': form_fields["name"],
                            'company': form_fields["company_name"],
                            'category': form_fields["business_category"],
                            'activity': form_fields["business_activity"],
                            'potential_hazards': form_fields["potential_hazards"]

                        }
                    })
                    st.success("Risk assessment generated successfully! Please proceed to the Review page.")

                    st.button("Review Risk Assessment", on_click=st.switch_page("pages/1_Review_and_Edit.py"))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")



