import numpy as np
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def transform(inputs):
    response = openai.Embedding.create(
        input=inputs,
        engine="text-search-ada-doc-001"
    )

    return np.array([x.embedding for x in response.data], dtype=np.float32)

def transform_query(inputs):
    response = openai.Embedding.create(
        input=inputs,
        engine="text-search-ada-query-001"
    )

    return np.array([x.embedding for x in response.data], dtype=np.float32)