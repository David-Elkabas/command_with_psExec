import subprocess
from pypsexec.client import Client


class IpAddress:
    def __init__(self, ip, username, password, executable, arguments="", working_dir="C:\Windows\System32"):
        self.ip = ip
        self.username = username
        self.password = password
        self.executable = executable
        self.arguments = arguments
        self.working_dir = working_dir
        self.results = ""


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
        # print("Failed to connect to:" + machine.ip)
        return result

    # print("STDOUT:\n%s" % result[0].decode('utf-8') if result[0] else "")
    # print("STDERR:\n%s" % result[1].decode('utf-8') if result[1] else "")
    # print("RC: %d" % result[2])
    return result


if __name__ == '__main__':
    ip = "your_ip_address"
    username = "username"
    password = "password"
    executable = "whoami.exe"  # where the exe that need to be run on the client is locate
    # arguments = ""  # arg for the executable
    # working_dir = "C:\Windows\System32"

    machine = IpAddress(ip, username, password, executable)
    output = ps_exec_script(machine)

    print(output)
    # c = Client(server, username=username, password=password,
    #            encrypt=True)
    # try:  # try to connect to the ip
    #     c.connect()
    #     try:
    #         c.create_service()
    #         result = c.run_executable(executable, arguments=arguments)
    #     finally:
    #         c.remove_service()
    #         #c.cleanup() #In the case of a fatal failure, this project may leave behind some the PAExec payload in C:\Windows or the service still installed. so this line clean it
    #         c.disconnect()
    # except:  # didnt succeed to connect to the ip
    #     result = ""
    #     print("Failed to connect to:" + server)
    #
    #     print("STDOUT:\n%s" % result[0].decode('utf-8') if result[0] else "")
    #     print("STDERR:\n%s" % result[1].decode('utf-8') if result[1] else "")
    #     print("RC: %d" % result[2])

