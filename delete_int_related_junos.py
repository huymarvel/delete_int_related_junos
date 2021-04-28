import jinja2
import yaml
from datetime import date
import napalm
import os.path, shutil

now = date.today()
device={
        "username":"tdhuy",
        "password":"muahoado1C",
        "optional_args": {"port":22}
        }
		
#Delete old directory
path1 = "D:/Temp_py"
shutil.rmtree(path1, ignore_errors=True)
# Create folder Temp_py at disk D
if not os.path.exists(path1):
    os.makedirs(path1)
conf_file_name = f"D:/Temp_py/Config_{now.day}{now.month}{now.year}.txt"
delete_file_name = f"D:/Temp_py/Delete_{now.day}{now.month}{now.year}.txt"
replace_file_name = f"D:/Temp_py/Replace_{now.day}{now.month}{now.year}.txt"	
#prepare conf file function
def create_data(template_j2,data_conf):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."), lstrip_blocks=True, trim_blocks=True)
    template = env.get_template(template_j2)

    f = open(data_conf)
    data_tem_str = f.read()
    f.close()

    data_tem_dict = yaml.safe_load(data_tem_str)
    #print (data_tem_dict)
    configs = template.render(int = data_tem_dict)

    #outFileName=f"D:/Temp_py/Config_{now.day}{now.month}{now.year}.txt"
    outFile=open(conf_file_name, "w")
    outFile.write(configs)
    outFile.close()
	
#delete all_related config
def delete_all(ip_list_file):
    f = open(ip_list_file,"r")
    data_host = f.read()
    data_host = data_host.strip()
    data_host_lst = data_host.split(",")
    f.close()
    #print (data_host_lst)
    
    for IP_lo0 in data_host_lst:
        device["hostname"] = IP_lo0
        driver = napalm.get_network_driver("junos")
        try:
            print("Connecting to {}...".format(device["hostname"]))
            conn = driver(**device)
            conn.open()
        except:
            print("Check IP, username, password, port")
        else:
            print ("Connected successful")
            f = open(replace_file_name, "a")
            with open(conf_file_name, "r") as conf_f:
                for cli_input in conf_f.readlines():
                    cli_output =conn.cli([cli_input])			
                    for v in cli_output.values():
                        f.write(v)
                    f.write("\n")
            f.close() 
			#
            f = open(replace_file_name, "r")			
            data = f.read()
            data = data.replace("set", "delete")
            f.close()
            f = open(replace_file_name, "w")	
            f.write(data)
            f.close()
            
            print("Loading configuration...")
            conn.load_merge_candidate(filename = replace_file_name)
            conn.load_merge_candidate(filename = delete_file_name)
            print("Done")
            
            print()
            print("Comparing configuration...")
            diff = conn.compare_config()
            print(diff)
            
            print()
            choice = input("Do you want to commit?(y/n) ")
            if choice == "y":
                print("Committing...")
                conn.commit_config()
                print("Done!")
            else:
                print("Configuration is ignored")
                conn.discard_config()
            conn.close()
						
create_data("template_delete_int.j2","data_conf.yml")
shutil.copyfile(conf_file_name,delete_file_name)
create_data ("template_showconf_int_other.j2","data_conf.yml")

delete_all("ip_list_test.txt")



