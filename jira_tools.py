import requests
from requests.auth import HTTPBasicAuth
import json

# ********************** IMPORTANT ***************************
# Define here your JIRA username
USERNAME = ""
# Define your personal API_TOKEN in JIRA (ask chatgpt in case you don't know how to do this) and paste it below
API_TOKEN = ""
# ************************************************************
JIRA_BASE_URL = "https://perzoinc.atlassian.net"
SEARCH_ENDPOINT = f"{JIRA_BASE_URL}/rest/api/2/search"

def get_data_from_jql_query(jql_query, fields_to_retrieve):
    auth_data = HTTPBasicAuth(USERNAME, API_TOKEN)

    payload = {"jql": jql_query} if len(fields_to_retrieve) == 0 \
        else {"jql": jql_query, "fields": fields_to_retrieve}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.request(
        "POST",
        SEARCH_ENDPOINT,
        data=json.dumps(payload),
        headers=headers,
        auth=auth_data
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return []

    return response.json()["issues"]

def get_test_cases_linked_to_issues(issues_jql_query):
    jql_for_issues = 'type in (bug, task)'
    if len(issues_jql_query):
        jql_for_issues += ' AND ' + issues_jql_query

    tc_per_bug = {}
    issues = get_data_from_jql_query(jql_for_issues, ["key", "summary", "status", "reporter"])
    for issue in issues:
        key = issue["key"]
        linked_issue_query = 'issue in linkedIssues(' + key + ')'

        linked_issues = get_data_from_jql_query(linked_issue_query, [])

        for l_issue in linked_issues:
            if l_issue["fields"]["issuetype"]["name"] == 'Xray Test':
                tc_id = l_issue["key"]
                print("Test found for: " + key + ": " + tc_id)
                if tc_id not in tc_per_bug.keys():
                    tc_per_bug[tc_id] = []
                tc_per_bug[tc_id].append(key)
    return tc_per_bug

if __name__ == '__main__':
    # Sanity check on the credentials
    if not len(USERNAME) or not len(API_TOKEN):
        print("You haven't read the important section on top!!")
        exit()

    # Example of getting TCs linked to a specific set of issues"
    discriminant = 'key in (ADMIN-8399,C2-22242,C2-22492,DIRECTORY-1596,GCPM-3344,' \
                   'GCPM-3852,GCPM-3856,GCPM-3863, ADMIN-8234,C2-22242,GCPM-3344,GCPM-3814,BE-6500,EIS-5306,' \
                   'GCPM-3710,GCPM-3711,EIS-5304,EIS-5305,GCPM-3344,GCPM-3689,GCPM-3690,GCPM-3691,GCPM-3692,' \
                   'GCPM-3702,GCPM-3704,GCPM-3705,GCPM-3707,GCPM-3597,GCPM-3633,GCPM-3637,GCPM-3640,GCPM-3641,' \
                   'SRE-9092,ADMIN-7577,ADMIN-7988,GCPM-3344,GCPM-3424,GCPM-3689,SRE-8572,UWH-126)'
    tc_pr_issue = get_test_cases_linked_to_issues(discriminant)

    print("===============================")
    for k, v in tc_pr_issue.items():
        print(str(k), str(v))
    # End of the example"
