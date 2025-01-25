# api_calls.py
import requests
import urllib3
import warnings
from ..utils import *
url_family_member_option = get_api_url("configurations/41")
url_loan_entity=get_api_url("configurations/43")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def update_configuration_family_member_option( headers):
    payload_edit_family_member = {
        "value": 0,
        "config": "[\"address\",\"asset\",\"income\",\"liabilities\",\"kyc\",\"cibil\",\"bankdetails\"]"
    }
    response = requests.put(url_family_member_option, headers=headers, json=payload_edit_family_member, verify=False)
    if response.status_code == 200:
        print("Family Member Configuration updated successfully.")
    else:
        print(f"Failed to update Family Member configuration: {response.text}")
    return response

def enable_configuration_family_member_option( headers):
    payload = {"enabled": "true"}
    response = requests.put(url_family_member_option, headers=headers, json=payload, verify=False)
    if response.status_code == 200:
        print("Family Member Configuration enabled successfully.")
    else:
        print(f"Failed to enable Family Member configuration: {response.text}")
    return response
def enable_configuration_loan_entity(headers):
    payload = {"enabled": "true"}
    response = requests.put(url_loan_entity, headers=headers, json=payload, verify=False)
    if response.status_code == 200:
        print("Loan Entity Configuration enabled successfully.")
    else:
        print(f"Failed to enable Loan Entity configuration: {response.text}")
    return response