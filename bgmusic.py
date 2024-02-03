#!/usr/bin/env python3

import os
import requests
import subprocess
from sys import argv

VALID_INPUTS = [
    "START",
    "RESUME",
    "STOP",
    "EXIT",
]

def send_message(message: str, port: int):
    data = message
    server_url='http://localhost:' + str(port)
    requests.post(server_url, data=data)

def get_daemon_port() -> int | None:
    xdg_config_path = os.path.expanduser(os.path.join("~", ".config"))
    file_name = "bgmusic_port.txt"
    file_path = os.path.join(xdg_config_path, file_name)

    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return int(content.strip())
    except FileNotFoundError:
        print("bgmusicd likely isn't running")
        return None

def validate_input(i: str) -> bool:
    global VALID_INPUTS
    for inpt in VALID_INPUTS:
        if i == inpt:
            return True
    return False

def setup_daemon():
    subprocess.Popen(["bgmusicd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True)

if __name__ == "__main__":
    port = get_daemon_port()
    if port == None:
        raise Exception("No valid port found")

    user_input = argv[1].upper()

    if user_input == "SETUP":
        setup_daemon()
        exit(0)
    if not validate_input(user_input):
        raise Exception(f"Invalid input = {user_input}")
    send_message(user_input, port)
