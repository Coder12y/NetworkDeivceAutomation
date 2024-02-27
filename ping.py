import os

devices = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

for device in devices:
    response = os.system("ping -c 1 " + device)
    if response == 0:
        print(f"{device} 可达")
    else:
        print(f"{device} 不可达")
