


select_endpoint = f"""
    Instruct:

    Given a user porpmt and the description of multiple endpoints, select the ones that should be called to resolve the prompt.
    If no endpoint is relevant, reply with NONE.
    
    Examples:
        user prompt: "Give me the open issues in the repository mosaic"
        endpoint:
            Method: Get
            Path: /repos/{{owner}}/{{repo}}/issues
            Summary: List issues
            Description: List issues in a repository

        answer: YES

        

        user prompt: "Give me the open issues in the repository myorg/myrepo"
        endpoint:
            Method: Get
            Path: /user
            Summary: Get the authenticated user
            Description: Get the authenticated user

        answer: NO
    
        
    Remarks: If the endpoint is relevant to solve the user prompt reply ONLY with a YES, otherwise reply ONLY with NO.
    Reply with only one word: 'YES' or 'NO'. DO NOT ADD ANY EXTRA TEXT.
    
    user prompt: '{user_prompt}'
    endpoint:
        Method: {endpoint['method']}
        Path: {endpoint['path']}
        Summary: {endpoint['summary']}
        Description: {endpoint['description']}

    answer:

    OUTPUT: 
"""