# Zabbix import hosts


[![](https://img.shields.io/badge/View-My_Profile-green?logo=GitHub)](https://github.com/Udeus)
[![](https://img.shields.io/badge/View-My_Repositories-blue?logo=GitHub)](https://github.com/Udeus?tab=repositories)
![](https://img.shields.io/github/license/udeus/zabbix-import-hosts)

Easy import hosts from Excel file to Zabbix server.

## Requirments
- Python 3.x + pip
- Zabbix server


## Install
`
pip install -r requirements.txt
`


## Usage
Run script:
`
python main.py --url <zabbix_address_url> --token <zabbix_api_token>
`

Example:
`
python main.py --url http://192.168.1.105 --token d36cab4cb00097b11bb97739828aed93ec521858de3e007a2d91a2047ff5a72d
`


## Commands

| Command       | Description                            |
|---------------|----------------------------------------|
| help          | Show all commands                      |
| groups        | Show all groups and ID                 |
| hosts         | Show all hosts and ID                  |
| templates     | Show all templates and ID              |
| template      | Show ID one template                   |
| proxy groups  |Show all proxy groups                   |
| proxies       | Show all proxies                       |
| import hosts  | Import hosts from file to Zabbix server |
| exit          | Close script                           |

### License

License: https://github.com/Udeus/zabbix-import-hosts?tab=GPL-3.0-1-ov-file