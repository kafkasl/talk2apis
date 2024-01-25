# from dotenv import load_dotenv, find_dotenv
import json
import numpy as np
from typing import List, Dict

from openai import OpenAI
from tiktoken import encoding_for_model


def to_binary(embedding: np.ndarray) -> bytes:
    return embedding.tobytes()


def to_array(binary: bytes) -> np.ndarray:
    return np.frombuffer(binary)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def count_tokens(input_string: str, model: str) -> int:
    """
    Counts the number of tokens in a given string.

    Args:
    - input_string: The string to encode and count tokens.

    Returns:
    The number of tokens in the input string.
    """
    encoder = encoding_for_model(model)
    return len(encoder.encode(input_string, disallowed_special=()))


def gen_embedding(text: str, model="text-embedding-ada-002", **kwargs) -> List[float]:
    client = OpenAI()
    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")
    MAX_TOKENS = 8192
    tokens = count_tokens(text, model)
    if tokens > MAX_TOKENS:
        raise ValueError(
            f"tokens exceed maximum length ({tokens} > {MAX_TOKENS}) for model {model}."
        )
    return np.array(
        client.embeddings.create(input=[text], model=model, **kwargs).data[0].embedding
    )


def generate_embeddings(endpoints: Dict) -> Dict:
    def get_embedding(endpoint):
        return endpoint["path"], gen_embedding(endpoint)

    return dict(map(get_embedding, endpoints))


def save_embeddings_to_file(embeddings, file_path):
    with open(file_path, "w") as file:
        json.dump(embeddings, file)
