import json
import os
import requests

from dotenv import load_dotenv

BASE_AUTH_URL = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"
BASE_API_URL = "https://api.sase.paloaltonetworks.com"


HEADERS = {
    "Accept": "application/json",
    "PANW-Region": "americas",
    "Content-Type": "application/json",
}

AUTH_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

load_dotenv()
TSG_ID = os.environ.get("TSG_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
SECRET_ID = os.environ.get("SECRET_ID")


def create_token():
    auth_url = f"{BASE_AUTH_URL}?grant_type=client_credentials&scope:tsg_id:{TSG_ID}"

    token = requests.request(
        method="POST",
        url=auth_url,
        headers=AUTH_HEADERS,
        auth=(CLIENT_ID, SECRET_ID),
    ).json()
    HEADERS.update({"Authorization": f'Bearer {token["access_token"]}'})


def get_unique_devices():
    url = f"{BASE_API_URL}/insights/v3.0/resource/query/users/agent/unique_device_connections_list"
    payload = json.dumps(
        {
            "filter": {
                "rules": [
                    {
                        "property": "platform_type",
                        "operator": "equals",
                        "values": ["prisma_access"],
                    }
                ]
            }
        }
    )
    try:
        response = requests.request("POST", url, headers=HEADERS, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def add_device_to_quarantine(device_id):
    url = f"{BASE_API_URL}/config/objects/v1/quarantined-devices"
    payload = json.dumps(
        {
            "host_id": device_id
        }
    )
    requests.request("POST", url, headers=HEADERS, data=payload)

if __name__ == "__main__":
    create_token()
    username = input("Enter the username to search: ")
    device_names = []
    devices = get_unique_devices()
    for device in devices["data"]:
        if device["username"] == username:
            device_names.append(device["device_name"])
    if not device_names:
        print(f"No devices found for user {username}")
    else:
        for device in device_names:
            print(f"Adding {device} to quarantine")
            add_device_to_quarantine(device)
