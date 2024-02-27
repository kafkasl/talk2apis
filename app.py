import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
from database.database import init_db
import uuid
import docker

from ai import llm

load_dotenv()

db_uri = os.getenv("SQLALCHEMY_APIS_DATABASE_URI")
validate_user_prompt = os.getenv("VALIDATE_USER_PROMPT")

app = Flask(__name__)
db = init_db(db_uri, app)


async def process_user_prompt(service, token, prompt):
    try:
        endpoints = await llm.get_task_endpoints(
            service=service, prompt=prompt, return_best_only=False
        )

        auth_info = await llm.get_auth_info(
            description=prompt, service=service, use_llm=False
        )

        code = await llm.generate_task_code(
            description=prompt,
            auth_details=auth_info,
            endpoints=endpoints,
            token=token,
        )

        response = {"code": code, "endpoints": endpoints}

        return response, None
    except Exception as e:
        return None, {"error": e}


# def process_user_prompt(service, token, prompt):
#     try:
# generate_service_call(prompt, service, token)
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

# except Exception as e:
#     print(e)
#     return None, "Error processing user prompt"

# Filter relevant endpoints from the database


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")  # Serve the FAQ content on this route


@app.route("/gen-script", methods=["POST"])
async def chat():
    data = request.get_json()

    if "service" not in data:
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
    response, error = await process_user_prompt(
        prompt=prompt, service=service, token=token
    )
    # code, error = await generate_service_call(prompt, service, token)
    if error is not None:
        print(f"Error: {error}")
        response = {"error": error}
        return jsonify(response), 500

    return jsonify(response)


@app.route("/run_code", methods=["POST"])
def run_code():
    code = request.json.get("code")

    scripts_folder = "user-scripts"
    # Check if the directory exists
    if not os.path.exists(scripts_folder):
        # If not, create the directory
        os.makedirs(scripts_folder)

    # Generate a random file name
    filename = f"{scripts_folder}/temp_script_{uuid.uuid4().hex}.py"

    # Save the code to a file
    with open(filename, "w") as file:
        file.write(code)

    try:
        # Create a Docker client
        client = docker.from_env()

        # Run the script in a Docker container
        result = client.containers.run(
            "talk2apis-code-runner",  # Use the new Docker image
            f"python {filename}",
            remove=True,
            volumes={os.environ["HOST_PROJECT_PATH"]: {"bind": "/app", "mode": "rw"}},
        )

        # Capture standard output
        output = result.decode("utf-8")
        error = None

    except Exception as e:
        output = None
        error = str(e)

    return jsonify({"output": output, "error": error})


if __name__ == "__main__":
    debug = os.getenv("DEBUG")
    port = os.getenv("HTTP_PORT")

    app.run(debug=debug, port=port, use_reloader=False)
