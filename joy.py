import usb_hid
import struct
import time
import analogio
import digitalio
import board

# 🎮 Joystick and Button Pins
joystick1_x = analogio.AnalogIn(board.A0)  # GP26 (ADC0)
joystick1_y = analogio.AnalogIn(board.A1)  # GP27 (ADC1) (Shared)
joystick1_btn = digitalio.DigitalInOut(board.GP22)
joystick1_btn.switch_to_input(pull=digitalio.Pull.UP)

joystick2_x = analogio.AnalogIn(board.A2)  # GP28 (ADC2)
joystick2_y = analogio.AnalogIn(board.A3)  # GP27 (Shared with Joystick 1)
joystick2_btn = digitalio.DigitalInOut(board.GP21)
joystick2_btn.switch_to_input(pull=digitalio.Pull.UP)

# 🔍 Find the Gamepad HID device
gamepad_device = None
for device in usb_hid.devices:
    if device.usage_page == 1 and device.usage == 5:
        gamepad_device = device
        break

if not gamepad_device:
    raise RuntimeError("Gamepad HID device not found!")

# 📌 Read joystick and scale values (-127 to 127)
def read_joystick(adc):
    raw = int(((adc.value / 65535) * 254) - 127)
    return 0 if abs(raw) < 5 else raw  # Apply dead zone

# 📌 Send HID Gamepad Report (6 Bytes)
def send_gamepad(x1, y1, x2, y2, buttons):
    report = struct.pack("<BBbbbb", 4, buttons & 0xFF, x1, y1, x2, y2)  # Must be exactly 6 bytes
    gamepad_device.send_report(report)

# 🚀 Main Loop
while True:
    x1 = -read_joystick(joystick1_x)  # Invert X1 axis (ONLY for Joystick 1)
    y1 = read_joystick(joystick1_y)  
    time.sleep(0.005)  # Small delay to allow ADC to stabilize
    x2 = read_joystick(joystick2_x)  # Keep X2 normal
    y2 = read_joystick(joystick2_y)  

    btn1 = not joystick1_btn.value  # 1 if pressed, 0 otherwise
    btn2 = not joystick2_btn.value

    buttons = (btn1 << 0) | (btn2 << 1)  # Combine button states

    send_gamepad(x1, y1, x2, y2, buttons)

    time.sleep(0.02)  # Stability delay
