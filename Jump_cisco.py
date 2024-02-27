import paramiko
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

def connect_to_cisco(hostname, username, password, command):
    # 创建 SSH 客户端
    client = paramiko.SSHClient()
    # 自动添加缺失的主机密钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接到 Cisco 设备
        client.connect(hostname, username=username, password=password, timeout=10)
        print(f"成功连接到 Cisco 设备 {hostname}")

        # 执行命令
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        return output
    except Exception as e:
        print(f"连接到 Cisco 设备 {hostname} 失败: {str(e)}")
        return None
    finally:
        # 关闭 SSH 连接
        client.close()

def save_to_excel(output_data, filename):
    # 创建 Excel 文件
    workbook = Workbook()
    sheet = workbook.active

    # 设置标题样式
    title_style = Font(bold=True, size=14)
    sheet['A1'].font = title_style

    # 设置单元格对齐
    align_center = Alignment(horizontal='center', vertical='center')
    sheet['A1'].alignment = align_center

    # 添加标题
    sheet['A1'] = 'Command Output'

    # 将数据写入 Excel
    for row_num, row_data in enumerate(output_data, start=2):
        sheet.cell(row=row_num, column=1, value=row_data).alignment = align_center

    # 保存 Excel 文件
    workbook.save(filename)
    print(f"数据已保存到 {filename}")

def main():
    # Cisco 设备信息
    cisco_info = {
        "hostname": "your_cisco_ip",
        "username": "your_username",
        "password": "your_password",
        "command": "show interfaces"
    }

    # 连接到 Cisco 设备并获取命令输出
    command_output = connect_to_cisco(cisco_info["hostname"], cisco_info["username"],
                                      cisco_info["password"], cisco_info["command"])

    if command_output:
        # 将命令输出保存到 Excel 文件
        save_to_excel([command_output], 'cisco_output.xlsx')

if __name__ == "__main__":
    main()
