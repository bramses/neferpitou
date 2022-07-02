import numpy as np
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def transform(inputs, DEBUG=True):

    if DEBUG:
        print(f"--OPENAI-- transforming {inputs}")

    clean_inputs = []
    for input in inputs:
        clean_inputs.append(clean_text(input))
    
    response = openai.Embedding.create(
        input=clean_inputs,
        engine="text-search-ada-doc-001"
    )

    if DEBUG:
        print(response.model)
        print(response.usage)

    return np.array([x.embedding for x in response.data], dtype=np.float32)

def transform_query(inputs, DEBUG=True):
    if DEBUG:
        print(f"--OPENAI-- transforming query {inputs}")
    
    clean_inputs = []
    for inp in inputs:
        clean_inputs.append(clean_text(inp))

    response = openai.Embedding.create(
        input=clean_inputs,
        engine="text-search-ada-query-001"
    )

    if DEBUG:
        print(response.model)
        print(response.usage)

    return np.array([x.embedding for x in response.data], dtype=np.float32)

def clean_text(inp):
    return inp.replace("\n", " ").replace("\r", " ").replace("\t", " ")