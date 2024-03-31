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
        self.total_storage = 0
        self.free_storage = 0

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

            cpu_average = calc_cpu_average(machine)

            if cpu_average is None:
                machine.cpu = 0
                machine.status = 'machine not found'
            else:
                machine.cpu = cpu_average
                print(f"the cpu of {machine.ip} is {machine.cpu}%")

                if machine.cpu < 80:  # need to add also the storage data for this section!
                    machine.free_storage, machine.total_storage = calc_storage(machine)
                    print(f"in {machine.ip} there is {machine.free_storage}MB free storage and the whole storage is"
                          f" {machine.total_storage}MB")

                    if machine.free_storage > 1000:
                        machine.executable = "whoami.exe"
                        machine.arguments = ""
                        result = ps_exec_script(machine)
                        print(f"psExec succeed at {machine.ip} and the results are {result} \n")

                        machine.status = 'all good' if result else 'psExec problem'
                    else:
                        machine.status =  f"storage too low at {machine.free_storage}MB \n"
                else:  # the cpu is too high - > dont execute the program
                    machine.status = f"cpu too full at {machine.cpu}% \n"

            machine.time_of_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data.append(machine)
    return data


def write_to_csv(csv_file, array_of_updated_machines_to_save):
    fieldnames = ['ip', 'username', 'password', 'status', 'time_of_check', 'cpu', 'free_storage(MB)', 'total_storage(MB)']
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
                'cpu': machine.cpu,
                'free_storage(MB)': machine.free_storage,
                'total_storage(MB)': machine.total_storage

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

    return sum / counter


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


def calc_cpu_average(machine):
    temp_cpu_array = []
    # get three samples of the cpu score and them get the average of them
    for x in range(3):
        temp_result = ps_exec_script(machine)
        if temp_result:
            array_of_cpu_percentage = get_numbers_from_string(temp_result[0])
            # there may be more than one core and therefore we need to calculate the average of them.
            temp_cpu_array.append(given_array_calc_average(array_of_cpu_percentage))
        else:
            return None

    print(f"the three cpu percentage calculated are: {temp_cpu_array}")
    machine_cpu = given_array_calc_average(temp_cpu_array)
    return round(machine_cpu)


def calc_storage(machine):
    machine.arguments = "logicaldisk get size, freespace, caption"
    temp_result = ps_exec_script(machine)
    if temp_result:
        only_numbers = get_numbers_from_string(temp_result[0])

        free_storage = round(only_numbers[0] / 1000000)
        full_disk_storage = round(only_numbers[1] / 1000000)
        return free_storage, full_disk_storage
    else:
        return None, None


if __name__ == '__main__':

    # - - - - - - - for debugging the cpu only - - - - - - - - - - - - - - -
    # machine = IpAddress("172.20.10.9", "david", "", "wmic", "cpu get loadpercentage")
    # result = ps_exec_script(machine)
    #
    # array_of_cpu_percentage = get_numbers_from_string(result[0])
    # # there may be more than one core and therefore we need to calculate the average of them.
    # cpu_percentage = given_array_calc_average(array_of_cpu_percentage)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # - - - - - - - for debugging the storage only - - - - - - - - - - - - - - -
    # machine = IpAddress("172.20.10.9", "david", "", "wmic", "logicaldisk get size, freespace, caption")
    # result = ps_exec_script(machine)
    #
    # only_numbers = get_numbers_from_string(result[0])
    #
    # free_storage = round(only_numbers[0] / 1000000)
    # full_disk_storage = round(only_numbers[1] / 1000000)
    # print(f"there is {free_storage}MB free storage and the whole storage is {full_disk_storage}MB")

    # there may be more than one core and therefore we need to calculate the average of them.
    # cpu_percentage = given_array_calc_average(array_of_cpu_percentage)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    all_machines_new_data = read_from_csv(csv_file)
    for data in all_machines_new_data:
        print(data)

    write_to_csv(csv_output, all_machines_new_data)
