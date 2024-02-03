#!/usr/bin/env python3

import os
import pygame.mixer
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080
bgmusic_dir = os.getenv("BGMUSIC_DIR")

pygame.mixer.init()

def daemon_begin():
    global bgmusic_dir
    if bgmusic_dir == None:
        raise Exception("No BGMUSIC_DIR found")
    song_path = bgmusic_dir + '/' + get_random_song(bgmusic_dir)
    print(song_path)

    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def daemon_resume():
    pygame.mixer.music.unpause()

def daemon_end():
    pygame.mixer.music.pause()

def daemon_exit():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    erase_port_config()

class RequestHandler(BaseHTTPRequestHandler):
    stop_server = False

    def _set_headers(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self._set_headers()
        data = post_data.decode("utf-8")

        self.handle_msg(data)

    def handle_msg(self, msg: str):
        if msg == "START":
            daemon_begin()
        elif msg == "RESUME":
            daemon_resume()
        elif msg == "STOP":
            daemon_end()
        elif msg == "EXIT":
            daemon_exit()
            RequestHandler.stop_server = True

def get_random_song(d: str) -> str:
    import random
    files = os.listdir(d)
    files= list(filter(lambda f:
        f.lower().endswith(".flac") or
        f.lower().endswith(".mp3") or
        f.lower().endswith(".ogg") or
        f.lower().endswith(".wav"),
    files))
    return random.choice(files)

def get_available_port() -> int:
    global PORT
    return PORT

def write_port_config(port: int):
    xdg_config_path = os.path.expanduser(os.path.join("~", ".config"))
    file_name = "bgmusic_port.txt"
    file_path = os.path.join(xdg_config_path, file_name)
    with open(file_path, "w") as f:
        f.write(str(port))

def erase_port_config():
    xdg_config_path = os.path.expanduser(os.path.join("~", ".config"))
    file_name = "bgmusic_port.txt"
    file_path = os.path.join(xdg_config_path, file_name)
    os.remove(file_path)

def run_server():
    port = get_available_port()
    write_port_config(port)

    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)

    print(f'bgmusicd started on {port}')
    while not RequestHandler.stop_server:
        httpd.handle_request()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
