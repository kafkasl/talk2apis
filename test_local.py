import requests
import json

from openapi.service import Service

def get_completion(prompt, model="phi"):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt
    }

    response = requests.post(url, data=json.dumps(data))

    # Split the response content into separate JSON objects
    json_objects = response.text.split('\n')

    # Decode each JSON object separately
    data = [json.loads(json_object) for json_object in json_objects if json_object]

    response_string = ' '.join([item['response'] for item in data if 'response' in item])

    return response_string

if __name__ == '__main__':
    service_name = 'github'
    file = 'openapi/definitions/github.json'

    # Create a new Service object
    service = Service(service_name, file)

    service_info = service.get_service_info()

    user_prompt = f"""
    Give me the list of repositories that I contributed to that have more than 10 contributors sorted by stars in decresing order
    """

    plan = f"""
    What endpoints from the github API would you say that are relevant to solve the following user prompt?

    user prompt: '{user_prompt}'

    Reply with an execution plan for completing the task and what kind of endpoints would you use for it.
    """


    code = f"""
    Given this user prompt and execution plan, write the python script that would solve the user prompt.

    user_prompt: '{user_prompt}'
    plan: 'To  solve  this  user  prompt ,  we  can  follow  these  steps : 
 
    1 .  Connect  to  the  GitHub  API  using  its  credentials . 
    2 .  Make  a  GET  request  to  the  endpoint  that  returns  repositories  with  more  than  10  contributors . 
    3 .  Filter  the  list  of  repositories  by  stars  in  decreasing  order  ( s orted  from  high  to  low ). 
    4 .  Return  the  filtered  list  of  repositories  as  the  response . 
    
    To  achieve  this ,  we  will  use  the  following  end points : 
    
    1 .  To  connect  to  the  GitHub  API ,  you 'll  need  an  access  token .  You  can  obtain  one  through  the  " G it Hub  Personal  Access  Token "  feature  on  their  website  by  providing  your  email  address  and  a  password .  This  endpoint  is  available  at  https :// api . github . com / personal / access _ token . 
    2 .  To  get  the  list  of  repositories  with  more  than  10  contributors ,  you  can  use  the  following  endpoint :  https :// api . github . com / re pos it ories / me / cont ribut ors ? since = all & per _ page = 100 .  In  this  case ,  " me "  is  the  GitHub  personal  access  token  and  it  will  return  a  page  of  100  repositories  for  each  call ,  sorted  by  the  number  of  contributors . 
    3 .  To  filter  the  list  by  stars  in  decreasing  order ,  you  can  use  the  following  endpoint :  https :// api . github . com / re pos it ories / {{ owner }} / {{ re po _ name }} / cont ribut ors ? order = stars & direction = desc .  This  will  return  a  page  of  100  repositories  with  their  contributors ,  sorted  by  the  number  of  stars  in  descending  order . 
    4 .  To  get  the  final  list  of  repositories  after  filtering ,  you  can  use  the  following  endpoint :  https :// api . github . com / re pos it ories / {{ owner }} / {{ re po _ name }} / cont ribut ors ? order = stars & direction = desc & per _ page = 100 . 
    
    By  combining  these  end points  and  their  parameters ,  we  can  create  an  execution  plan  to  solve  the  user  prompt  as  follows : 
    
    1 .  Connect  to  the  GitHub  API  with  your  access  token . 
    2 .  Make  a  GET  request  to  the  endpoint  ` https :// api . github . com / re pos it ories / me / cont ribut ors ? since = all & per _ page = 100 `. 
    3 .  Iter ate  through  each  page  of  repositories  obtained  in  step  2 . 
    4 .  For  each  repository ,  make  a  GET  request  to  the  endpoint  ` https :// api . github . com / re pos it ories / {{ owner }} / {{ re po _ name }} / cont ribut ors ? order = stars & direction = desc & per _ page = 100 `. 
    5 .  Extract  the  list  of  repositories  with  more  than  10  contributors  from  step  4  and  store  them  in  a  collection  ( e . g .,  a  list  or  an  array ). 
    6 .  Sort  the  collected  list  by  stars  in  descending  order . 
    7 .  Return  the  sorted  list  of  repositories  as  the  response . '

    
 

    Make sure you do not use any external library other than 'requests', just the standard library.
    """

    resp = get_completion(code)

    print(resp)

    # for endpoint in service.get_service_endpoints():
  

    #     prompt = f"""
    #         We need to decide if the following endpoint is relevant to solve the user prompt.
    #         It does not need to satisfy the user prompt, it just needs to be relevant to solve it.

    #         user prompt: '{user_prompt}'
    #         endpoint: '{endpoint["summary"]}. {endpoint["description"]}'

    #         Reply with a short sentence of what do you thik this endpoint is about and end up the sentence with
    #         a YES or NO. For example:

    #         This endpoint is about getting the authenticated user. YES
    #     """

    #     resp = get_completion(prompt)

    #     if 'YES' in resp or 'Yes' in resp or 'yes' in resp:
    #         print(f"{endpoint['summary']} {resp}")
            