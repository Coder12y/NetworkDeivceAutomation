import paramiko
import datetime

class UserInfo(object):
    def login_info(self):
        self.NCM = ""
        self.ad_username = ""
        self.ad_password = ""
        self._session = requests.Session()

def _open_session(ad_username, ad_password, ad_830_username, ad_830_password, disable_page, NCM, hostname, echo):
    # Establishes SSH session to device using paramiko
    # Create instance of SSHClient object
    device_pre = paramiko.SSHClient()
    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    device_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # initiate SSH connection
    try:
        device_pre.connect(NCM, port=8022, username=ad_username, password=ad_password, look_for_keys=False)
    except:
        raise Exception("login_failed")

    # Use invoke_shell to establish an 'interactive session'
    device_session = device_pre.invoke_shell()
    hostname = hostname.upper()
    terminal_screen = ""

    while 'NA›' not in terminal_screen:
        output = device_session.recv(1)
        output = ''.join(map(chr, output))
        terminal_screen = terminal_screen + output

    if echo == "enable":
        timestamp = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print("SSH connected to {} at {}".format(hostname, timestamp))

    if "SF001" in hostname:
        apic_fqdn = "{}.hk.hsbe".format(hostname)
        apic_username = "apic#tacacs\||\{}".format(ad_username)
        device_session.send("ssh {}\n{}\n{}\n".format(apic_fqdn, apic_username, ad_password))
    else:
        device_session.send("ssh {}\n{}\n{}\n".format(hostname, ad_username, ad_password))

    wrong_msg = "Failure Reason: Failed to connect via SSH to {} on port 22. Unknown host".format(hostname)

    if disable_page == "on":
        terminal_screen = ""
        while hostname + "#" not in terminal_screen:
            output = device_session.recv(1)
            output = "".join(map(chr, output))
            terminal_screen = terminal_screen + output

            if wrong_msg in terminal_screen:
                raise Exception("wrong_device")
                break

        device_session.send("terminal length 0\n")
        terminal_screen = ""
        while hostname + "#" not in terminal_screen:
            output = device_session.recv(1)
            output = "".join(map(chr, output))
            terminal_screen = terminal_screen + output

        return device_session

    elif disable_page == "off":
        terminal_screen = ""

def issue_command(device_session, hostname, command, echo):
    # Issues IOS/NX-OS commands and returns response
    if echo == "enable":
        timestamp = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print("{} - Issuing command '{}'".format(timestamp, command))

    device_session.send(command + "\n")
    hostname = hostname.upper()
    terminal_screen = ""

    while hostname + "#" not in terminal_screen:
        output = device_session.recv(1)
        output = ''.join(map(chr, output))
        terminal_screen = terminal_screen + output

    return terminal_screen

def issue_ping_command(devicesession, hostname, command, echo):
    # Issues IOS/NX-OS commands and returns response
    if echo == "enable":
        timestamp = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print("{} -› Issuing command '{}'".format(timestamp, command))
        
    devicesession.send(command + "\n")
    hostname = hostname.upper()
    terminal_screen = ""

    while hostname + "#" not in terminal_screen:
        output = devicesession.rec(1)
        output = ''.join(map(chr, output))
        terminal_screen = terminal_screen + output

    if "100.00% packet loss" in terminal_screen:
        return "no response"
    else:
        return "success"

def _close_session(devicesession, echo):
    # close session
    devicesession.close()
    
    if echo == "enable":
        timestamp = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print("{} -> SSH connection close\n".format(timestamp))
