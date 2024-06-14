import serial
import time

# Set up the serial connection (change 'COM3' to your Arduino's COM port)
arduino = serial.Serial(port='COM7', baudrate=115200, timeout=1)

def read_temperature():
    command = f"T\n"
    arduino.write(command.encode())
    arduino.write(b'T')  # Sending command to read temperature (if necessary)
    data = arduino.readline().decode().strip()  # Read the serial data
    # data = arduino.readline().decode()
    print(data)
    try:
        return float(data)
    except ValueError:
        return None

def update_controller(value):
    command = f"CONTROLLER={value}\n"
    arduino.write(command.encode())

def update_setpoint(value):
    command = f"SETPOINT={value}\n"
    arduino.write(command.encode())

def stop_experiment():
    arduino.write(b'STOP\n')
    print("Experiment stopped.")

def start_experiment():
    arduino.write(b'START\n')
    print("Experiment started.")


def send_command(command):
    arduino.write((command + '\n').encode())
    time.sleep(0.1)  # Small delay to ensure command is fully sent

# Function to set the speed for all motors
def set_speeds(speeds):
    command = f"SPEED {' '.join(map(str, speeds))}"
    send_command(command)

# Function to set volume and speed for all motors
def set_volumes_and_speeds(volume_speed_pairs):
    command = "VOLUME " + ' '.join(' '.join(map(str, pair)) for pair in volume_speed_pairs)
    send_command(command)

# Function to stop all motors
def stop_all():
    send_command("STOP")

# Function to reset all motors
def reset_all_motors(speed, delay_time):
    command = f"RESET {speed} {delay_time}"
    send_command(command)



def main():
    
    current_controller_value = 3
    current_setpoint_value = 40
    start_experiment()  # Start the experiment at the beginning
    start_time = time.time()

    # Initialize an array to hold the temperature data
    temperature_data = []

    with open('temperature_log_40_1_int0_155real.txt', 'a') as file:
        try:
            while True:
                temperature = read_temperature()
                if temperature is not None:
                    elapsed_time = time.time() - start_time
                    file.write(f'{elapsed_time:.2f} seconds, {temperature:.2f} °C\n')
                    # temperature_data.append((elapsed_time, temperature))
                    print(f'Temperature: {temperature:.2f} °C, Time: {elapsed_time:.2f} seconds')
                else:
                    print('Failed to read temperature')

                # Example of updating controller value (commented out)
                # current_controller_value += 1
                # if current_controller_value > 10:
                #     current_controller_value = 3
                # update_controller(current_controller_value)
                # print(f'Controller value set to: {current_controller_value}')
                
                # Update setpoint value
                current_setpoint_value = 40
                # update_setpoint(current_setpoint_value) 

                # set_speeds([500, 500, 500, 500, 500])
                # reset_all_motors(300, 5)
                set_volumes_and_speeds([(2000, 0), (5000, -100), (150000, 10000), (100000, -500), (500000, 100)]) # microliters and microliters per second


                time.sleep(1)  # Wait 2 seconds before the next update

        except KeyboardInterrupt:
            # Handle Ctrl+C to stop the experiment
            stop_experiment()
            print("Experiment interrupted by user.")

            # Write temperature data to file
            # with open('temperature_log.txt', 'a') as file:
            #     for elapsed_time, temperature in temperature_data:
            #         file.write(f'{elapsed_time:.2f} seconds, {temperature:.2f} °C\n')

            print("Temperature data saved to 'temperature_log.txt'.")


if __name__ == '__main__':
    main()