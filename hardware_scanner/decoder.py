import ndef
import serial
from selenium import webdriver
from selenium.webdriver.common.by import By
import re


ser_status = True
try:
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
    )
    ser_status = True
except serial.SerialException as e:
    ser_status = False
    print(e)
    # exit(1)

def decode_nfc_message(hex_data):
    byte_data = bytearray.fromhex(hex_data.replace(" ", "")[4:])
    
    decoded_records = list(ndef.message_decoder(byte_data))

    payload = decoded_records[0].data
    payload = payload.decode('utf-8') if isinstance(payload, bytes) else payload
    url = re.sub('\x04', 'https://', payload)
    return url


browser = webdriver.Chrome()
browser.get('https://blankwaard.eu')

msg_ex = "03 12 d1 01 0e 55 04 62 6c 61 6e 6b 77 61 61 72 64 2e 65 75 fe 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"

prev_line = ""
line = ""
while True:
    if ser_status:
        line = ser.readline()
        prev_line = line
        print(line.decode())

    if prev_line is not line:
        # url = decode_nfc_message(line.decode())
        url = decode_nfc_message(msg_ex)
        browser.get(url)
        




