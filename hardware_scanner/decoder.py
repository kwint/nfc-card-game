import ndef
import serial
from selenium import webdriver
import re


try:
    ser = serial.Serial(
        port="/dev/ttyACM0",
        baudrate=115200,
    )
except Exception as e:
    print(e)
    exit(1)


def decode_nfc_message(hex_data):
    byte_data = bytearray.fromhex(hex_data.replace(" ", "")[14:-10])

    # decoded_records = list(ndef.message_decoder(byte_data))

    # payload = decoded_records[0].data
    # payload = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    print(byte_data)
    payload = byte_data.decode('utf-8')
    url = re.sub("\x04", "https://", payload)
    return url


browser = webdriver.Chrome()

msg_ex = "03 12 d1 01 0e 55 04 62 6c 61 6e 6b 77 61 61 72 64 2e 65 75 fe 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"

ntag213_ex = "30 04 26 ee 30 05 af ff 30 06 34 cd 30 07 bd dc 30 08 4a 24 30 09 c3 35 30 0a 58 07 30 0b d1 16 30 0c 6e 62 30 0d e7 73 30 0e 7c 41 30 0f f5 50"

prev_line = ""
line = ""
while True:
    line = ser.readline()

    if prev_line != line:
        try:
            url = decode_nfc_message(line.decode())
            browser.get(url)
            prev_line = line
        except Exception as e:
            print(e)
