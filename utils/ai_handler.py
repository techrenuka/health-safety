import os
import json
from openai import OpenAI

# Initialize client with environment variables (recommended for security)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # Prefer environment variable
    organization=os.getenv("OPENAI_ORGANIZATION") # Prefer environment variable
)

ASSISTANT_ID = "asst_bjxEoHCSfmKqNnt1c7DK1oNr"  # Your assistant ID

def get_ai_recommendation(data):
    try:
        # Create a thread with the user's message
        thread = client.beta.threads.create(messages=[
            {
                "role": "user",
                "content": f"Generate safety risk assessment for {data['business_category']} "
                           f"in {data['business_activity']} and {data['potential_hazards']}. "
                           f"Respond in JSON format with keys: "
                           "'risks', 'recommendations'."


            }
        ])

        # Create a run using your assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            instructions="You are a safety risk assessment expert. Respond in valid JSON format."
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

        # Parse and return JSON
        return json.loads(response_content)

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        return {"error": "Invalid JSON response", "raw_response": response_content}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {"error": str(e)}

# Example usage:
if __name__ == "__main__":
    data_sample = {
        "business_category": "construction",
        "business_activity": "high-rise building projects"
    }
    
    result = get_ai_recommendation(data_sample)
    print(json.dumps(result, indent=2))