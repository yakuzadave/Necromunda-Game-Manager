from typing import List, Optional
import json

from pydantic import BaseModel
from groq import Groq
import os
groq_api_key = os.environ['GROQ_API_KEY']
from rich import print

groq = Groq(api_key=os.environ['GROQ_API_KEY'], base_url=os.environ['GROQ_BASE_URL'])
import requests
import os

headers = {
    "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
    "Content-Type": "application/json",
}

payload = {
    "messages" : [
        {
            "role" : "user",
            "content" : "Hello, I want to create a new gang to use in Necromunda for Escher with a starting point value of 1000 points.  Can you help?"
        }
    ],
    "model" : "llama-3.3-70b-versatile",
}

req = requests.post(url="https://api.groq.com/openai/v1/chat/completions", headers=headers, data=payload)
print(req.text)