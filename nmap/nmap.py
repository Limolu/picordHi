import subprocess
import re

def scan_network(target_mac):
    # 使用nmap掃描區域網路主機
    try:
        print("Scanning the network...")
        result = subprocess.run(
            ["nmap", "-sP", "-n", "192.168.42.0/24"],  # 修改為你的區域網路網段
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print("Error running nmap:", result.stderr)
            return None
        
        output = result.stdout
        # 符合IP位址和MAC位址的格式
        ip_mac_pattern = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})\s+.*\s+MAC Address:\s+([0-9A-F:]+)")
        
        for match in ip_mac_pattern.finditer(output):
            ip, mac = match.groups()
            if mac.replace(":", "").lower() == target_mac.lower():
                return ip
        
        print("No matching MAC address found.")
        return None

    except Exception as e:
        print("Error:", e)
        return None


if __name__ == "__main__":
    target_mac = "ee:3a:4a:ac:f5:81"  # 替換為目標MAC位址
    ip = scan_network(target_mac)
    if ip:
        print(f"The IP address for MAC {target_mac} is: {ip}")
    else:
        print("No IP address found for the given MAC.")
