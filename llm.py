from jinja2 import Template
from typing import Dict

# from alpha_codium.llm.ai_handler import AiHandler
from embeddings import gen_embedding, cosine_similarity
from database.services import APIEndpoints


def rank_closest_embeddings(target_embedding, embeddings_dict, top_k=100):
    """
    Compares the target embedding with a set of embeddings and returns the top k matches.

    Args:
    - target_embedding: The embedding to compare against.
    - embeddings_dict: A dictionary mapping endpoints to embeddings.
    - top_k: The number of top matches to return.

    Returns:
    A list of tuples (endpoint, similarity score) sorted by similarity score in descending order.
    """
    match_scores = []

    # Calculate similarity for each endpoint
    for endpoint, embedding in embeddings_dict.items():
        similarity = cosine_similarity(target_embedding, embedding)
        match_scores.append((endpoint, similarity))

    # Sort matches by similarity in descending order
    sorted_matches = sorted(match_scores, key=lambda x: x[1], reverse=True)
    # Return top k matches or all matches
    return sorted_matches if top_k is None else sorted_matches[:top_k]


def render(template: str, args: Dict) -> str:
    t = Template(template)
    return t.render(args)


# def ai_self_reflection(description: str, model: str = "gpt-4") -> str:
#     temperature = 0.2
#     frequency_penalty = 0.1
#     system_prompt = """The self-reflection must cover every aspect of the request. Pay attention to small details and nuances in the request description.
#     """
#     user = """You are given a problem description.
#     problem description:
#     =====
#     {{ description }}
#     =====


#     Your goals is to write down which are the required outputs of this task.

#     The output must be a YAML object equivalent to type $ProblemOutput and they will be generated by python code, according to the following Pydantic definitions:
#     =====
#     Class Output(BaseModel):
#         type: str = Field(description="python type of the output")
#         name: str = Field(description="Name of the output")
#         explanation: str = Field(description="Short explanation of what this output is.")


#     class ProblemOutput(BaseModel):
#         outputs: list[Output] = Field(description="List of required outputs of the problem.")
#     =====

#     Example YAML output:
#     ```yaml
#     outputs:
#     - type: |
#         ...
#     name: |
#         ..
#     explanation: |
#         ..
#     ...
#     ```

#     Answer:
#     ```yaml
#     """
#     ai_handler = AiHandler()

#     user_prompt = render(user, {"description": description})
#     outputs_def_response, finish_reason = await ai_handler.chat_completion(
#         model=model,
#         system=system_prompt,
#         user=user_prompt,
#         temperature=temperature,
#         frequency_penalty=frequency_penalty,
#     )
#     return outputs_def_response


# def ai_generate_code(
#     description: str, outputs: str, endpoint_documentation: str, model: str = "gpt-4"
# ) -> str:
#     temperature = 0.2
#     frequency_penalty = 0.1
#     system_prompt = """"""

#     code_prompt = """You are given a problem description, the required outputs of this task, and the documentation of the endpoint to be used.

#     problem description:
#     =====
#     {{ description }}
#     =====

#     required outputs:
#     =====
#     {{ outputs }}
#     =====

#     endpoint documentation:
#     =====
#     {{ endpoint_documentation }}
#     =====

#     Your goal is to generate a valid Python code that correctly solves the problem and retrieves all the outputs from the endpoint. Always use pagination to retrieve all data.

#     Guidelines:
#     - Make sure to include all the necessary module imports, properly initialize the variables, and address the problem constraints.
#     - The code needs to be self-contained, and executable as-is.
#     - The output format must match the required outputs.
#     - Assume that the github token is already defined and available in the environment variable GITHUB_API_TOKEN.


#     The generated code must follow this structure:
#     ```
#     def f1(...):
#         ...
#         return ...

#     def f2(...):
#         ...
#         return ...
#     ...

#     if __name__ == "__main__":
#         ...
#     ```
#     The output should be printed without additional words using the 'print()' method.


#     Answer:
#     ```python
#     """

#     ai_handler = AiHandler()

#     user_prompt = render(
#         code_prompt,
#         {
#             "description": description,
#             "outputs": outputs,
#             "endpoint_documentation": endpoint_documentation,
#         },
#     )
#     code_response, finish_reason = await ai_handler.chat_completion(
#         model=model,
#         system=system_prompt,
#         user=user_prompt,
#         temperature=temperature,
#         frequency_penalty=frequency_penalty,
#     )

#     return code_response


def code_gen(prompt, service, token):
    # Example usage
    service = "GitHub v3 REST API"  # Replace with your actual service name
    embeddings = APIEndpoints.get_embeddings_for_service(service)

    prompt_embedding = gen_embedding(prompt)
    ranked_paths = rank_closest_embeddings(prompt_embedding, embeddings)
    path = ranked_paths[0][0]  # get first element, and the path from it
    print(path)
    # outputs = ai_self_reflection(description)
    # code = ai_generate_code(description, outputs, "")
    # endpoint_definition = endpoints_details[service]["paths"]["/user/subscriptions"]
    # resolved_definition = resolve_refs(endpoint_definition, endpoints_details[service])


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
