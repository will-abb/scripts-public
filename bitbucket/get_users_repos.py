import json

import requests

# executes api calls to bitbucket, there is an equation for credentials and one for paginations


# get token to make requests
def get_token():
    url = "https://bitbucket.org/site/oauth2/access_token"
    client_id = ""
    secret = ""

    data = {"grant_type": "client_credentials"}
    response = requests.post(url, data=data, auth=(client_id, secret))
    return json.loads(response.text)["access_token"]


# gets list of repos: i think this request is too big code 429
def list_repos(page_number=1):
    url = "https://api.bitbucket.org/2.0/repositories/SelectQuote"
    auth_token = get_token()

    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}
    response = requests.request(
        "GET", url, headers=headers, params={"page": page_number}
    )

    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    return response


# get workspace user list
def list_workspace_users(page_number=1):
    url = "https://api.bitbucket.org/2.0/workspaces/SelectQuote/members"
    auth_token = get_token()

    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}
    response = requests.request(
        "GET", url, headers=headers, params={"page": page_number}
    )

    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    return response


# get user list with permissions of users
def list_user_permissions_in_workspace(page_number=1):
    url = "https://api.bitbucket.org/2.0/workspaces/selectquote/permissions"
    auth_token = get_token()

    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}
    response = requests.request(
        "GET", url, headers=headers, params={"page": page_number}
    )

    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    return response


# get particular user info
def get_user(page_number=1):
    url = "https://api.bitbucket.org/2.0/users/62a7447dbf7afc006f3a99bb"
    auth_token = get_token()

    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}
    response = requests.request(
        "GET", url, headers=headers, params={"page": page_number}
    )

    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    return response


# this is for pagination through results
# replace the command after 'response =' with the command you want to paginate through
def get_all_pages():
    # reseting file then appending results
    wfile = open("results.json", "w")
    wfile.write("{")
    wfile.close()
    wfile = open("results.json", "a")

    # first call needed since it no 'next' exists
    response = list_user_permissions_in_workspace()
    fmt_response = json.dumps(
        json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
    )
    print(fmt_response)
    wfile.write(fmt_response)

    page_number = 1
    # loop must be in format response
    while "next" in fmt_response:
        page_number += 1
        response = list_user_permissions_in_workspace(page_number)
        fmt_response = json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        )

        print(fmt_response)
        wfile.write(fmt_response)
        wfile.write(",")

    wfile.write("}")
    wfile.close()


get_all_pages()
# get_user()
# list_workspace_users()
# list_repos()
# get_user_permission()
# list_user_permissions_in_workspace()
