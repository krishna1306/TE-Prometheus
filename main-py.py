import datetime

import requests
import os
import json
import pickle
import prometheus_client as prom
import logging

# Set Logging Standards - DEBUG and above (DEBUG, INFO, WARNING, ERROR and CRITICAL)
logging.basicConfig(filename='main-py.log', level=logging.INFO)

# TE Credentials
TE_USER = "user@gmail.com"
TE_SECRET = "rest_api_code"

# Headers for making API Calls
headers = {"Content-Type": "application/json",
           "Accept": "application/json"}

# Base URL for TE API
base_url = "https://api.thousandeyes.com/v6"

# We watch the below metrics. Each metric is formatted as ('value1a','value1b')
# 'value1a' --> easy to read metric name
# 'value1b' --> metric name as per TE API response
Watched_Metrics = [('latency', 'avgLatency'), ('jitter', 'jitter'), ('loss', 'loss'), ('srcAgentId', 'agentId'),
                   ('dstIp', 'serverIp'), ('srcCountry', 'countryId')]


def get_session():
    """
    Get the session object for Thousand Eyes API Server
    :return: Returns the session Object
    """
    session = requests.Session()
    return session


def get_response_data(session, url):
    """
    Get the response data for any API Call
    :param session: Establish a session to TE API server first. And pass the session object
    :param url: API URL
    :return: Returns python dictionary data in the response
    """
    response = session.get(url, auth=(TE_USER, TE_SECRET), headers=headers)
    data = json.loads(response.text)

    return data


def get_enabled_gis_tests(session):
    url = base_url + "/tests.json"
    data = get_response_data(session, url)

    enabled_gis_tests = []

    for test in data["test"]:
        if test['enabled'] != 0 and test['testName'][0:3] == "GIS":
            enabled_gis_tests.append(test)

    return enabled_gis_tests


def get_test_data(session, testId):
    # Construct the metrics_URL
    metrics_url = "https://api.thousandeyes.com/v6/net/metrics/" + str(testId)

    # Get the response from TE using the metrics_URL supplied
    data = get_response_data(session, metrics_url)

    # Initiate an empty list to store all the dictionaries for this Test Agent
    result = []

    for metrics in data['net']['metrics']:
        # An empty dictionary to hold the values, before adding it to result[]
        dic = {}

        for name, metric_name in Watched_Metrics:
            try:
                dic[name] = metrics[metric_name]
            except:
                dic[name] = -1

        dic['testId'] = testId
        result.append(dic)

    return result


def get_enterprise_agents_dict(session):
    endpoint = f"{base_url}/agents.json"
    response = session.get(endpoint, auth=(TE_USER, TE_SECRET), headers=headers)

    data = json.loads(response.text)

    agents_dict = {}

    for agents in data['agents']:
        if "Enterprise" in agents['agentType']:
            countryID = agents['countryId']
            try:
                agents_dict[agents['clusterMembers'][0]['targetForTests']] = [agents['agentId'], countryID]
            except:
                agents_dict[agents['targetForTests']] = [agents['agentId'], countryID]

    return agents_dict


if __name__ == "__main__":
    session = get_session()

    enabled_gis_tests = get_enabled_gis_tests(session)

    # GIS ENABLED TESTS PRINT - FOR DEBUG ONLY
    # for test in enabled_gis_tests:
    #     print(f"\nTest ID is : {test['testId']}")
    #     print(f"Test Name is : {test['testName']}")
    #     print(f"Destination IP is : {test['server']}")
    #     print(f"Test URL is : {test['apiLinks'][1]['href']}")

    enabled_gis_tests_dic = {}

    for test in enabled_gis_tests:
        enabled_gis_tests_dic[test['testId']] = test['testName']

    per_session_data = {}

    for test_id, test_name in enabled_gis_tests_dic.items():
        per_session_data[test_id] = get_test_data(session, test_id)

    # Metrics
    metrics_list = ["latency", "jitter", "loss"]

    # Set Guage Label Format for Prometheus Export

    guages = {}

    for item in metrics_list:
        guages[item] = prom.Gauge(f"{item}_total", f"Gauge {item} figure", [
            "srcAgentId", "dstAgentIp", "dstAgentId", "srcAgentLocation", "dstAgentLocation", "version", "domain", "testId"])

    enterprise_agents_dict = get_enterprise_agents_dict(session)

    with open('metrics', 'w') as metrics_file:

        for items in per_session_data:
            for each_test in per_session_data[items]:
                for metric in metrics_list:
                    try:
                        dstAgentId = enterprise_agents_dict[each_test['dstIp']][0]
                        dstAgentLocation = enterprise_agents_dict[each_test['dstIp']][1]
                    except:
                        dstAgentId = 'Unknown'
                        dstAgentLocation = "Unknown"
                    guages[metric].labels(srcAgentId=each_test['srcAgentId'],
                                          dstAgentIp=each_test['dstIp'],
                                          dstAgentId=dstAgentId,
                                          srcAgentLocation=each_test['srcCountry'],
                                          dstAgentLocation=dstAgentLocation,
                                          version="1.0",
                                          testId=items,
                                          domain="GIS").set(each_test[metric])
                    output = prom.exposition.generate_latest().decode("utf-8")
                    content_type = prom.exposition.CONTENT_TYPE_LATEST

        metrics_file.write(output)

    date_time = datetime.datetime.now()

    logging.info(f"Metrics Exported at {date_time}")
