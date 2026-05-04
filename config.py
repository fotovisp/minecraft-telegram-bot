import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.dell_host = os.getenv("dell_host")
        self.dell_user = os.getenv("dell_user")
        self.mc_dir = os.getenv("mc_dir")
        self.rcon_pwd = os.getenv("rcon_pwd")
        self.token = os.getenv("token")
        self.admin_id = int(os.getenv("admin_id"))
        self.users_id = [int(uid) for uid in json.loads(os.getenv("users_id", "[]"))]
        self.tmux_session = os.getenv("tmux_session", "mc")
        self.mc_dir = os.getenv("mc_dir")
        self.ip_idrac = os.getenv("ip_idrac")
        self.user_idrac = os.getenv("user_idrac")
        self.password_idrac = os.getenv("password_idrac")
