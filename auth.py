auth_info = {
    "seqera": """The API requires an authentication token to be specified in each API request using the Bearer HTTP header.
cURL example: `curl -H "Authorization: Bearer eyJ...YTk0" https://tower.nf/api/workflow`
""",
    "openai": """The API requires an authentication token to be specified in each API request using the Bearer HTTP header.
cURL example: `curl https://api.openai.com/v1/chat/completions   -H "Content-Type: application/json" -H "Authorization: Bearer $OPENAI_API_KEY"   -d '{
`
""",
    "github": """Many REST API endpoints require authentication or return additional information if you are authenticated. Additionally, you can make more requests per hour when you are authenticated.

To authenticate your request, you will need to provide an authentication token with the required scopes or permissions.You can authenticate your request by sending the token in the Authorization header of your request. For example, in the following request, replace YOUR-TOKEN with a reference to your token:

curl --request GET \
--url "https://api.github.com/octocat" \
--header "Authorization: Bearer YOUR-TOKEN" \
--header "X-GitHub-Api-Version: 2022-11-28""",
}
