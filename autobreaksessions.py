import re, platform, sys, os, logging, datetime
from urllib.request import urlopen as url
from time import sleep
try:
    from netmiko import ConnectHandler
except ModuleNotFoundError:  # Netmiko not installed by default
    print("INSTALL MISSING MODULE")
    try:
        url("https://pypi.org/")
    except:
        print("The Internet is required to install missing module")
        sys.exit(0)
    from pip._internal import main as pip
    pip(['install', 'netmiko'])
    from netmiko import ConnectHandler
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def choice(msg:str, default:bool=True):
    if default:
        param = input(msg + ' [Y/n] ')
    else:
        param = input(msg + ' [y/N] ')
    while True:
        if not param:
            return default
        elif param.lower() == 'y':
            return True
        elif param.lower() == 'n':
            return False
        else:
            print('\nNot correct answer')
            if default:
                param = input(msg + ' [Y/n] ')
            else:
                param = input(msg + ' [y/N] ')

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'auto':
            auto = True
        elif sys.argv[1] == 'manual':
            auto = False
        else:
            auto = choice("AUTO MODE")
    else:
        auto = choice("AUTO MODE")

    asa = {
        'host': '',  # Cisco ASA settings
        'username': '',
        'password': '',
        'secret': '',
        'device_type': 'cisco_asa',
        'fast_cli': False }
    timeout = 300  # seconds. No traffic timeout
    connection = ConnectHandler(**asa)
    connection.enable()
    connection.send_command('terminal length 0')
    print('CONNECTED')

    previousTx = {}
    previousRx = {}
    while True:
        sessions = connection.send_command("show vpn-sessiondb anyconnect")  # Get all sessions...
        users = re.findall(r"Username     : \S+", sessions)
        users = list(map(lambda x : x.replace("Username     : ", ""), users))
        ips = re.findall(r"192.168.205.\d{0,3}", sessions)
        bytesTx = re.findall(r"Bytes Tx     : \d+", sessions)
        bytesTx = list(map(lambda x : int(x.replace("Bytes Tx     : ", "")), bytesTx))
        bytesRx = re.findall(r"Bytes Rx     : \d+", sessions)
        bytesRx = list(map(lambda x : int(x.replace("Bytes Rx     : ", "")), bytesRx))
        if len(users) == len(ips) == len(bytesTx) == len(bytesRx):  # If lists are correct
            for i in range(len(ips)):
                try:
                    if previousTx[ips[i]] == bytesTx[i] and previousRx[ips[i]] == bytesRx[i]:  # If the traffic has not changed
                        ping = connection.send_command("ping " + ips[i], read_timeout=20)  # Check ping. If the host does not ping
                        if '!' not in ping:  
                            if auto:
                                connection.send_command("vpn-sessiondb logoff name " + users[i] + " noconfirm")  # Session logoff
                                print(users[i], 'LOGOFF\n', ips[i], bytesTx[i], bytesRx[i], previousTx[ips[i]], previousRx[ips[i]])
                            else:
                                if choice(users[i] + 'LOGOFF'):  # If auto mode is enabled - ask user
                                    connection.send_command("vpn-sessiondb logoff name " + users[i] + " noconfirm")
                                    print(users[i], 'LOGOFF\n', ips[i], bytesTx[i], bytesRx[i], previousTx[ips[i]], previousRx[ips[i]])
                    previousTx[ips[i]] = bytesTx[i]  # Safe traffic info for next cycle
                    previousRx[ips[i]] = bytesRx[i]
                except KeyError:
                    previousTx[ips[i]] = bytesTx[i]  # If it's first launch - write current numbers to previous
                    previousRx[ips[i]] = bytesRx[i]
            sleep(timeout)  # Wait for next check
        else:
            print("PARSING ERROR\n\n", ips, users, bytesTx, bytesRx)
            sys.exit(0)  
logging.basicConfig(level=logging.ERROR,
                    filename=os.getcwd() + '\\abs-' + datetime.datetime.strftime(datetime.datetime.today(), '%d%m%Y%H%M%S') + '.log')
try:
    main()
except Exception as e:
    logging.error(e)