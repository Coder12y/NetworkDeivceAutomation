import paramiko
import getpass
import textfsm
import re
import os
import time
import xlwings as sw

def extract_data(command_output, template):
    '''Extracts data from command output based on FSM template file'''
    fsm = textfsm.TextFSM(template)
    return fsm.ParseText(command_output)

def _analysis_device_data(device_data, template_file):
    key_list = []
    value_list = []
    device_data_list = []

    with open(template_file, "r") as extract_temp:
        value_list = extract_data(device_data, extract_temp)

    with open(template_file, "r") as file:
        contents = file.readlines()

        for line in contents:
            if "Value" in line:
                key_name = re.findall(r"Value\s+(\S+|\S+)? (\S+) \s+\(", line)[0][1]
                key_list.append(key_name)

        for each_value in value_list:
            each_data_obj = {}
            for index, each_key in enumerate(key_list):
                each_data_obj[each_key] = each_value[index]
            if each_data_obj:
                device_data_list.append(each_data_obj)

    return device_data_list

def get_output(device_session, command_prompt):
    line = output = ""

    if command_prompt == "login:":
        number_input = 0
        while command_prompt not in line.lower():
            char = device_session.recv(1)
            char = "".join(map(chr, char))
            line += char

        # Read until end of line character is read
        while command_prompt not in line.lower() and char != "\n":
            char = device_session.recv(1)
            char = "".join(map(chr, char))
            # Additional line will appear in Notepad++ if don't remove \r
            if char == "\r":
                continue
            line += char

        if "[inactive]" not in line and line[0].isnumeric():
            number_input = int(line[0])

        if "shell]?" in line:
            device_session.send("ssh {}\n".format(number_input))

        if "Management of this device has been disabled." in line:
            output = "Skip..."
            break

    else:
        while command_prompt not in line:
            char = line
            # Read until command prompt is found or end of line character is read
            while command_prompt not in line and char != '\n':
                char = device_session.recv(1)
                char = "".join(map(chr, char))
                # Additional line will appear in Notepad++ if don't remove \r
                if char == '\r':
                    continue
                line += char

            if command_prompt in line.lower():
                break

        elif "Are you sure you want to continue connecting (yes/no)?".lower() in line.lower():
            # Your code for handling the question
            pass

    return line, output
