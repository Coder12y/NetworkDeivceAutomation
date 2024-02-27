import textfsm

def extract_data(command_output, template):
    fsm = textfsm.TextFSM(template)
    return fsm.ParseText(command_output)

def _express_select(session_output, dir_path, command, device_type):
    if (device_type == "C6K" and command == "show ip arp") or (device_type == "N7K" and command == "show ip arp"):
        file_name = "{}_arp_temp.txt".format(device_type.lower())
        with open(dir_path + file_name, "r") as arp_temp_file:
            output = extract_data(session_output, arp_temp_file)
            output_dict = {}
            count = 0
            for each_entry in output:
                ip = each_entry[0]
                output_dict[ip] = [each_entry]
                mac = each_entry[1]

                if mac in output_dict.keys():
                    count = count + 1
                    output_dict[count] = each_entry
                else:
                    output_dict[mac] = each_entry

            return output_dict, count

    elif command == "show int status":
        with open(dir_path + "7k_int_temp.txt", "r") as n7k_int_temp:
            output = extract_data(session_output, n7k_int_temp)
            output_dict = {}

            for each_entry in output:
                interface = each_entry[0]
                output_dict[interface] = each_entry

            return output_dict

    elif command == "show ip eigrp nei":
        with open(dir_path + "7k_routing_temp.txt", "r") as n7k_routing_temp:
            output = extract_data(session_output, n7k_routing_temp)
            return output
        
    elif command == "show inventory":
        with open(dir_path + "7k_inventory_temp.txt", "r") as n7k_inventory_temp:
            output = extract_data(session_output, n7k_inventory_temp)
            return output

    elif command == "show vlan brief":
        with open(dir_path + "7k_vlan_temp.txt", "r") as n7k_vlan_temp:
            output = extract_data(session_output, n7k_vlan_temp)
            return output

    elif command == "show mac address-table dynamic | ex Po":
        with open(dir_path + "7k_mac_temp.txt", 'r') as n7k_mac_temp:
            output = extract_data(session_output, n7k_mac_temp)
            output_dict = {}
            for each_entry in output:
                mac = each_entry[1]
                output_dict[mac] = each_entry
            return output_dict

    elif command == "show int des":
        with open(dir_path + "7k_description_temp.txt", 'r') as n7k_des_temp:
            output = extract_data(session_output, n7k_des_temp)
            output_dict = {}
            for each_entry in output:
                interface = each_entry[0]
                output_dict[interface] = each_entry
            return output_dict

    elif command == "server_identify":
        with open(dir_path + "7k_server_identify_temp.txt", 'r') as n7k_server_identify_temp:
            output = extract_data(session_output, n7k_server_identify_temp)
            return output

    elif device_type == "ACI" and command == "show endpoints | grep eth":
        with open(dir_path + "ACI_endpoint_temp.txt", 'r') as aci_endpoint_temp:
            output = extract_data(session_output, aci_endpoint_temp)
            output_dict = {}
            for each_entry in output:
                char = each_entry[1].lower()
                mac_list = char.split(":")
                mac = mac_list[0] + mac_list[1] + ". " + mac_list[2] + mac_list[3] + ". " + mac_list[4] + mac_list[5]
                output_dict[mac] = each_entry
            return output_dict

    elif command == "server_identify":
        with open(dir_path + "ACI_identify_temp.txt", 'r') as aci_server_identify_temp:
            output = extract_data(session_output, aci_server_identify_temp)
            return output
