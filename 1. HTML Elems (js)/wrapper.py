import os
import sys
import subprocess
import time
import re

def pkill(name):
    os.system(f"pkill -f {name}")

def get_used_ports():
    # Execute the ss command to get a list of used ports
    result = subprocess.run(['ss', '-tuln'], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.split('\n')

    used_ports = set()
    for line in lines:
        if 'LISTEN' in line:
            parts = line.split()
            # Extract the port number from the last column, which is in the form *:port or [::]:port
            port = parts[-1].split(':')[-1]
            if port.isdigit():
                used_ports.add(int(port))
    return used_ports

def check_port(port1):
    try:
        # Run netstat command and grep the port
        result = subprocess.check_output(['netstat', '-tulpn'], text=True)
        if str(port1) in result:
            print('True: Port is used')
            return True
        else:
            print("False: Port is not used")
            return False
    except subprocess.CalledProcessError as e:
        print("False: Port is not used")
        return False
    except Exception as e:
        print("False: Port is not used")
        return False

def get_ports(max_ports=200, start_port = 11001):
    used_ports = get_used_ports()
    available_ports = []

    for port in range(start_port, 65536):
        if len(available_ports) >= max_ports:
            break
        if port not in used_ports:
            available_ports.append(port)

    return available_ports

def get_website_root(url):
    try:
        website_root = url.split("://")[1]
        if 'www' in website_root:
            website_root = '_'.join(website_root.split('.')[1:])
        else:
            website_root = '_'.join(website_root.split('.'))
        website_root = website_root.replace('/', '-')
    except Exception as e:
        print((url + "\n") * 1000)
        print(e)
        website_root = url.replace('/', '-')
    return website_root

def start_server(url, extn):
    pkill('wpr')
    time.sleep(1)
    [temp_port1, temp_port2] = get_ports(2, 11001)
    website_root = get_website_root(url)
    go_path = '/home/character/go/src/github.com/catapult-project/catapult/web_page_replay_go/'
    wpgro_filepath = f'/home/character/replay_1/broken_site_tracker/09-08/{extn}_{website_root}.wprgo'

    os.chdir(go_path)

    cmd = ['go', 'run', 'src/wpr.go', 'replay', '--http_port='+str(temp_port1), '--https_port='+str(temp_port2), wpgro_filepath]
    print((' '.join(cmd) + "\n") * 100)
    process = subprocess.Popen(cmd, env = os.environ.copy(), stdout = sys.stdout, stderr = sys.stdout)
    print('start servers', process, process.pid)
    # os.system(" ".join(cmd))
    for i in range(10):
        print(f'Waiting for port {temp_port1} to be occupied')
        time.sleep(2)
        if check_port(temp_port1):
            break

    if not check_port(temp_port1):
        process.kill()
        return

def get_wpr_ports():
    flag = False
    result = subprocess.check_output(['netstat', '-tulpn'], text=True)
    for line in result.split('\n'):
        if 'wpr' in line:
            pattern = r'\d+\.\d+\.\d+\.\d+:(\d+)'
            match = re.search(pattern, line)
            if match:
                flag = True
                print(match.group(1))
    if not flag:
        print("Server Not Started")


 
def main():
    if len(sys.argv) < 2:
        print("Usage: ./wrapper.py {function} {parameters}")
        sys.exit(1)

    # The first argument is the function name
    func_name = sys.argv[1]

    # All subsequent arguments are passed to the function
    func_args = sys.argv[2:]

    try:
        # Get the function by name from the current module
        func = getattr(sys.modules[__name__], func_name)
    except AttributeError:
        print(f"Function '{func_name}' not found")
        sys.exit(1)

    # Call the function with the provided arguments
    func(*func_args)



if __name__ == "__main__":
    main()
