import subprocess
import sys
import os 

if __name__ == "__main__":
    while True:
        process = subprocess.Popen([sys.executable, "webhook.py"])
        os.system(f"title Successfully logged into Zalo.")
        process.wait()
        