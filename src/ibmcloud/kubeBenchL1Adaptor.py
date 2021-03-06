import time
import json
import sys
import requests
import logging
import argparse
import datetime
import string
import random
import os

logger = logging.getLogger("iam")

vulnerablity_notes_defenition = {
    "notes": [
        {
            "kind": "FINDING",
            "short_description": "Kube bench ibmcloud warnings",
            "long_description": "Kube bench ibmcloud warnings",
            "provider_id": "kubeBenchIBMCloudWarnings",
            "id": "kubebenchibmcloud-warning",
            "reported_by": {
                "id": "kubebenchibmcloud-warning",
                "title": "Kubebench ibmcloud control"
            },
            "finding": {
                "severity": "LOW",
                "next_steps": [{
                    "title": "KUBE BENCH IBMCLOUD WARNINGS"
                }]
            }
        },
        {
            "kind": "FINDING",
            "short_description": "Kube bench ibmcloud failures",
            "long_description": "Kube Bench IBMCloud failures",
            "provider_id": "kubeBenchIBMCloudFailures",
            "id": "kubebenchibmcloud-failure",
            "reported_by": {
                "id": "kubebenchibmcloud-failure",
                "title": "Kubebench ibmcloud control"
            },
            "finding": {
                "severity": "HIGH",
                "next_steps": [{
                    "title": "KUBE BENCH IBMCLOUD FAILURE "
                }]
            }
        },

        {
            "kind": "CARD",
            "provider_id": "kubeBenchIBMCloud",
            "id": "kubebenchibmcloud-card",
            "short_description": "Kubebench ibmcloud vulnerabilities",
            "long_description": "kubebench ibmcloud reported vulnerabilities",
            "reported_by": {
                "id": "kubebenchibmcloud-card",
                "title": "kubebench ibmcloud vulnerabilities"
            },
            "card": {
                "section": "Container Config Benchmark",
                "title": "Kube-Bench",
                "subtitle": "IBM Cloud",
                "context" : {},
                "finding_note_names": [
                    "providers/kubeBenchIBMCloudWarnings/notes/kubebenchibmcloud-warning",
                    "providers/kubeBenchIBMCloudFailures/notes/kubebenchibmcloud-failure"
                ],
                "elements": [{
                    "kind": "NUMERIC",
                    "text": "Warnings",
                    "default_time_range": "4d",
                    "value_type": {
                        "kind": "FINDING_COUNT",
                        "finding_note_names": [
                            "providers/kubeBenchIBMCloudWarnings/notes/kubebenchibmcloud-warning"
                        ]
                    }
                },
                    {
                        "kind": "NUMERIC",
                        "text": "Failiures",
                        "default_time_range": "4d",
                        "value_type": {
                            "kind": "FINDING_COUNT",
                            "finding_note_names": [
                                "providers/kubeBenchIBMCloudFailures/notes/kubebenchibmcloud-failure"
                            ]
                        }
                    }
                ]
            }
        }
    ]
}


def obtain_iam_token(api_key):
    if not api_key:
        raise Exception("obtain_uaa_token: missing api key")

    token_url = os.environ['TOKEN_URL']
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    }

    body = 'grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey=' + api_key + '&response_type=cloud_iam'

    try:
        response = requests.post(token_url, data=body, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.exception("An unexpected error was encountered while obtaining IAM token" + str(err))
        return None
    if response.status_code == 200 and response.json()['access_token']:
        return response.json()['access_token']


def create_note(account_id, token, endpoint):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    for note in vulnerablity_notes_defenition["notes"]:
        if note['kind'] == "CARD":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloud/notes"
        elif note['provider_id'] == "kubeBenchIBMCloudWarnings":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudWarnings/notes"
        elif note['provider_id'] == "kubeBenchIBMCloudFailures":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudFailures/notes"

        try:
            response = requests.post(url, data=json.dumps(note), headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.exception("An unexpected error was encountered while creating note" + str(err))
        if response.status_code == 200:
            logger.info("Note created : %s" % note['id'])


def get_all_kubebenchnotes(account_id, token, endpoint):
    notes = []
    url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloud/notes"
    notes.extend(get_notes(account_id, token, endpoint, url))
    url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudWarnings/notes"
    notes.extend(get_notes(account_id, token, endpoint, url))
    url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudFailures/notes"
    notes.extend(get_notes(account_id, token, endpoint, url))
    return notes


def get_notes(account_id, token, endpoint, url):
    occurrences = []
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.exception("An unexpected error was encountered while getting the note" + str(err))
        return False
    if response.status_code == 200:
        body = response.json()
        for note in body['notes']:
            occurrences.append(note['id'])
        return note
    else:
        return []


def delete_notes(account_id, token, endpoint, notes):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    for note in notes:
        if note['kind'] == "CARD":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloud/notes"
        elif note['provider_id'] == "kubeBenchIBMCloudWarnings":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudWarnings/notes"
        elif note['provider_id'] == "kubeBenchIBMCloudFailures":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudFailures/notes"
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
        except:
            logger.exception("An unexpected error was encountered while deleting the note" + str(err))
        time.sleep(1)


def get_all_kubebenchoccurrences(account_id, token, endpoint):
    occurrences = []
    url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloud/occurrences"
    occurrences.extend(get_occurrences(account_id, token, endpoint, url))
    url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudWarnings/occurrences"
    occurrences.extend(get_occurrences(account_id, token, endpoint, url))
    url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudFailures/occurrences"
    occurrences.extend(get_occurrences(account_id, token, endpoint, url))
    return occurrences


def get_occurrences(account_id, token, endpoint, url):
    occurrences = []
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.exception("An unexpected error was encountered while getting the occurrences" + str(err))
        return False
    if response.status_code == 200:
        body = response.json()
        for occurrence in body['occurrences']:
            occurrences.append(occurrence)
        return occurrences


def delete_occurrences(account_id, token, endpoint, occurrences):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    for occurrence in occurrences:
        if occurrence['provider_id'] == "kubeBenchIBMCloudWarnings":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudWarnings/occurrences/" + occurrence['id']
        elif occurrence['provider_id'] == "kubeBenchIBMCloudFailures":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudFailures/occurrences/" + occurrence['id']

        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.exception("An unexpected error was encountered while deleting the occurrence" + str(err))
        time.sleep(1)


def id_generator(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for x in range(size))


# This method needs to be defined for any partner application that needs to adapt
def createOccurences(account_id, token, endpoint, occurrencesJson):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    for occurrence in occurrencesJson:
        if occurrence['provider_id'] == "kubeBenchIBMCloudWarnings":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudWarnings/occurrences"
        elif occurrence['provider_id'] == "kubeBenchIBMCloudFailures":
            url = endpoint + "/" + account_id + "/providers/kubeBenchIBMCloudFailures/occurrences"
        try:
            response = requests.post(url, data=json.dumps(occurrence), headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.exception("An unexpected error was encountered while creating occurrence" + str(err))
        if response.status_code == 200:
            logging.info("Created occurrence")
		    

def executePointInTimeVulnerabilityOccurenceAdapter(apikey, account_id, endpoint, vulnerabilitiesReportedByPartner):
    token = obtain_iam_token(apikey)
    try:
        create_note(account_id, token, endpoint)
    except:
        print("ignoring metadata duplicateerrors")
    try:
        vulnerabilityOccurrences = get_all_kubebenchoccurrences(account_id, token, endpoint)
        delete_occurrences(account_id, token, endpoint, vulnerabilityOccurrences)
    except:
        print("ignoring metadata duplicateerrors")

    createOccurences(account_id, token, endpoint, vulnerabilitiesReportedByPartner["insights"])
    occurrences = get_all_kubebenchoccurrences(account_id, token, endpoint)
    return occurrences


def postToSA(args):
    logging.info("Patch Management Monitoring started")
    apikey = args["apikey"]
    account_id = args["account"]
    endpoint = args["endpoint"]
    vulnerabilityOccurrences = executePointInTimeVulnerabilityOccurenceAdapter(apikey, account_id, endpoint,
                                                                               args["vulnerabilityInsights"])
    logging.info("Patch Management Monitoring completed")
    return {'insights': vulnerabilityOccurrences}
