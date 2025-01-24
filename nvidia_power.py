import subprocess
import time

CMD_GPU = r"nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits"
CMD_TIME = r"nvidia-smi --query-gpu=timestamp --format=csv,noheader,nounits"

def get_gpu_power():
    output = subprocess.run(CMD_GPU,
                            shell=True,
                            stdout=subprocess.PIPE)
    return output.stdout.decode().rstrip().strip()
    
def get_time():
    output = subprocess.run(CMD_TIME,
                            shell=True,
                            stdout=subprocess.PIPE)
    return output.stdout.decode().rstrip().strip()

def print_data():
    output = ""
    output += f"GPU: {get_gpu_power()}\n"
    output += f"TIME: {get_time()}\n"
    return output

def save_data():
    with open('data/labels.csv', 'a') as file:
        file.write(get_gpu_power())
        file.write(", ") 
        file.write(get_time())
        file.write("\n")

def main():
    while(True):
        print(print_data())
        save_data()


if __name__ == "__main__":
    main()