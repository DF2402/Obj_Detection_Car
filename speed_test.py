import serial
# this is a test script for UART communication
# it is used to send command to the robot
uart_port = '/dev/ttyTHS0'  # Replace with the correct UART port (e.g., ttyTHS1, ttyTHS2)
baud_rate = 115200          # Baud rahhhhte (e.g., 9600, 115200)
timeout = 1                 # Timeout for reading in seconds
        
try:
    ser = serial.Serial(
    port=uart_port,
    baudrate=baud_rate,
    timeout=timeout
    )
    print(f"Connected to {uart_port} with baud rate {baud_rate}")
except Exception as e:
    print(f"Error opening UART: {e}")
            #exit()
def send_data(data):
    if ser.isOpen():
        ser.write(data.encode())  # Convert string to bytes and send
        print(f"UART Command : {data}")
    else:
        print("UART port is not open!")
send_data("[+,80,+,80]")