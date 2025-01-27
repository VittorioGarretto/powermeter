import subprocess
import time

# Using only one GPU
CMD_GPU = r"nvidia-smi -i 0 --query-gpu=power.draw --format=csv,noheader,nounits"

def get_gpu_power():
    output = subprocess.run(CMD_GPU,
                            shell=True,
                            stdout=subprocess.PIPE)
    return output.stdout.decode().rstrip().strip()

def print_data():
    output = ""
    output += f"GPU: {get_gpu_power()}\n"
    output += f"TIME: {time.time()}\n"
    return output

def save_data():
    with open('labels.csv', 'a') as file:
        file.write(get_gpu_power())
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