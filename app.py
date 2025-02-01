import streamlit as st
import os
import pdfkit
from jinja2 import Environment, FileSystemLoader

print("Streamlit version:", st.__version__)
print("PDFKit version:", pdfkit.__version__)
print("Jinja2 version:", Environment.__module__)

wkhtmltopdf = st.write(os.getcwd() os.getcwd() + '/wkhtmltopdf/bin/wkhtmltoimage.exe' );

print(wkhtmltopdf)

# Configure PDFKit
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf)  # Use the executable in the current folder

# Set up Jinja environment
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("health.html")

# Streamlit app
st.title("Health and Safety Form Generator")

with st.form("risk_form"):
    # Company Details
    st.header("Company Information")
    col1, col2 = st.columns(2)
    company_name = col1.text_input("Company Name")
    assessors_name = col1.text_input("Assessor's Name")
    address = col1.text_area("Address")
    date = col2.date_input("Date")
    stand_no = col2.text_input("Stand Number")
    signature = col2.file_uploader("Upload Signature", type=["png", "jpg", "jpeg"])
    
    # Hazards
    st.header("Hazards Information")
    hazards = []
    hazard_count = st.number_input("Number of Hazards", min_value=1, value=1, step=1)  # Allow user to specify number of hazards

    for i in range(hazard_count):  # Use user-defined number of hazards
        with st.expander(f"Hazard {i + 1}", expanded=(i == 0)):
            hazard = st.text_input(f"Hazard Type {i + 1}")
            severity = st.radio(f"Severity {i + 1}", ["Low", "Medium", "High"])
            probability = st.radio(f"Probability {i + 1}", ["Low", "Medium", "High"])
            persons = st.multiselect(f"Persons at Risk {i + 1}", ["Exhibitors", "Members of the public", "Contractors"])
            controls = st.text_area(f"Controls {i + 1}")
            hazards.append({
                "hazard": hazard,   
                "severity": severity,
                "probability": probability,
                "persons": persons,
                "controls": controls
            })
    
    # Health and Safety Representative
    st.header("Safety Representative")
    hs_name = st.text_input("Name")
    hs_position = st.text_input("Position")
    hs_contact = st.text_input("Contact Information")
    
    # Final Signature
    st.header("Final Authorization")
    final_signature = st.file_uploader("Upload Authorized Signature", type=["png", "jpg", "jpeg"])
    print_name = st.text_input("Print Name")
    
    submitted = st.form_submit_button("Generate PDF")

if submitted:
    # Render HTML with Jinja
    rendered_html = template.render(
        company_name=company_name,
        assessors_name=assessors_name,
        address=address,
        stand_no=stand_no,
        date=date,
        signature=signature,
        hazards=hazards,
        hs_name=hs_name,
        hs_position=hs_position,
        hs_contact=hs_contact,
        final_signature=final_signature,
        print_name=print_name
    )
    
    # Generate PDF
    try:
        pdf = pdfkit.from_string(rendered_html, False, configuration=config)
        
        # Show download button
        st.success("PDF generated successfully!")
        st.download_button(
            label="Download PDF",
            data=pdf,
            file_name=f"{print_name}.pdf",
            mime="application/pdf"
        )
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}") 