import paho.mqtt.client as mqtt # type: ignore
import time
import subprocess

BROKER_IP = "host_ip"  
CMD_GPU = f"nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits"

def get_gpu_power():
    output = subprocess.run(CMD_GPU,
                            shell=True,
                            stdout=subprocess.PIPE)
    return output.stdout.decode().rstrip().strip().splitlines()

def on_request(client, userdata, msg):
    print("Received request for nvidia-smi")

    labels = get_gpu_power()
    read_time = str(time.time())
    string_labels = ','.join(map(str, labels)) + "," + read_time

    client.publish("vm/nvidia_data", string_labels, qos=0)
    print("Data sent")

client = mqtt.Client(client_id="vm_responder")
client.on_message = on_request

client.connect(BROKER_IP, 1883, 60)
client.subscribe("vm/request_nvidia", qos=0)

client.loop_forever()