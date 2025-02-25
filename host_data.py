import paho.mqtt.client as mqtt
import ast
import time
import subprocess

# Power readings, files should be executable
SCRIPTS = ["./ram_power.sh", "./nvme_power.sh", "./storage_power.sh",
           "./nic_power.sh", "./cpu_power.sh"]
PATH = "power-scripts/"

entity = "smartplug_id"

# Setting up the csv file to be used as pandas df
with open('data.csv', 'a') as file:
    file.write('timestamp,ac_frequency,current,energy,linkquality,power,state,voltage,')
    file.write('ram_power,nvme_power,storage_power,nic_power,cpu_power,psu_eff\n')


def shell_read(script):
    output = subprocess.run(script,
                            shell=True,
                            stdout=subprocess.PIPE)
    return output.stdout.decode().rstrip().strip()


# Callback function to handle incoming messages
def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    payload_dict = ast.literal_eval(msg.payload.decode()) #generating data dict
    payload_dict['state'] = 1 if payload_dict['state']=='ON' else 0 #converting ON/OFF in binary values
    payload_val = payload_dict.values()
    efficiency = shell_read(f"{PATH}./psu_eff.sh {payload_dict['power']} 850 Platinum")  # Need 3 arg: power, max load, rating
    
    with open('data.csv', 'a') as file:
        file.write(str(time.time()))
        file.write(",")
        for val in payload_val:
            file.write(str(val))
            file.write(",")
        for script in SCRIPTS:
            script = PATH + script
            file.write(shell_read(script))
            file.write(",")
        file.write(efficiency)
        file.write("\n")


# Callback function for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        # Subscribe to the topic for the entity
        client.subscribe(f"zigbee2mqtt/{entity}", qos=0)
        print(f"Subscribed to topic: zigbee2mqtt/{entity}")
    else:
        print(f"Connection failed with code {rc}")


# Create MQTT client and set up callbacks
client = mqtt.Client(client_id="zigbee_reader")
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
try:
    client.connect("localhost", 1883, 60)
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

# Start the loop to process messages
client.loop_forever()