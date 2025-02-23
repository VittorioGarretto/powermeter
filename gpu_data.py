import subprocess
import time

CMD_GPU = r"nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits"

def get_gpu_power():
    output = subprocess.run(CMD_GPU,
                            shell=True,
                            stdout=subprocess.PIPE)
    return output.stdout.decode().rstrip().strip().splitlines()

def print_data():
    output = ""
    output += f"GPU: {get_gpu_power()}\n"
    output += f"TIME: {time.time()}\n"
    return output

def save_data():
    power = map(float, get_gpu_power())
    label = sum(power)
    with open('labels.csv', 'a') as file:
        file.write(str(label))
        file.write(",") 
        file.write(str(time.time()))
        file.write("\n")

def main():
    while(True):
        print(print_data())
        save_data()

if __name__ == "__main__":
    with open('labels.csv', 'a') as file:
        file.write('gpu_power,timestamp\n')
    main()