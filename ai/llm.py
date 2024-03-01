import yaml

from jinja2 import Template
from typing import Dict, List, Tuple
from .handler import AiHandler
from auth import auth_info
from openai import OpenAI
import json

from database.services import APIEndpoint
from ai.embeddings import get_embedding, cosine_similarity, count_tokens

DEFAULT_MODEL = "gpt-4"
ai_handler = AiHandler()

def clip_to_context(text: str, clip_ratio: float= 0.8, model=DEFAULT_MODEL, **kwargs) -> str:
    client = OpenAI()
    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")
    MAX_TOKENS = 8192
    tokens = count_tokens(text, model)
    # clip ratio represents how much of the context window the text can occupy
    while tokens > MAX_TOKENS * clip_ratio:
        # Calculate the ratio of current tokens to the maximum allowed tokens
        ratio = tokens / MAX_TOKENS
        # Determine the amount of text to keep based on the clip ratio and the calculated token ratio.
        # This uses the length of the text as a proxy for token count, adjusting the length to keep
        # within the desired token limit. The assumption is that reducing the text by this ratio
        # will similarly reduce the token count to within the target range.
        amount_to_keep = len(text) * clip_ratio / ratio
        text = text[:int(amount_to_keep)]
        tokens = count_tokens(text, model)
    return text

def render(template: str, args: Dict) -> str:
    t = Template(template)
    return t.render(args)


def rank_closest_embeddings(
    target_embedding: str, embeddings: List[Dict], top_k: int = 100
) -> List[Tuple[Dict, float]]:
    """
    Compares the target embedding with a set of embeddings and returns the top k matches.

    Args:
    - target_embedding: The embedding to compare against.
    - embeddings: A list of (endpoint, embedding) tuples.
    - top_k: The number of top matches to return.

    Returns:
    A list of tuples (endpoint, similarity score) sorted by similarity score in descending order.
    """
    match_scores = []

    # Calculate similarity for each endpoint
    for endpoint, embedding in embeddings:
        similarity = cosine_similarity(target_embedding, embedding)
        match_scores.append((endpoint, similarity))

    # Sort matches by similarity in descending order
    sorted_matches = sorted(match_scores, key=lambda x: x[1], reverse=True)
    # Return top k matches or all matches
    return sorted_matches if top_k is None else sorted_matches[:top_k]


async def self_reflection(description: str, model: str = DEFAULT_MODEL) -> str:
    temperature = 0.2
    frequency_penalty = 0.1
    system_prompt = """The self-reflection must cover every aspect of the request. Pay attention to small details and nuances in the request description.
    """
    user = """You are given a problem description.
    problem description:
    =====
    {{ description }}
    =====


    Your goals is to write down which are the required outputs of this task.

    The output must be a YAML object equivalent to type $ProblemOutput and they will be generated by python code, according to the following Pydantic definitions:
    =====
    Class Output(BaseModel):
        type: str = Field(description="python type of the output")
        name: str = Field(description="Name of the output")
        explanation: str = Field(description="Short explanation of what this output is.")


    class ProblemOutput(BaseModel):
        outputs: list[Output] = Field(description="List of required outputs of the problem.")
    =====

    Example YAML output:
    ```yaml
    outputs:
    - type: |
        ...
    name: |
        ..
    explanation: |
        ..
    ...
    ```

    Answer:
    ```yaml
    """
    ai_handler = AiHandler()

    user_prompt = render(user, {"description": clip_to_context(description)})
    outputs_def_response, finish_reason = await ai_handler.chat_completion(
        model=model,
        system=system_prompt,
        user=user_prompt,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
    )
    return outputs_def_response


async def get_task_endpoints(
    prompt: str,
    service: str,
    return_best_only: bool = True,
    model: str = DEFAULT_MODEL,
) -> List[dict]:
    task_endpoints_prompt = """You are given a task description, and a list of candidate endpoints to solve the task. The endpoints in the list follow the format '[METHOD]endpoint/path: description'. Each endpoint is separated by |||. The description might be empty. The endpoints are ranked by similarity to the task description.

    problem description:
    =====
    {{ description }}
    =====

    endpoints:
    =====
    {{ endpoints }}
    =====


    Your goal is to return a single endpoint required to perform the task, return a list with a single element.
    Include only the endpoint path in your response, no description nor method.

    The output must be a YAML object equivalent to type $Endpoints and they will be generated by python code, according to the following Pydantic definitions:
    =====
    class Endpoints(BaseModel):
        outputs: list[str] = Field(description="List of paths of the required endpoints to solve the task.")
    =====

    Example YAML output:
    ```yaml
    endpoints:
    - /path/to/endpoint1
    - /path/to/endpoint2
    - /path/to/endpoint3
    ```

    Answer:
    ```yaml
    """

    try:
        embeddings = APIEndpoint.get_embeddings_for_service(service)
        prompt_embedding = get_embedding(prompt)
        ranked_endpoints = rank_closest_embeddings(
            prompt_embedding, embeddings, top_k=40
        )
    except Exception as e:
        print(f"Error retrieving endpoint info: {e}")
        return []

    if len(ranked_endpoints) < 1:
        return []

    print("\n".join([e.path for e, _ in ranked_endpoints]))
    if return_best_only:
        best = ranked_endpoints[0][0]
        return [best.to_dict()]

    # We could add the parametesrs also to the request, but then they might become too large
    params = {
        "description": prompt,
        "endpoints": '|||'.join([f"[{e.method}]{e.path}: {e.description}" for e, _ in ranked_endpoints])
    }

    user_prompt = render(task_endpoints_prompt, params)
    endpoints_response, finish_reason = await ai_handler.chat_completion(
        model=DEFAULT_MODEL,
        system="",
        user=user_prompt,
        temperature=0.0,
    )

    endpoints_paths = yaml.safe_load(endpoints_response.lstrip('```yaml\n').rstrip('\n```'))["endpoints"]
    endpoints_defs = [
        e.to_dict() for e, _ in ranked_endpoints if e.path in endpoints_paths
    ]
    return endpoints_defs


async def get_auth_info(
    description: str,
    endpoints_definition: str = [],
    service: str = "",
    use_llm=False,
    model: str = DEFAULT_MODEL,
) -> str:
    auth_prompt = """You are given a task description, the definition of an API endpoint required to solve the task (or part of it), the description of the auth needed by the service (if available).
    problem description:

    =====
    {{ description }}
    =====

    API endpoints definition:
    =====
    {{ endpoints_definition }}
    =====

    service authentication details:
    =====
    {{ auth_details }}
    =====

    Your goal is to decide whether it is necessary to use authentication in this endpoint. Answer as follows:
    * If authentication is needed, provide the necessary details to authenticate the request.
    * If no authentication is needed, reply "no authentication needed"

    """

    if not use_llm:
        if service in auth_info:
            return auth_info[service]
        else:
            # General instructions for using bearer token authentication
            return "To authenticate the request, include a header with 'Authorization: Bearer <YOUR_TOKEN_HERE>'. Replace <YOUR_TOKEN_HERE> with your actual token."

    user_prompt = render(
        auth_prompt,
        {
            "description": description,
            "endpoint_definition": clip_to_context(endpoints_definition),
        },
    )

    auth_response, finish_reason = await ai_handler.chat_completion(
        model=model,
        system="",
        user=user_prompt,
        temperature=0,
    )

    return auth_response


async def generate_task_code(
    description: str,
    endpoints: List[dict],
    auth_details: str,
    token: str,
    model: str = DEFAULT_MODEL,
) -> str:
    code_prompt = """You are given a problem description, the definition of the endpoint(s), and the token and details needed to authenticate.

    problem description:
    =====
    {{ description }}
    =====

    endpoints definition:
    =====
    {{ endpoints_definition }}
    =====

    service authentication details:
    =====
    {{ auth_details }}
    =====

    auth token:
    =====
    {{ token }}
    =====

    Your goal is to generate a valid Python code that correctly solves the problem.
    Guidelines:
    - Make sure to include all the necessary module imports, properly initialize the variables, and address the problem constraints.
    - The code needs to be self-contained, and executable as-is.
    - The output format must match the required outputs.
    - Make sure to retrieve all pages in requests that return paginated results.
    - Do not include any documentation

    The generated code must follow this structure:
    ```
    def f1(...):
        ...
        return ...

    def f2(...):
        ...
        return ...
    ...

    if __name__ == "__main__":
        ...
    ```
    The output should be printed without additional words using the 'print()' method.


    Answer:
    ```python
    """

    user_prompt = render(
        code_prompt,
        {
            "description": clip_to_context(description, 0.5),
            "token": token if token else "no token provided",
            "auth_details": auth_details,
                "endpoints_definition": clip_to_context('\n'.join([json.dumps(endpoint) for endpoint in endpoints]), 0.3),
        },
    )

    code_response, finish_reason = await ai_handler.chat_completion(
        model=model,
        system="",
        user=user_prompt,
        temperature=0.2,
        frequency_penalty=0.1,
    )

    code = code_response.lstrip('```python\n').rstrip('```')
    if '```' in code:
        code = code.split('```')[0]
    return code

async def generate_service_call(prompt, service, token):
    # outputs = await self_reflection(prompt)

    try:
        # 1. Get the most probable endpoints needed to solve the problem
        embeddings = APIEndpoint.get_embeddings_for_service(service)
        prompt_embedding = get_embedding(prompt)
        ranked_endpoints = rank_closest_embeddings(prompt_embedding, embeddings)

        # use the most similar endpoint
        endpoint_definition = ranked_endpoints[0][0].definition


        auth_details = auth_info[service]
    except Exception as e:
        print(f"Error retrieving endpoint info: {e}")
        endpoint_definition = ""
        auth_details = ""

    code = await generate_task_code(
        prompt,
        endpoint_definition=endpoint_definition,
        token=token,
        auth_details=auth_details,
    )

    return code, None


# asyncio.run(main())

# import os


# import requests


# def get_watched_repos(user):
#     token = os.getenv("GITHUB_API_TOKEN")
#     headers = {"Authorization": f"token {token}"}
#     url = f"https://api.github.com/users/{user}/subscriptions"
#     watched_repos = []

#     while url:
#         response = requests.get(url, headers=headers)
#         data = response.json()
#         for repo in data:
#             watched_repos.append(repo["full_name"])
#         if "next" in response.links.keys():
#             url = response.links["next"]["url"]
#         else:
#             url = None

#     return watched_repos


# if __name__ == "__main__":
#     watched_repositories = get_watched_repos("kafkasl")
#     print(watched_repositories)
