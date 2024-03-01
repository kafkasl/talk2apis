import json
from ai.embeddings import get_embedding, to_binary
from tqdm import tqdm
import numpy as np
import yaml
import os


def resolve_refs(
    path,
    definition,
    schema,
    parent_refs=None,
    only_schema_paths=False,
):
    """
    In OpenAPI, $ref is used to reference a definition elsewhere in the document,
    promoting reusability and DRY principles.

    The context of $ref matters:
    - In a schema object, it references another schema definition, defining the data structure.
    - In an examples object, it references an example of a real-world value for the schema.

    Circular references within schemas can lead to infinite loops.
    However, circular references within examples are less problematic as they don't affect the data structure.

    The resolve_refs function should (BUT IS NOT) treat $ref keys differently based on their context
    (schema or examples) to handle these scenarios.
    """
    if parent_refs is None:
        parent_refs = set()

    if isinstance(definition, dict):
        # we should be resolving only references in schema, but currently we are doing
        # only in parameters (which don't include exmaples) so we can skip checking for
        # the schema keyword
        if "$ref" in definition and (not only_schema_paths or "schema" in path):
            ref_path = definition["$ref"]
            if ref_path in parent_refs:
                print(f"Circular reference detected: {ref_path}")
                return ref_path
            ref_path_parts = ref_path.split("/")[
                1:
            ]  # Split and ignore the first '#' element
            ref_definition = schema
            for part in ref_path_parts:
                ref_definition = ref_definition[part]
            resolved_definition = resolve_refs(
                path + [ref_path],
                ref_definition,
                schema,
                parent_refs | {ref_path},
                only_schema_paths,
            )  # Recursively resolve nested references
            return resolved_definition
        else:
            return {
                key: resolve_refs(
                    path + [key], value, schema, parent_refs, only_schema_paths
                )
                for key, value in definition.items()
            }
    elif isinstance(definition, list):
        return [
            resolve_refs(
                path + [str(index)], item, schema, parent_refs, only_schema_paths
            )
            for index, item in enumerate(definition)
        ]
    else:
        return definition


class Service:
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.definition = None

    def load_service_data(self):
        file_extension = os.path.splitext(self.file_path)[1].lower()

        with open(self.file_path, "r") as f:
            if file_extension == ".json":
                self.definition = json.load(f)
            elif file_extension in [".yml", ".yaml"]:
                self.definition = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported file format")

    def get_service_info(self):
        if self.definition is None:
            self.load_service_data()

        res = {}

        res["name"] = self.name
        res["description"] = self.definition.get("info", {}).get("description", "")

        res["version"] = self.definition.get("info", {}).get("version", "")
        res["base_url"] = (self.definition.get("servers", [{}])[0]).get("url", "")

        return res

    def parse_parameters(self, path, method_dict):
        parameters = []
        if "parameters" not in method_dict:
            return parameters

        for parameter in method_dict["parameters"]:
            param = {}

            if len(parameter) == 1:
                continue

            param["name"] = parameter["name"]

            if "type" in parameter["schema"]:
                param["type"] = parameter["schema"]["type"]
            else:
                param["type"] = json.dumps(parameter["schema"])

            if "description" in parameter:
                param["description"] = parameter["description"]
            else:
                param["description"] = ""

            if "required" in parameter:
                param["required"] = parameter["required"]
            else:
                param["required"] = False

            parameters.append(param)

        return parameters

    def get_service_endpoints(self):
        endpoints = []
        for path, endpoint_dict in tqdm(
            list(self.definition["paths"].items()), desc="Processing endpoints"
        ):
            # if path != "/pipelines":
            #     continue
            for method, method_dict in endpoint_dict.items():
                # if method != "get":
                #     continue
                endpoint = {}

                endpoint["path"] = path
                endpoint["method"] = method

                endpoint["summary"] = method_dict.get("summary", "")
                endpoint["description"] = method_dict.get("description", "")

                # let's resolve at least the parameters if they exist
                if "parameters" in method_dict:
                    method_dict["parameters"] = resolve_refs(
                        path.split("/"), method_dict["parameters"], self.definition
                    )

                if "responses" in method_dict:
                    method_dict["responses"] = resolve_refs(
                        path.split("/"),
                        method_dict["responses"],
                        self.definition,
                        only_schema_paths=True,
                    )

                endpoint["definition"] = json.dumps(method_dict)

                try:
                    endpoint["embedding"] = to_binary(
                        get_embedding(endpoint["definition"])
                    )
                except ValueError as e:
                    print(f"skip embedding {path}: {e}")
                    endpoint["embedding"] = to_binary(np.array([]))

                endpoints.append(endpoint)

        return endpoints
