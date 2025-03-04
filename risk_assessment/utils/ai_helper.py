import os
import json
from openai import OpenAI
from django.conf import settings

# Initialize client with settings from Django settings
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    organization=settings.OPENAI_ORGANIZATION
)

def get_ai_recommendation(data):
    try:
        # Create a thread with the user's message
        thread = client.beta.threads.create(messages=[
            {
                "role": "user",
                "content": f"Generate safety risk assessment for {data['category']} "
                           f"in {data['activity']}. "
                           f"Include potential hazards: {data.get('potential_hazards', 'None specified')}. "
                           f"Respond with a JSON object containing an 'assessments' array with objects having these keys: "
                           "'Hazard', 'Severity', 'Probability', 'Persons at Risk', 'Controls to Minimise Risk'."
            }
        ])

        # Create a run using your assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=settings.OPENAI_ASSISTANT_ID,
            instructions="You are a safety risk assessment expert. Respond in valid JSON format with an 'assessments' array."
        )

        # Wait for completion (simple version - consider adding timeout in production)
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        if run.status == "failed":
            return {"error": "AI processing failed"}

        # Get the latest response
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="asc"
        )

        # Extract the JSON response from the assistant
        response_content = messages.data[-1].content[0].text.value
        
        # Clean up the response to extract just the JSON part
        if "```json" in response_content:
            json_start = response_content.find("```json") + 7
            json_end = response_content.rfind("```")
            response_content = response_content[json_start:json_end].strip()

        # Parse and return JSON
        return json.loads(response_content)

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Raw response: {response_content}")
        # Fallback with dummy data if JSON parsing fails
        return {
            "assessments": [
                {
                    "Hazard": "Example hazard (AI response error)",
                    "Severity": "Medium",
                    "Probability": "Low",
                    "Persons at Risk": "Employees",
                    "Controls to Minimise Risk": "Please try again or enter manually"
                }
            ]
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {"error": str(e)}