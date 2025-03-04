# Health & Safety Risk Assessment Generator

A Streamlit application that helps businesses create professional health and safety risk assessments.

## Features

- AI-powered risk assessment generation
- Customizable hazard identification and control measures
- PDF generation with professional formatting
- Digital Ocean Spaces integration for document storage

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install wkhtmltopdf (required for PDF generation):
   - Windows: Download from https://wkhtmltopdf.org/downloads.html
   - Mac: `brew install wkhtmltopdf`
   - Linux: `sudo apt-get install wkhtmltopdf`

4. Create a `.env` file with your API keys (see `.env.example`)

5. Run the application:
   ```
   streamlit run Home.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORGANIZATION=your_openai_org_id

DO_SPACES_KEY=your_digital_ocean_spaces_key
DO_SPACES_SECRET=your_digital_ocean_spaces_secret
DO_SPACES_BUCKET=your_bucket_name
DO_SPACES_REGION=your_region
DO_SPACES_ENDPOINT=https://your_region.digitaloceanspaces.com
```

## Project Structure

- `Home.py` - Main application entry point
- `pages/` - Streamlit pages for multi-step process
- `utils/` - Utility functions for AI, PDF generation, and storage
- `health.html` - HTML template for PDF generation

## Dependencies

- streamlit - Web application framework
- pdfkit - PDF generation
- jinja2 - HTML templating
- boto3 - AWS/Digital Ocean Spaces integration
- openai - OpenAI API integration
- fpdf - Alternative PDF generation
- pandas - Data handling