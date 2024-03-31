import subprocess
from pypsexec.client import Client
import csv
from datetime import datetime
import re


executable = "whoami.exe"  # where the exe that need to be run on the client is locate
csv_file = "ip_addresses.csv"
csv_output = "output.csv"

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
        self.cpu = ""
        self.storage_by_percent = ""
        self.storage_by_value = ""


    def __str__(self):
        return f"MyClass: arguments={self.arguments}, ip={self.ip}, username={self.username}, password={self.password}, status={self.status}, time_of_check={self.time_of_check} "

def read_from_csv(csv_file):
    data = []
    with open(csv_file, 'r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            ip = row['ip']
            username = row['username']
            password = row['password']
            executable = "wmic"  # where the exe that need to be run on the client is locate
            arguments = "cpu get loadpercentage"

            machine = IpAddress(ip, username, password, executable, arguments)

            temp_cpu_array = []
            x = 0
            # get three samples of the cpu score and them get the average of them
            while x < 3:
                result = ps_exec_script(machine)
                if result:
                    array_of_cpu_percentage = get_numbers_from_string(result[0])
                    x = x + 1
                # there may be more than one core and therefore we need to calculate the average of them.
                    temp_cpu_array.append(given_array_calc_average(array_of_cpu_percentage))
                else:
                    x = 3

            print(f"the three cpu percentage calculated are: {temp_cpu_array}")
            if temp_cpu_array:
                machine.cpu = given_array_calc_average(temp_cpu_array)
                # machine.storage_by_percent = machine_info.storage_by_percent
                # machine.storage_by_value = machine_info.storage_by_value
                print(f"the cpu of {machine.ip} is {machine.cpu}%")
                if machine.cpu < 80:  # need to add also the storage data for this section!
                    machine.executable = "whoami.exe"
                    machine.arguments =""
                    result = ps_exec_script(machine)
                    print(f"psExec succeed at {machine.ip} and the results are {result} \n")

                    machine.status = 'all good' if result else 'psExec problem'
                else:  # the cpu is too high - > dont execute the program
                    machine.status = f"cpu too full at {machine.cpu}% \n"
            else:
                machine.status = 'machine not found'
            machine.time_of_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data.append(machine)
    return data


def write_to_csv(csv_file, array_of_updated_machines_to_save):
    fieldnames = ['ip', 'username', 'password', 'status', 'time_of_check', 'cpu']
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for machine in array_of_updated_machines_to_save:
            writer.writerow({
                'ip': machine.ip,
                'username': machine.username,
                'password': machine.password,
                'status': machine.status,
                'time_of_check': machine.time_of_check,
                'cpu': machine.cpu

            })
        print("finish saving all the DATA")


def get_numbers_from_string(input_string):

    # Regular expression pattern to match numbers
    pattern = r'\d+'
    # Find all numbers in the string using regex
    numbers = re.findall(pattern, input_string)
    # Convert the numbers from string to integers
    numbers = [int(num) for num in numbers]
    return numbers


def given_array_calc_average(array_of_numbers):

    counter = 0
    sum = 0
    for number in array_of_numbers:
        counter = counter + 1
        sum = sum + number

    return sum/counter


def ps_exec_script(machine):
    # print(f"starting to connect to {machine.ip} with the command {machine.executable}")
    c = Client(machine.ip, username=machine.username, password=machine.password,
               encrypt=True)
    try:  # try to connect to the ip
        c.connect()
        try:
            c.create_service()
            result = c.run_executable(machine.executable, arguments=machine.arguments)
        finally:
            c.remove_service()
            # c.cleanup()  #In the case of a fatal failure, this project may leave behind some the PAExec payload in
            # C:\Windows or the service still installed. so this line clean it
            c.disconnect()
    except:  # didnt succeed to connect to the ip
        result = ""
        print("Failed to connect to:" + machine.ip + "\n")
        return result

    # print("STDOUT:\n%s" % result[0].decode('utf-8') if result[0] else "")
    # print("STDERR:\n%s" % result[1].decode('utf-8') if result[1] else "")
    # print("RC: %d" % result[2])
    # return result
    # print(result)
    return [result[0].decode('utf-8'), result[1].decode('utf-8'), result[2]]


if __name__ == '__main__':

    # - - - - - - - for debugging the cpu only - - - - - - - - - - - - - - -
    # machine = IpAddress("172.20.10.9", "david", "", "wmic", "cpu get loadpercentage")
    # result = ps_exec_script(machine)
    #
    # array_of_cpu_percentage = get_numbers_from_string(result[0])
    # # there may be more than one core and therefore we need to calculate the average of them.
    # cpu_percentage = given_array_calc_average(array_of_cpu_percentage)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    all_machines_new_data = read_from_csv(csv_file)
    for data in all_machines_new_data:
        print(data)

    write_to_csv(csv_output, all_machines_new_data)

