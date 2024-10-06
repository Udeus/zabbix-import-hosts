import os
import requests
import argparse
import pandas as pd
from tabulate import tabulate
terminal_width = os.get_terminal_size().columns
from utils import zabbix_url

help_command = [["help", "Show all commands"], ["groups", "Show all groups and ID"], ["hosts", "Show all hosts and ID"],
                ["templates", "Show all templates and ID"], ["template", "Show ID one template"],
                ["proxy groups", "Show all proxy groups"], ["proxies", "Show all proxies"],
                ["import hosts", "Import hosts from file to Zabbix server"], ["author", "About author"],
                ["exit", "Close script"]]

parser = argparse.ArgumentParser(description="Zabbix import host | More info: https://github.com/Udeus/zabbix-import-hosts/")
parser.add_argument("--url", type=str, help="Zabbix url address")
parser.add_argument("--token", type=str, help="API token")
args = parser.parse_args()


if args.url:
    api_url = zabbix_url(args.url)
else:
    api_url = zabbix_url(input("Zabbix url address: "))


if args.token:
    api_token = args.token
else:
    api_token = input("Zabbix API token: ")


print(tabulate(help_command, headers=["Command", "Description"], tablefmt="psql"))
print("How to use: https://github.com/Udeus/zabbix-import-hosts")


def connect_api(api_date):
    request_header = {'Authorization': 'Bearer ' + api_token, 'Content-Type': 'application/json-rpc'}
    response = requests.post(api_url, data=api_date, headers=request_header)
    response = response.json()["result"]

    return response


def get_groups():
    api_date = '{"jsonrpc": "2.0","method": "hostgroup.get","params": {"output": ["name", "groupid"]},"id": 1}'
    response = connect_api(api_date)
    print(tabulate(response, headers="keys", tablefmt="psql"))


def get_hosts_list():
    api_date = '{"jsonrpc": "2.0","method": "host.get","params": {"output": ["name", "groupid"]},"id": 1}'
    response = connect_api(api_date)
    print(tabulate(response, headers="keys", tablefmt="psql"))


def get_templates():
    api_date = '{"jsonrpc": "2.0","method": "template.get","params": {"output": ["name", "groupid"]},"id": 1}'
    response = connect_api(api_date)
    print(tabulate(response, headers="keys", tablefmt="psql"))


def get_template():
    template_name = input("Template name: ")
    api_date = f'{{"jsonrpc": "2.0","method": "template.get","params": {{"output": ["name", "groupid"],"filter": {{"host": ["{template_name}"]}}}},"id": 1}}'
    response = connect_api(api_date)
    if response:
        print(tabulate(response, headers="keys", tablefmt="psql"))
    else:
        print("Template not found")


def get_proxies_groups():
    api_date = '{"jsonrpc": "2.0","method": "proxygroup.get","params": {"output": ["name", "proxy_groupid"]},"id": 1}'
    response = connect_api(api_date)
    if response:
        print(tabulate(response, headers="keys", tablefmt="psql"))
    else:
        print("Proxy group not found")


def get_proxies():
    api_date = '{"jsonrpc": "2.0","method": "proxy.get","params": {"output": ["name", "proxyid", "address"]},"id": 1}'
    response = connect_api(api_date)
    if response:
        print(tabulate(response, headers="keys", tablefmt="psql"))
    else:
        print("Proxy not found")


def import_hosts():
    file_name = input("File to import: ")
    file = pd.read_excel(file_name)

    for index, row in file.iterrows():
        file_hostname = row["Hostname*"]
        file_address_ip = row["IP address"]
        file_dns = row["DNS"]
        file_interface = row["Interface"]
        file_port = row["Port"]
        file_group = row["Group ID*"]
        file_template_id = row["Template ID"]
        file_proxy_id = row["Proxy ID"]
        useip = 1
        interface_id = 1
        port = 10050
        interface_detals = ""

        # Required hostname and group
        if pd.isna(file_hostname) or pd.isna(file_group):
            break
        else:

            # Check adress ip/dns
            if pd.isna(file_address_ip):
                file_address_ip = ""
            if pd.isna(file_dns):
                file_dns = ""
            if file_dns and not file_address_ip:
                useip = 0

            if file_interface == "Agent" or pd.isna(file_interface):
                interface_id = "1"
                if pd.isna(file_port):
                    port = "10050"
                else:
                    port = round(file_port)
            elif file_interface == "SNMPv1" or file_interface == "SNMPv2" or file_interface == "SNMPv3":
                interface_id = "2"
                if file_interface == "SNMPv1":
                    interface_detals = ', "details": {"version": 1, "community": "{$SNMP_COMMUNITY}"}'
                elif file_interface == "SNMPv2":
                    interface_detals = ', "details": {"version": 2, "community": "{$SNMP_COMMUNITY}"}'
                elif file_interface == "SNMPv3":
                    interface_detals = ', "details": {"version": 3}'

                if pd.isna(file_port):
                    port = "161"
                else:
                    port = round(file_port)
            elif file_interface == "JMX":
                interface_id = "4"
                if pd.isna(file_port):
                    port = "12345"
                else:
                    port = round(file_port)
            elif file_interface == "IPMI":
                interface_id = "3"
                if pd.isna(file_port):
                    port = "623"
                else:
                    port = round(file_port)

            if file_address_ip == "" and file_dns == "":
                interface = ''
            else:
                interface = f',"interfaces": [{{"type": "{interface_id}","main": 1,"useip": "{useip}","ip": "{file_address_ip}","dns": "{file_dns}","port": "{port}" {interface_detals}}}]'

            if pd.isna(file_template_id):
                template = ""
            else:
                file_template_id = round(file_template_id)
                template = f',"templates": [{{"templateid": "{file_template_id}"}}]'

            if pd.isna(file_proxy_id):
                proxy_id = ""
            else:
                file_proxy_id = round(file_proxy_id)
                proxy_id = f', "proxyid": "{file_proxy_id}"'

            api_data = f'{{"jsonrpc": "2.0","method": "host.create","params": {{"host": "{file_hostname}"{proxy_id}{interface},"groups": [{{"groupid": "{round(file_group)}"}}]{template}}},"id": 1}}'
            request_header = {'Authorization': 'Bearer ' + api_token, 'Content-Type': 'application/json-rpc'}
            response = requests.post(api_url, data=api_data, headers=request_header)
            response = response.json()
            result = response.get("result", {}).get("hostids")
            error = response.get("error", {}).get("data")

            print('-' * terminal_width)
            print("Hostname:", file_hostname)

            if result is not None:
                print("New host ID:", result)
            elif error is not None:
                print("Error message:", error)
            else:
                print("Error")


if api_token and api_url:
    while True:

        # Check URL API
        try:
            data = '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'
            header = {'Content-Type': 'application/json-rpc'}

            response_api = requests.post(api_url, data=data, headers=header)
            response_api.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"Error API: {e}")
            break

        except Exception as e:
            print(f"Error: {e}")
            break

        # Check API Token
        try:
            data = '{"jsonrpc": "2.0","method": "token.get","params": {"output": "extend"},"id": 1}'
            header = {'Authorization': 'Bearer ' + api_token, 'Content-Type': 'application/json-rpc'}

            response_api = requests.post(api_url, data=data, headers=header)
            response_api = response_api.json()["result"]

            command = input("Command: ")

        except Exception:
            print("Error API: Correct your token")
            break

        # Commands
        if command == "help":
            print(tabulate(help_command, headers=["Command", "Description"], tablefmt="psql"))
            print("How to use: https://github.com/Udeus/zabbix-import-hosts")
        elif command == "groups":
            get_groups()
        elif command == "hosts":
            get_hosts_list()
        elif command == "templates":
            get_templates()
        elif command == "template":
            get_template()
        elif command == "proxy groups":
            get_proxies_groups()
        elif command == "proxies":
            get_proxies()
        elif command == "import hosts":
            import_hosts()
        elif command == "author":
            print("Created by Andrzej Pietryga")
            print("Github: https://github.com/Udeus/")
        elif command == "exit":
            print("Closing the script...")
            break
        else:
            print("Command not found")
