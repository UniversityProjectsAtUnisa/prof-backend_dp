import shlex
import subprocess
from common.utils import get_env_variable

port = get_env_variable("PORT", 8000)
commands = ["python -m providers", f"uvicorn main:app --host=0.0.0.0 --port={port}"]

if __name__ == '__main__':
    processes = []
    for command in commands:
        proc = subprocess.Popen(shlex.split(command))
        processes.append(proc)

    for proc in processes:
        proc.wait()
