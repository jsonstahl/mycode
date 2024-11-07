#!/usr/bin/python3

import requests
import json


time_url = "http://date.jsontest.com"
ip_url = "http://ip.jsontest.com"
validate_url = "http://validate.jsontest.com/"

def main():

    time_response_call = requests.get(time_url)
    time_response_json = time_response_call.json()
    time = time_response_json['time']

    ip_call = requests.get(ip_url)
    ip_call_json = ip_call.json()
    ip = ip_call_json['ip']

    with open('./myservers.txt', 'r') as file:
        content = file.read()
        print(content)

    test_array = {}
    test_array["json"] = {}
    test_array["json"]["time"] = time
    test_array["json"]["ip"] = ip.replace(" ", "").replace(":", "-")
    test_array["json"]["servers"] = content.replace(" ", "").replace(":", "-")
    array = str(test_array)

    validate_response = requests.post(validate_url, data=array)

    validate_response_json = validate_response.json()

    print(validate_response_json)

if __name__ == "__main__":
    main()
