from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "ip": "192.168.1.1",
    "username": "your_username",
    "password": "your_password",
}

try:
    connection = ConnectHandler(**device)
    output = connection.send_command("show running-config")
    with open(f"{device['ip']}_config_backup.txt", "w") as file:
        file.write(output)
    print("配置备份完成")
except Exception as e:
    print(f"无法连接到设备或备份配置失败: {str(e)}")
finally:
    connection.disconnect()
