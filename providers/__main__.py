import shlex
import subprocess
from . import providers_port_mapping

if __name__ == '__main__':
    processes = []
    for provider in providers_port_mapping:
        proc = subprocess.Popen(shlex.split(f"python -m providers.{provider}"))
        processes.append(proc)

    for proc in processes:
        proc.wait()
