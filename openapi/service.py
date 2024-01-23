import json

class Service():
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.definition = None

    def load_service_data(self):
        with open(self.file_path) as f:
            self.definition = json.load(f)

    def get_service_info(self):
        if self.definition is None:
            self.load_service_data()

        res = {}

        res['name'] = self.name
        res['description'] = self.definition['info']['description']

        res['version'] = self.definition['info']['version']
        res['base_url'] = self.definition['servers'][0]['url']

        return res
    
    def get_service_endpoints(self):
        endpoints = []
        for path, endpoint_dict in self.definition['paths'].items():
            for method, method_dict in endpoint_dict.items():
                endpoint = {}

                endpoint['path'] = path
                endpoint['method'] = method

                endpoint['summary'] = method_dict['summary']
                endpoint['description'] = method_dict['description']

                parameters = []
                if 'parameters' in method_dict:
                    for parameter in method_dict["parameters"]:
                        param = {}

                        # By now skip references
                        # {'$ref': '#/components/parameters/pagination-before'}
                        if len(parameter) == 1:
                            continue

                       
                        param['name'] = parameter['name']

                        if 'type' in parameter['schema']:
                            param['type'] = parameter['schema']['type']
                        else:
                            param['type'] = json.dumps(parameter['schema'])

                        if 'description' in parameter:
                            param['description'] = parameter['description']
                        else:
                            param['description'] = ''

                        if 'required' in parameter:
                            param['required'] = parameter['required']
                        else:
                            param['required'] = False
                            
                        parameters.append(param)
                    
                    endpoint['parameters'] = parameters

                endpoints.append(endpoint)

        return endpoints


