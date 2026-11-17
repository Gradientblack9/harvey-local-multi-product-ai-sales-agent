import json
import os
import subprocess
import psutil

def recommend(ram_gb, gpu_vram_gb=0):
    if ram_gb < 8:
        return "qwen3:1.7b", "Low memory: start with 1.7B and close other applications."
    if ram_gb >= 24 or gpu_vram_gb >= 8:
        return "qwen3:8b", "Enough memory for an 8B model; benchmark before increasing context."
    return "qwen3:4b", "4B balances memory and quality on this machine. CPU inference may take a few minutes per task."

def inspect():
    ram = round(psutil.virtual_memory().total/1024**3,1)
    available = round(psutil.virtual_memory().available/1024**3,1)
    gpus = []
    try:
        flags = getattr(subprocess,"CREATE_NO_WINDOW",0)
        result = subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv,noheader,nounits"],capture_output=True,text=True,timeout=3,creationflags=flags)
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                name, memory = line.rsplit(",",1)
                gpus.append({"name":name.strip(),"vram_gb":round(float(memory)/1024,1)})
    except (OSError,subprocess.TimeoutExpired,ValueError):
        pass
    model, reason = recommend(ram,max((g["vram_gb"] for g in gpus),default=0))
    return {"ram_gb":ram,"available_ram_gb":available,"cpu_cores":psutil.cpu_count(logical=False),"cpu_threads":os.cpu_count(),"gpus":gpus,"recommended_model":model,"reason":reason,
            "guideline":"The PRD suggests 8B on 16 GB+. This implementation uses a conservative 24 GB RAM or 8 GB VRAM threshold to leave room for the OS, browser and embeddings."}
