import os
import logging
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API Setup
openai.api_key = os.environ.get("OPENAI_API_KEY")

class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 100

@app.post("/generate/")
async def generate(request: GenerationRequest):
    prompt = request.prompt
    # Convert max_length to tokens as needed, here we use a rough max tokens
    # GPT-3.5-Turbo can handle up to ~4k tokens context, we can just use a safe number
    max_tokens = min(request.max_length, 300)

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who answers questions based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3,
            top_p=0.9
        )
        answer = completion.choices[0].message.content.strip()
        logger.info(f"Generated Text: {answer}")
        return {"generated_text": answer}
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with OpenAI API.")
