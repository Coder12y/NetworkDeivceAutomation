import xlwings as Xw
from sys import argv
import multiprocessing
import subprocess as sp
import time
from switch_ssh_cli import _open_session, _close_session
import textfsm
import re

def extract_data(command_output, template):
    '''Extracts data from command output based on FSM template file.'''
    fsm = textfsm.TextFSM(template)
    return fsm.ParseText(command_output.decode('ascii'))

def _ping_capture(devicesession, hostname, command):
    devicesession.send(command + "\n")
    terminal_screen = ""
    while hostname + "#" not in terminal_screen:
        output = devicesession.recv(1)
        output = "".join(map(chr, output))
        terminal_screen = terminal_screen + output
    # print(terminal_screen)
    return terminal_screen

def show_capture(devicesession, hostname, command):
    devicesession.send(command + "\n")
    terminal_screen = ""
    while hostname + "" not in terminal_screen:
        output = devicesession.recv(1)
        output = "".join(map(chr, output))
        terminal_screen = terminal_screen + output
    terminal_screen = terminal_screen.encode(encoding='utf8')
    # print(terminal_screen)
    return terminal_screen

def _special_issue_command(devicesession, command, action, hostname):
    # Issues IOS/NX-OS commands and returns response
    if action == 'ping':
        print("Issuing command '{0}'".format(command))
        if "I" in _ping_capture(devicesession, hostname, command):
            return "ok"
        else:
            # re-ping
            print("Ping time out, Re-Issuing command '{0}'".format(command))
            if "I" in _ping_capture(devicesession, hostname, command):
                return "ok"
            else:
                return "No response"
    elif action == "check_mac" or action == "cat6k_show_mac":
        print("Issuing command '{0}'".format(command))
        output = show_capture(devicesession, hostname, command)

def _cat6k_ping(sd_switch_hostname, ad_username, ad_password, ping_command, action, ping_row, NCM):
    ssh_session = _open_session(ad_username, ad_password, ad_username, ad_password, "off", NCM, sd_switch_hostname, "enable")
    session_output = _special_issue_command(ssh_session, ping_command, action, sd_switch_hostname)
    print("Ping Result: {0}".format(session_output))
    _close_session(ssh_session, "enable")
    return [session_output, ping_row]

def multiple_laptop_ping(ping_brief, ip, row_count):
    print(ping_brief + " " + time.ctime())
    status, result = sp.getstatusoutput("ping -w 1000 -n 1 {0}".format(ip))
    if status == 0:
        status = "ok"
    else:
        status = "No response"
    return [ip, status, row_count]

def _ping_session(ad_username, ad_password, sd_switch_hostname, action, sht, NCM):
    process_count = 0
    sht.range('A2').value = "Process -> {0}%".format(process_count)
    sht.range('A2').color = None
    end_row = sht.range('A3').end('down').row
    vlan_row_list = []
    for row_count in range(4, end_row + 1):
        vlan_row_list.append(row_count)
    first_row = vlan_row_list[0]
    last_row = vlan_row_list[-1]

    # reset M&N column
    sht.range('M1:M{0}'.format(last_row)).clear_contents()
    sht.range('M{0}:M{1}'.format(first_row, last_row)).color = None

    ip_list = sht.range('A4:A{0}'.format(last_row)).value

    # 90% assign to ping progress
    interval_list = []
    ip_len = len(ip_list)
    interval = int(ip_len / 90) + 1

    for each in range(1, ip_len):
        if each % interval == 0:
            interval_list.append(each)

    # ssh line vty # 60
    line_vty1 = 30
    pool = multiprocessing.Pool(processes=line_vty1)
    ping_result_list = []
    count = 0

    for ip in ip_list:
        count += 1
        ping_brief = "{0} Start to ping {1}".format(count, ip)
        ping_result_list.append(pool.apply_async(func=_multiple_laptop_ping, args=(ping_brief, ip, None)))
        if count in interval_list:
            process_count += 1

    pool.close()
    pool.join()
    print("Local laptop Ping done.")
    sht.range('A2').value = "Process -> {0}%".format(process_count)

    ping_status_list = []
    for ping_result_set in ping_result_list:
        ping_result = ping_result_set.get()
        ping_status = ping_result[1]
        ping_status_list.append([ping_status])

    sht.range('M{0}:M{1}'.format(first_row, last_row)).value = ping_status_list
    print("Laptop Ping result written into excel.")

    no_response_list = []
    for row_count in range(4, end_row + 1):
        excel_status_value = sht.range('M{0}'.format(row_count)).value
        excel_ip_value = sht.range('A{0}'.format(row_count)).value
        if excel_status_value == "No response":
            no_response_list.append([row_count, excel_ip_value])

    line_vty2 = 3
    pool = multiprocessing.Pool(processes=line_vty2)
    cat6k_ping_status_list = []

    for no_response_value in no_response_list:
        row_count = no_response_value[0]
        excel_ip_value = no_response_value[1]
        ping_command = "ping ip {0} repeat 1".format(excel_ip_value)
        cat6k_ping_status_list.append(pool.apply_async(func=_cat6k_ping, args=(sd_switch_hostname, ad_username, ad_password, ping_command, action,row_count,NCM)))

    pool.close()
    pool.join()
    print("Cat6K Ping done.")
    process_count = 95
    sht.range('A2').value = "Process -> {0}%".format(process_count)

    for ping_result_set in cat6k_ping_status_list:
        ping_result = ping_result_set.get()
        ping_status = ping_result[0]
        ping_row = ping_result[1]
        sht.range('M{0}'.format(ping_row)).value = ping_status

    print("Cat6k Ping result written into excel.")
    process_count = 100
    sht.range('A2').value = "Process -> {0}%".format(process_count)
    sht.range('A2').color = (153, 204, 0)

def _show_mac(ad_username, ad_password, apic_hostname, action, sht, NCM):
    process_count = 0
    sht.range('A2').value = "Process -> {0}%".format(process_count)
    sht.range('A2').color = None
    # ping.py
    end_row = sht.range('A3').end("down").row
    current_vlan_value = str(int(sht.range('K2').value))
    vlan_row_list = []

    for row_count in range(4, end_row + 1):
        vlan_value = str(int(sht.range('C{0}'.format(row_count)).value))
        if vlan_value == current_vlan_value:
            excel_ip = str(sht.range('A{0}'.format(row_count)).value)
            excel_mac = str(sht.range('B{0}'.format(row_count)).value).upper()
            vlan_row_list.append([row_count, excel_ip, excel_mac])

    first_row = vlan_row_list[0][0]
    last_row = vlan_row_list[-1][0]

    # reset M&N column
    sht.range('P{0}:P{1}'.format(first_row, last_row)).clear_contents()
    sht.range('P{0}:P{1}'.format(first_row, last_row)).color = None

    apic_username = "apic#tacacs\|||{0}".format(ad_username)
    show_endpoint = "show endpoints vlan {0} | grep vlan".format(current_vlan_value)
    ssh_session = _open_session(ad_username, ad_password, apic_username, ad_password, "on", NCM, apic_hostname, "enable")
    session_output = _special_issue_command(ssh_session, show_endpoint, action, apic_hostname)
    _close_session(ssh_session, "enable")

    # Extracting data from command outputs ...
with open("svi_endpoint_temp.txt", "r") as svi_endpoint_temp:
    command_output = svi_endpoint_temp.read()

    output = _extract_data(session_output, command_output)
    ip_list = []
    mac_list = []

    for element in output:
        ip = str(element[0])
        mac = str(element[11])
        ip_list.append(ip)
        mac_list.append(mac)

    for entry in vlan_row_list:
        row_count = entry[0]
        excel_ip = entry[1]
        excel_mac = entry[2]

        if excel_ip in ip_list:
            if excel_mac in mac_list:
                sht.range('P{0}'.format(row_count)).value = "Pass"
                sht.range('P{0}'.format(row_count)).color = (153, 204, 0)
            else:
                sht.range('P{0}'.format(row_count)).value = "Fail -> IP match but MAC missing in ACI endpoint table"
                sht.range('P{0}'.format(row_count)).color = (255, 0, 0)
        else:
            sht.range('P{0}'.format(row_count)).value = "Fail -> IP missing in ACI endpoint table"
            sht.range('P{0}'.format(row_count)).color = (255, 0, 0)

    if not output:
        sht.range('P{0}'.format(row_count)).value = "Failed, No IP and MAC matched"
        sht.range('P{0}'.format(row_count)).color = (255, 0, 0)



