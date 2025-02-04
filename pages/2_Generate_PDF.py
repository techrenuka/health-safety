import streamlit as st
import pdfkit
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
import boto3
from utils.spaces_config import get_spaces_client
from io import BytesIO

def get_wkhtmltopdf_path():
    """Helper function to get wkhtmltopdf path"""
    if os.name == 'nt':  # Windows
        paths = [
            'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
            '.\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    return 'wkhtmltopdf'  # Linux/Mac default

# Configure PDFKit
try:
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf') 
except Exception as e:
    st.error(f"Error configuring wkhtmltopdf: {str(e)}")
    st.info("Please ensure wkhtmltopdf is installed on your system")
    st.stop()

# Set up Jinja environment
template_path = "health.html"
if not os.path.exists(template_path):
    st.error(f"Template file not found: {template_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    st.stop()

env = Environment(loader=FileSystemLoader('.'))
try:
    template = env.get_template("health.html")
except Exception as e:
    st.error(f"Error loading template: {str(e)}")
    print(f"Error loading template: {str(e)}")
    st.stop()

st.title("Step 3: Generate Health and Safety Form")

# Check for required session state data
if 'ai_response' not in st.session_state or 'user_data' not in st.session_state:
    st.error("Please complete the previous steps first")
    st.stop()

# Get AI recommendations and user data
ai_response = st.session_state['ai_response']
user_data = st.session_state['user_data']

# Create two columns for the action buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Check Again"):
        st.switch_page("pages/1_Review_and_Edit.py")

# Dynamic form with AI-recommended fields
with st.form("risk_assessment_form"):
    # Company Details Section
    st.header("Company Information")
    col1, col2 = st.columns(2)
    
    company_details = {
        'company_name': col1.text_input("Company Name", value=user_data.get("company", ""), disabled=True),
        'assessors_name': col1.text_input("Assessor's Name", value=user_data.get("name", ""), disabled=True),
        'address': col1.text_area("Address", value=user_data.get("address", ""), disabled=True),
        'date': col2.date_input("Assessment Date", value=datetime.now(), disabled=True),
        'stand_no': col2.text_input("Stand Number", value=user_data.get("stand_no", ""), disabled=True),
        'signature': col2.file_uploader("Upload Signature", type=["png", "jpg", "jpeg"], disabled=True)
    }

    # Business Information
    st.header("Business Details")
    business_info = {
        'category': st.text_input("Business Category", value=user_data.get("category", ""), disabled=True),
        'activity': st.text_area("Business Activity", value=user_data.get("activity", ""), disabled=True)
    }

    # Hazards Assessment Section
    st.header("Risk Assessment")
    hazards = []
    
    for i, assessment in enumerate(ai_response.get("assessments", [])):
        with st.expander(f"Hazard {i + 1}", expanded=(i == 0)):
            hazard_data = {
                "hazard": st.text_input(f"Hazard Type {i + 1}", value=assessment.get("Hazard", ""), disabled=True),
                "severity": st.radio(f"Severity {i + 1}", ["Low", "Medium", "High"], 
                                   index=["Low", "Medium", "High"].index(assessment.get("Severity", "Low")), disabled=True),
                "probability": st.radio(f"Probability {i + 1}", ["Low", "Medium", "High"],
                                      index=["Low", "Medium", "High"].index(assessment.get("Probability", "Low")), disabled=True),
                "persons": st.text_input(f"Persons at Risk {i + 1}", value=assessment.get("Persons at Risk", ""), disabled=True),
                "controls": st.text_area(f"Control Measures {i + 1}", value=assessment.get("Controls to Minimise Risk", ""), disabled=True)
            }
            hazards.append(hazard_data)

    # Health & Safety Representative
    st.header("Safety Representative Details")
    safety_rep = {
        'hs_name': st.text_input("Representative Name", value=user_data.get("hs_name", ""),),
        'hs_position': st.text_input("Position", value=user_data.get("hs_position", "")),
        'hs_contact': st.text_input("Contact Details", value=user_data.get("hs_contact", ""))
    }

    # Final Authorization
    st.header("Authorization")
    authorization = {
        'final_signature': st.file_uploader("Authorized Signature", type=["png", "jpg", "jpeg"]),
        'print_name': st.text_input("Print Name", value=user_data.get("name", ""))
    }

    # Submit button
    submitted = st.form_submit_button("✅ Approve & Generate PDF")
    
if submitted:
    if not (all(safety_rep.values()) and all(authorization.values())):
        st.error("Please fill all required fields.")
    else:
        try:
            # Prepare data for PDF generation
            pdf_data = {
                **{k: v or "" for k, v in company_details.items()},  # Replace None with empty string
                **{k: v or "" for k, v in business_info.items()},
                'hazards': [{k: v or "" for k, v in h.items()} for h in hazards],
                **{k: v or "" for k, v in safety_rep.items()},
                **{k: v or "" for k, v in authorization.items() if not isinstance(v, (bytes, bytearray))}
            }

            # Validate critical data
            print("PDF Data Keys:", pdf_data.keys())
            for key, value in pdf_data.items():
                if value is None:
                    print(f"Warning: {key} is None")

            # Generate HTML from template
            rendered_html = template.render(**pdf_data)
            
            if not rendered_html:
                raise ValueError("Failed to render HTML template")
            
            # Handle file uploads for signatures
            if authorization.get('final_signature'):
                final_sig_bytes = authorization['final_signature'].read()
                # Store signature temporarily or handle it in the template
                pdf_data['final_signature_data'] = final_sig_bytes

            if company_details.get('signature'):
                company_sig_bytes = company_details['signature'].read()
                # Store signature temporarily or handle it in the template
                pdf_data['company_signature_data'] = company_sig_bytes

            # PDF generation options with more detailed settings
            options = {
                'encoding': 'UTF-8',
                'no-outline': None,
                'quiet': '',
                'enable-local-file-access': None,
                'disable-smart-shrinking': None,
                'print-media-type': None,
                'page-size': 'A4'
            }

            # Generate PDF with explicit error checking
            try:
                print("Attempting to generate PDF...")
                pdf = pdfkit.from_string(
                    rendered_html, 
                    False,  # Don't save to file
                    configuration=config, 
                    options=options
                )
                
                if not pdf:
                    raise ValueError("PDF generation returned None")
                    
                print(f"PDF generated successfully")
                
            except Exception as pdf_error:
                print(f"PDF Generation Error: {str(pdf_error)}")
                st.error(f"PDF Generation Error: {str(pdf_error)}")
                st.error("Additional context: Check if wkhtmltopdf is properly installed and accessible")
                st.stop()

            # After successful PDF generation
            try:
                # Create sanitized filename
                safe_company_name = "".join(x for x in company_details.get('company_name', 'unknown') 
                                          if x.isalnum() or x in (' ', '-', '_'))
                filename = f"risk_assessment_{safe_company_name}_{datetime.now().strftime('%Y%m%d')}.pdf"

                # Upload to Digital Ocean Spaces
                spaces_client = get_spaces_client()
                pdf_buffer = BytesIO(pdf)

                
                spaces_client.upload_fileobj(
                    pdf_buffer,
                    "slateai",
                    f"risk-assessments/{filename}",
                    ExtraArgs={'ACL': 'public-read', 'ContentType': 'application/pdf'}
                )

                # Generate temporary URL for download (valid for 1 hour)
                pdf_url = spaces_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': "slateai",
                        'Key': f"risk-assessments/{filename}"
                    },
                    ExpiresIn=3600  # URL valid for 1 hour

                )

                st.success("PDF generated and stored successfully!")
                st.download_button(
                        label="Download PDF",
                        data=pdf,
                        file_name=filename,
                        mime="application/pdf"
                    )

                # Download button using the temporary URL
                # st.markdown(f"[Download PDF]({pdf_url})", unsafe_allow_html=True)

            except Exception as upload_error:
                st.error("Error uploading to Digital Ocean Spaces")
                st.error(f"Details: {str(upload_error)}")
                
                # Debug information
                st.write("Debug Info:")
                st.write(f"Bucket: {os.getenv('DO_SPACES_BUCKET')}")
                st.write(f"Region: {os.getenv('DO_SPACES_REGION')}")
                st.write(f"Endpoint: {os.getenv('DO_SPACES_ENDPOINT')}")
                
                # Fallback to direct download if upload fails
                st.warning("Falling back to direct download...")
                if pdf:  # Only show download button if PDF was generated
                    st.download_button(
                        label="Download PDF",
                        data=pdf,
                        file_name=filename,
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error("Error in overall process")
            st.error(f"Details: {str(e)}")
            st.info("""
            Troubleshooting Steps:
            1. Verify wkhtmltopdf installation
            2. Check template rendering
            3. Verify environment variables
            4. Check network connectivity
            5. Ensure all required fields are completed
            """)