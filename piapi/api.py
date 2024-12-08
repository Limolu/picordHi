from flask import Flask, jsonify
import RPi.GPIO as GPIO

app = Flask(__name__)

# 設定 GPIO 模式和腳位
GPIO.setmode(GPIO.BCM)
GPIO_PIN = 16
GPIO.setup(GPIO_PIN, GPIO.OUT)

# GPIO 開啟
@app.route('/gpio_on', methods=['GET'])
def gpio_on():
    GPIO.output(GPIO_PIN, GPIO.HIGH)
    return jsonify({"status": "GPIO is ON"}), 200

# GPIO 關閉
@app.route('/gpio_off', methods=['GET'])
def gpio_off():
    GPIO.output(GPIO_PIN, GPIO.LOW)
    return jsonify({"status": "GPIO is OFF"}), 200

# 獲取 GPIO 狀態
@app.route('/gpio_status', methods=['GET'])
def gpio_status():
    state = GPIO.input(GPIO_PIN)
    status = "ON" if state == GPIO.HIGH else "OFF"
    return jsonify({"status": f"GPIO is {status}"}), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=80)
    except KeyboardInterrupt:
        GPIO.cleanup()