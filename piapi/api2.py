import nmap
import re
import asyncio
import threading
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# 全局變數用於存儲掃描到的目標 IP 地址
red_ip = None
light_ip = None

async def scan_for_mac_async(network_range, target_macs):
    """
    使用 nmap 異步掃描網路範圍，並提取指定 MAC 地址的 IP。
    
    :param network_range: 掃描的網路範圍，例如 '192.168.1.0/24'
    :param target_macs: 要匹配的目標 MAC 地址列表，例如 ['00:1A:2B:3C:4D:5E', 'AA:BB:CC:DD:EE:FF']
    :return: 返回 MAC 地址與 IP 地址的映射字典
    """
    global red_ip, light_ip
    nm = nmap.PortScanner()
    print(f"正在掃描網路範圍: {network_range}")
    
    mac_to_ip = {mac: None for mac in target_macs}

    try:
        nm.scan(hosts=network_range, arguments='-sn')
        for host in nm.all_hosts():
            if 'addresses' in nm[host] and 'mac' in nm[host]['addresses']:
                mac_address = nm[host]['addresses']['mac']
                ip_address = nm[host]['addresses'].get('ipv4', '未知IP')
                
                # 檢查是否匹配目標 MAC 地址
                for target_mac in target_macs:
                    if re.fullmatch(target_mac, mac_address, re.IGNORECASE):
                        print(f"匹配到目標 MAC: {mac_address}，IP 地址: {ip_address}")
                        mac_to_ip[target_mac] = ip_address

        # 更新全局變數
        red_ip = mac_to_ip.get(target_macs[0])
        light_ip = mac_to_ip.get(target_macs[1])
        print(f"更新結果 - Red IP: {red_ip}, Light IP: {light_ip}")
    except Exception as e:
        print(f"掃描失敗: {e}")

async def periodic_scan():
    """
    每隔五分鐘執行一次掃描。
    """
    network_range = '192.168.1.0/24'  # 根據實際網路修改
    target_macs = [r'00:1A:2B:3C:4D:5E', r'AA:BB:CC:DD:EE:FF']  # 目標 MAC 地址列表
    while True:
        await scan_for_mac_async(network_range, target_macs)
        await asyncio.sleep(300)  # 等待 5 分鐘


# red1
@app.route('/red1_on', methods=['GET'])
def turn_on():
    """
    向目標 ESP8266 發送開啟請求。
    """
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/on1')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "已開啟 red1"}), 200
            else:
                return jsonify({"status": "error", "message": "無法開啟 red1"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red1 設備"}), 404

@app.route('/red1_off', methods=['GET'])
def turn_off():
    """
    向目標 ESP8266 發送關閉請求。
    """
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/off1')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "已關閉 red1"}), 200
            else:
                return jsonify({"status": "error", "message": "無法關閉 red1"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red1 設備"}), 404

"""
@app.route('/red1_status', methods=['GET'])
def get_status():
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/status1')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "獲取狀態成功", "data": response.json()}), 200
            else:
                return jsonify({"status": "error", "message": "無法獲取 red1 狀態"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red1 設備"}), 404
"""


# red2
@app.route('/red2_on', methods=['GET'])
def turn_on():
    """
    向目標 ESP8266 發送開啟請求。
    """
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/on2')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "red2 已開啟"}), 200
            else:
                return jsonify({"status": "error", "message": "無法開啟 red2"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red2 設備"}), 404

@app.route('/red2_off', methods=['GET'])
def turn_off():
    """
    向目標 ESP8266 發送關閉請求。
    """
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/off2')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "red2 已關閉"}), 200
            else:
                return jsonify({"status": "error", "message": "無法關閉 red2"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red2 設備"}), 404

"""
@app.route('/red2_status', methods=['GET'])
def get_status():
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/status2')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "獲取狀態成功", "data": response.json()}), 200
            else:
                return jsonify({"status": "error", "message": "無法獲取 red2 狀態"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red2 設備"}), 404
"""


# red3
@app.route('/red3_on', methods=['GET'])
def turn_on():
    """
    向目標 ESP8266 發送開啟請求。
    """
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/on3')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "red3 已開啟"}), 200
            else:
                return jsonify({"status": "error", "message": "無法開啟 red3"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red3 設備"}), 404

@app.route('/red3_off', methods=['GET'])
def turn_off():
    """
    向目標 ESP8266 發送關閉請求。
    """
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/off3')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "red3 已關閉"}), 200
            else:
                return jsonify({"status": "error", "message": "無法關閉 red3"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red3 設備"}), 404

"""
@app.route('/red3_status', methods=['GET'])
def get_status():
    if red_ip:
        try:
            response = requests.get(f'http://{red_ip}/status3')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "獲取狀態成功", "data": response.json()}), 200
            else:
                return jsonify({"status": "error", "message": "無法獲取 red3 狀態"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 red3 設備"}), 404
"""


# light
@app.route('/light_on', methods=['GET'])
def light_on():
    """
    向目標 Light ESP8266 發送開啟請求。
    """
    if light_ip:
        try:
            response = requests.get(f'http://{light_ip}/on')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "Light ESP8266 已開啟"}), 200
            else:
                return jsonify({"status": "error", "message": "無法開啟 Light ESP8266"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 Light ESP8266 設備"}), 404

@app.route('/light_off', methods=['GET'])
def light_on():
    """
    向目標 Light ESP8266 發送開啟請求。
    """
    if light_ip:
        try:
            response = requests.get(f'http://{light_ip}/off')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "Light ESP8266 已關閉"}), 200
            else:
                return jsonify({"status": "error", "message": "無法關閉 Light ESP8266"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 Light ESP8266 設備"}), 404

"""
@app.route('/light_status', methods=['GET'])
def get_status():
    if light_ip:
        try:
            response = requests.get(f'http://{light_ip}/status')
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "獲取狀態成功", "data": response.json()}), 200
            else:
                return jsonify({"status": "error", "message": "無法獲取 Light ESP8266 狀態"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"請求失敗: {e}"}), 500
    return jsonify({"status": "error", "message": "未找到 Light ESP8266 設備"}), 404
"""

if __name__ == '__main__':
    # 啟動掃描任務
    loop = asyncio.get_event_loop()
    threading.Thread(target=lambda: loop.run_until_complete(periodic_scan()), daemon=True).start()
    
    # 啟動 Flask API
    try:
        app.run(host='0.0.0.0', port=81)
    except KeyboardInterrupt:
        print("服務已停止")
