import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
from database.database import init_db
import openai
from llm import code_gen

load_dotenv()

db_uri = os.getenv("SQLALCHEMY_APIS_DATABASE_URI")
validate_user_prompt = os.getenv("VALIDATE_USER_PROMPT")

app = Flask(__name__)
db = init_db(db_uri, app)


def get_completion(prompt, model="gpt-3.5-turbo", max_tokens=5000):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model, messages=messages, temperature=0.0, max_tokens=max_tokens
    )

    return response.choices[0].message["content"]


def llm_get_prompt_tasks(service, prompt):
    prompt = f"""
    Given a user prompt your must extract a list of tasks that need to interact with an API  to perform the task the user asked for.


    Example 1:
        Prompt: Give me the list of repositories in GitHub that I contributed and have more than 10 collaborators sorted by number of stars

        Answer:
        Get Authenticated user
        List user repositories
        Get repository collaborators


    Example 2:
        Prompt: Give access to the user polAlv to my  mosaic repository

        Answer:
        Get Authenticated user
        List user repositories
        Get user profile
        Add a repository collaborator

    Reply only with the list, no additional text.


    Prompt: {prompt}
    """

    tasks = get_completion(prompt, model="gpt-4-1106-preview")
    return tasks.split("\n")


def llm_get_prompt_tags(service, user_prompt):
    prompt = f"""
    Given the API for a service and a user prompt reply with the list of tags should be
    used to find the relevant endpoints.


    Example 1:
        Service: Github
        Task: Get Authenticated user

        Method: Get
        Tags: Get user

    Example 2:
        Service: Github
        Task: List user repositories

        Method: Get
        Tags: GET repo details contributors


    Service: {service}
    User prompt: {user_prompt}
    Tags:
    """

    return get_completion(prompt)


def llm_get_task_endpoints(service, task):
    return []


def llm_generate_script(service, token, user_prompt, endpoints):
    pass


def process_user_prompt(service, token, prompt):
    try:
        code_gen(prompt, service, token)
        # TODO: ask the llm if this request makes sense

        # split_in_tasks = llm_get_prompt_tasks(service, prompt)
        # if len(tasks) == 0:
        #     return None, f"No task for the given prompt {prompt}"

        # endpoints = []
        # for task in tasks:
        #     llm_get_endpoints = llm_get_task_endpoints(service, task)
        #     endpoints += llm_get_endpoints

        # code = llm_generate_script(service, token, prompt, endpoints)

        # return code, None

    except Exception as e:
        print(e)
        return None, "Error processing user prompt"

    # Filter relevant endpoints from the database


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/gen-script", methods=["POST"])
def chat():
    data = request.get_json()

    if "service" not in data or data["service"] != "github":
        response = {"error": "Bad parameters: missing or invalid service"}
        return jsonify(response), 400

    if "token" not in data:
        response = {"error": "Bad parameters: missing token"}
        return jsonify(response), 400

    if "prompt" not in data or len(data["prompt"]) == 0:
        response = {"error": "Bad parameters: missing or invalid prompt"}
        return jsonify(response), 400

    service = data["service"]
    token = data["token"]
    prompt = data["prompt"]
    code, error = process_user_prompt(service, token, prompt)
    if error is not None:
        response = {"error": error}
        return jsonify(response), 500

    response = {
        "code": code,
    }

    return jsonify(response)


if __name__ == "__main__":
    debug = os.getenv("DEBUG")
    port = os.getenv("HTTP_PORT")

    app.run(debug=debug, port=port)
