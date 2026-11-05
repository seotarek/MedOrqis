#!/usr/bin/env python3
"""
MedOrqis — RunPod Cloud GPU Automation Manager
Manages RunPod on-demand GPU instances for zero-local-download model fine-tuning.

Usage:
    python3 training/runpod_manager.py status        # Check account balance & running pods
    python3 training/runpod_manager.py gpus          # List available GPUs and live prices
    python3 training/runpod_manager.py launch --gpu "A100 PCIe (80GB)"   # Launch training pod
    python3 training/runpod_manager.py terminate --pod_id <ID>           # Stop & terminate pod
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error

def _load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

_load_env_file()
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY", "")
if not RUNPOD_API_KEY:
    print("[ERROR] RUNPOD_API_KEY is not set. Please add it to your environment or .env file.")
    sys.exit(1)

RUNPOD_GRAPHQL_URL = f"https://api.runpod.io/graphql?api_key={RUNPOD_API_KEY}"


def execute_graphql(query: str, variables: dict = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    req = urllib.request.Request(
        RUNPOD_GRAPHQL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "MedOrqis-CloudManager/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Connection Error: {e}")
        sys.exit(1)


def check_status():
    query = """
    query MyselfStatus {
      myself {
        id
        email
        clientBalance
        pods {
          id
          name
          desiredStatus
          imageName
          machine {
            gpuDisplayName
          }
        }
      }
    }
    """
    res = execute_graphql(query)
    user = res.get("data", {}).get("myself", {})
    pods = user.get("pods", [])
    
    print("=" * 65)
    print("RUNPOD ACCOUNT & CLOUD POD STATUS")
    print("=" * 65)
    print(f"Email:          {user.get('email')}")
    print(f"User ID:        {user.get('id')}")
    print(f"Client Balance: ${user.get('clientBalance', 0.0):.2f}")
    print("-" * 65)
    
    if not pods:
        print("Active Pods:    0 (No pods currently running)")
    else:
        print(f"Active Pods:    {len(pods)}")
        for p in pods:
            gpu_name = p.get("machine", {}).get("gpuDisplayName", "Standard GPU")
            print(f"- Pod ID: {p.get('id')} | Name: {p.get('name')} | GPU: {gpu_name} | Status: {p.get('desiredStatus')}")
    print("=" * 65)


def list_gpus():
    query = """
    query GpuList {
      gpuTypes {
        id
        displayName
        memoryInGb
        lowestPrice(input: {gpuCount: 1}) {
          minimumBidPrice
          uninterruptablePrice
        }
      }
    }
    """
    res = execute_graphql(query)
    gpus = res.get("data", {}).get("gpuTypes", [])
    
    print("=" * 75)
    print("RECOMMENDED GPUS FOR MEDORQIS FOUNDATION MODEL TRAINING")
    print("=" * 75)
    print(f"{'GPU Model':<28} | {'VRAM':<6} | {'On-Demand':<12} | {'Suitability'}")
    print("-" * 75)
    
    targets = {
        "A100 PCIe (80GB)": "Karnak-40B QLoRA (Optimal / Best Value)",
        "A100 SXM (80GB)": "Karnak-40B QLoRA (High Speed SXM4)",
        "H100 SXM (80GB)": "Karnak-40B Full/QLoRA (Maximum Speed)",
        "RTX 6000 Ada (48GB)": "Karnak-40B QLoRA (Economy 48GB)",
        "RTX 4090 (24GB)": "Karnak-6B QLoRA Pilot ($0.34/hr)"
    }
    
    for g in gpus:
        name = g.get("displayName")
        if name in targets:
            mem = f"{g.get('memoryInGb')}GB"
            lp = g.get("lowestPrice") or {}
            price = lp.get("uninterruptablePrice")
            price_str = f"${price:.2f}/hr" if price is not None else "Checking..."
            print(f"{name:<28} | {mem:<6} | {price_str:<12} | {targets[name]}")
    print("=" * 75)


def launch_pod(gpu_type_id: str = "NVIDIA A100-PCIE-80GB", volume_in_gb: int = 100):
    mutation = """
    mutation CreatePod($input: PodFindAndDeployOnDemandInput!) {
      podFindAndDeployOnDemand(input: $input) {
        id
        imageName
        desiredStatus
      }
    }
    """
    docker_args = "bash -c 'git clone https://github.com/seotarek/MedOrqis.git && cd MedOrqis && bash training/runpod_bootstrap.sh'"
    
    variables = {
        "input": {
            "cloudType": "SECURE",
            "gpuCount": 1,
            "volumeInGb": volume_in_gb,
            "containerDiskInGb": 50,
            "minVcpuCount": 8,
            "minMemoryInGb": 64,
            "gpuTypeId": gpu_type_id,
            "name": "MedOrqis-Karnak-Trainer",
            "imageName": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
            "dockerArgs": docker_args,
            "startSsh": True
        }
    }
    
    print(f"Sending launch request to RunPod for GPU: {gpu_type_id}...")
    res = execute_graphql(mutation, variables)
    pod = res.get("data", {}).get("podFindAndDeployOnDemand", {})
    if pod and pod.get("id"):
        print(f"[SUCCESS] Pod launched! Pod ID: {pod.get('id')}")
        print("The pod will clone MedOrqis and execute training automatically in the cloud.")
    else:
        print("[RESPONSE]", json.dumps(res, indent=2))


def terminate_pod(pod_id: str):
    mutation = """
    mutation TerminatePod($input: PodTerminateInput!) {
      podTerminate(input: $input)
    }
    """
    res = execute_graphql(mutation, {"input": {"podId": pod_id}})
    print(f"[TERMINATED] Pod {pod_id} result:", res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedOrqis RunPod Manager")
    parser.add_argument("action", choices=["status", "gpus", "launch", "terminate"], help="Action to execute")
    parser.add_argument("--gpu", default="NVIDIA A100-PCIE-80GB", help="GPU Type ID for launch")
    parser.add_argument("--pod_id", default="", help="Pod ID for termination")
    args = parser.parse_args()
    
    if args.action == "status":
        check_status()
    elif args.action == "gpus":
        list_gpus()
    elif args.action == "launch":
        launch_pod(args.gpu)
    elif args.action == "terminate":
        if not args.pod_id:
            print("Error: --pod_id is required for terminate")
            sys.exit(1)
        terminate_pod(args.pod_id)
