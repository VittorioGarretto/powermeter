import torch
import argparse
import time
import numpy as np

def check_gpu() -> bool:
	return torch.cuda.is_available()

def select_gpu(gpu_id: int) -> str:
	num_gpus = torch.cuda.device_count()
	assert gpu_id >= 0 
	assert gpu_id < num_gpus - 1
	device = f"cuda:{gpu_id}"
	return device

def stress_gpu(device: str, batch: int) -> None:
	timeout = time.time() + 25
	a = torch.randn((batch, batch), dtype=torch.float32).to(device)
	while(True):
		a = a @ a 
		if time.time() > timeout: 
			break
	del a
	torch.cuda.empty_cache()
	torch.cuda.ipc_collect()
   

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Stress test for GPU with matrix multiplications")
	parser.add_argument("--gpu_id", type=int, default=0, help="GPU ID to use")
	parser.add_argument("--batch", type=int, default=100, help="matrix size for the stress test")
	args = parser.parse_args()

	if check_gpu: 
		device = select_gpu(args.gpu_id)
	threshold = args.batch
	batch = np.random.randint(low=threshold, high=threshold+10)
	print(f"Batch used: {batch}")
	stress_gpu(device, batch)