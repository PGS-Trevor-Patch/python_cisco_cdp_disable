#######################
### REQUIREMENTS ###
#######################
# pip install -r requirements.txt

import requests
import json
import csv
import os.path
import re
import netmiko
import getpass
from netmiko import ConnectHandler

def ACI_CDP_DISABLE(user,pwd):
    with open('inventory.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            NAME = row['DEVICE_NAME']
            IP = row['DEVICE_IP']
            VENDOR = row['DEVICE_VENDOR']
            FAMILY = row['DEVICE_FAMILY']
            
            
            if VENDOR == "cisco" and FAMILY == "aci":
                #LOGIN
                AUTH_URL = 'https://' + IP + '/api/aaaLogin.json'
                AUTH_PAYLOAD = {"aaaUser":{"attributes":{"name":user,"pwd":pwd}}}
                AUTH_CALL = requests.post(url=AUTH_URL, json=AUTH_PAYLOAD, verify=False )
                if AUTH_CALL.status_code == 200:
                    JSON_DATA = AUTH_CALL.json()
                    ACI_API_TOKEN = JSON_DATA["imdata"][0]["aaaLogin"]["attributes"]["token"]
                    HEADERS = {"Cookie" : "APIC-Cookie=" + ACI_API_TOKEN + "",}
                    return HEADERS
                else:
                    print("The APIC, " + NAME + ", responded with the status code of " + str(AUTH_CALL.status_code) + ".")
                #LEAF ACCESS POLICIES
                GET_URL = 'https://' + IP + '/api/node/mo/uni/infra/funcprof.json?query-target=subtree&target-subtree-class=infraAccPortGrp'
                GET_CALL = requests.get(url=GET_URL, headers=HEADERS, verify=False)
                if GET_CALL.status_code == 200:
                    JSON_DATA = GET_CALL.json()
                    OBJECT_LIST = JSON_DATA["imdata"]
                    OBJECT_COUNT = 0
                    for OBJECT in OBJECT_LIST:
                        INFRA_ACC_PORT_GRP = JSON_DATA["imdata"][OBJECT_COUNT]["infraAccPortGrp"]["attributes"]["name"]
                        POST_URL = 'https://' + IP + '/api/node/mo/uni/infra/funcprof/accportgrp-' + INFRA_ACC_PORT_GRP + '/rscdpIfPol.json'
                        POST_PAYLOAD = {"infraRsCdpIfPol":{"attributes":{"tnCdpIfPolName":"CDP_DISABLE"},"children":[]}}
                        POST_CALL = requests.post(url=POST_URL,json=POST_PAYLOAD,headers=HEADERS,verify=False)
                        print("The APIC, " + NAME + ", responded to the POST with the status code of " + str(POST_CALL.status_code) + ".")
                        OBJECT_COUNT += 1
                else:
                    print("The APIC, " + NAME + ", responded to the GET with the status code of " + str(GET_CALL.status_code) + ".")
                #PC/VPC POLICIES
                GET_URL = 'https://' + IP + '/api/node/mo/uni/infra/funcprof.json?query-target=subtree&target-subtree-class=infraAccBndlGrp'
                GET_CALL = requests.get(url=GET_URL, headers=HEADERS, verify=False)
                if GET_CALL.status_code == 200:
                    JSON_DATA = GET_CALL.json()
                    OBJECT_LIST = JSON_DATA["imdata"]
                    OBJECT_COUNT = 0
                    for OBJECT in OBJECT_LIST:
                        INFRA_ACC_BNDL_GRP = JSON_DATA["imdata"][OBJECT_COUNT]["infraAccBndlGrp"]["attributes"]["name"]
                        POST_URL = 'https://' + IP + '/api/node/mo/uni/infra/funcprof/accbundle-' + INFRA_ACC_BNDL_GRP + '/rscdpIfPol.json'
                        POST_PAYLOAD = {"infraRsCdpIfPol":{"attributes":{"tnCdpIfPolName":"CDP_DISABLE"},"children":[]}}
                        POST_CALL = requests.post(url=POST_URL,json=POST_PAYLOAD,headers=HEADERS,verify=False)
                        print("The APIC, " + NAME + ", responded to the POST with the status code of " + str(POST_CALL.status_code) + ".")
                        OBJECT_COUNT += 1
                else:
                    print("The APIC, " + NAME + ", responded to the GET with the status code of " + str(GET_CALL.status_code) + ".")
            
def NXOS_CDP_DISABLE(user,pwd): 
    with open('inventory.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            NAME = row['DEVICE_NAME']
            IP = row['DEVICE_IP']
            VENDOR = row['DEVICE_VENDOR']
            FAMILY = row['DEVICE_FAMILY']
            
            if VENDOR == "cisco" and FAMILY == "nxos":  
                net_connect = ConnectHandler(
                    device_type="cisco_nxos",
                    host=IP,
                    username=user,
                    password=pwd,
                )
                commands_list = [
                    "configure terminal",
                    "no cdp enable"
                    ]
                cli_output = net_connect.send_config_set(commands_list)
                print(cli_output)
                net_connect.save_config()
                
def IOS_CDP_DISABLE(user,pwd): 
    with open('inventory.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            NAME = row['DEVICE_NAME']
            IP = row['DEVICE_IP']
            VENDOR = row['DEVICE_VENDOR']
            FAMILY = row['DEVICE_FAMILY']
            
            if VENDOR == "cisco" and FAMILY == "ios":  
                net_connect = ConnectHandler(
                    device_type="cisco_ios",
                    host=IP,
                    username=user,
                    password=pwd,
                )
                commands_list = [
                    "configure terminal",
                    "no cdp enable"
                    ]
                cli_output = net_connect.send_config_set(commands_list)
                print(cli_output)
                net_connect.save_config()            

while True:
    print('Author: Trevor Patch')
    print('Release Date: 09/22/2022')
    print('Script Version: 1')
    print('Description: ')    
    print(' This script was developed to enable customers to rapidly disable CDP across Cisco Systems Infrastructure') 
    print('\n')
    print('--------------------------------')
    print('\n')
    user = input('Enter the username: ')
    pwd = getpass.getpass(prompt = 'Enter the password: ')
    print('\n')
    print('--------------------------------')
    print('\n')
    print('Menu: ')
    print('0. Quit')
    print('1. ACI')
    print('2. NXOS')
    print('3. IOS')
    MENU_SELECTION = input("PLEASE SELECT A MENU NUMBER: ")    
    if MENU_SELECTION == 0:
        break
    elif MENU_SELECTION == 1: 
        ACI_CDP_DISABLE(user,pwd)
    elif MENU_SELECTION == 2: 
        NXOS_CDP_DISABLE(user,pwd)
    elif MENU_SELECTION == 3: 
        IOS_CDP_DISABLE(user,pwd)
    else:
        print('Invalid Menu Selection. Please input the menu number only.')            
