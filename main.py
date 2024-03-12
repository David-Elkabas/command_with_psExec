import subprocess
from pypsexec.client import Client
import csv
from datetime import datetime

executable = "whoami.exe"  # where the exe that need to be run on the client is locate
csv_file = "ip_addresses.csv"

class IpAddress:
    def __init__(self, ip, username, password, executable, arguments="", working_dir="C:\Windows\System32"):
        self.ip = ip
        self.username = username
        self.password = password
        self.executable = executable
        self.arguments = arguments
        self.working_dir = working_dir
        self.status = ""
        self.time_of_check = ""

    def __str__(self):
        return f"MyClass: ip={self.ip}, username={self.username}, password={self.password}, status={self.status}, time_of_check={self.time_of_check} "

def read_from_csv(csv_file):
    data = []
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ip = row['ip']
            username = row['username']
            password = row['password']
            machine = IpAddress(ip, username, password, executable)
            result = ps_exec_script(machine)
            print(result)
            machine.status = 'good' if result else 'bad'
            machine.time_of_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data.append(machine)
    return data


def write_to_csv(csv_file, array_of_updated_machines_to_save):
    fieldnames = ['IP', 'username', 'password', 'status', 'time_of_check']
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for machine in array_of_updated_machines_to_save:
            writer.writerow({
                'IP': machine.ip,
                'username': machine.username,
                'password': machine.password,
                'status': machine.status,
                'time_of_check': machine.time_of_check
            })


def ps_exec_script(machine):
    c = Client(machine.ip, username=machine.username, password=machine.password,
               encrypt=True)
    try:  # try to connect to the ip
        c.connect()
        try:
            c.create_service()
            result = c.run_executable(machine.executable, arguments=machine.arguments)
        finally:
            c.remove_service()
            # c.cleanup() #In the case of a fatal failure, this project may leave behind some the PAExec payload in C:\Windows or the service still installed. so this line clean it
            c.disconnect()
    except:  # didnt succeed to connect to the ip
        result = ""
        print("Failed to connect to:" + machine.ip)
        return result

    # print("STDOUT:\n%s" % result[0].decode('utf-8') if result[0] else "")
    # print("STDERR:\n%s" % result[1].decode('utf-8') if result[1] else "")
    # print("RC: %d" % result[2])
    # return result
    return  result[0].decode('utf-8')


if __name__ == '__main__':

    all_data = read_from_csv(csv_file)
    for data in all_data:
        print(data)

    write_to_csv(csv_file, all_data)

