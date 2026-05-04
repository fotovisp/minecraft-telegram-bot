import os
import asyncio
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
from fabric import Connection

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


class Telegram_Bot(Config):
    def __init__(self):
        super().__init__()
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()

        self.dp.message.register(self.start, Command("start"))

        self.dp.message.register(self.start_mc, F.text == "start")
        self.dp.message.register(self.stop_mc, F.text == "stop")
        self.dp.message.register(self.restart_mc, F.text == "restart")
        self.dp.message.register(self.list_mc, F.text == "list")
        self.dp.message.register(self.backup_mc, F.text == "backup")
        self.dp.message.register(self.power_on_server, F.text == "power on")
        self.dp.message.register(self.power_off_server, F.text == "power off")

        self.dp.message.register(self.status_server, F.text == "status")

    async def run_remote(self, command):
        def sync_run():
            try:
                with Connection(host=self.dell_host, user=self.dell_user) as c:
                    result = c.run(command, hide=True)
                    return result.stdout.strip()
            except Exception as e:
                return f"Error: {e}"

        return await asyncio.to_thread(sync_run)

    async def idrac_remote(self, command):
        def sync():
            try:
                # i made ssh connection to idrac without password using ssh keys, so there is no need to pass user and password in the command
                with Connection(host="idrac", connect_timeout=20) as c:
                    result = c.run(command, hide=True, pty=True, timeout=30)
                    return result.stdout.strip()
            except Exception as e:
                return f"Error: {e}"

        return await asyncio.to_thread(sync)

    async def start(self, message: types.Message):
        id = message.from_user.id
        if id == self.admin_id:
            kb = [
                [types.KeyboardButton(text="start"), types.KeyboardButton(text="stop")],
                [
                    types.KeyboardButton(text="restart"),
                    types.KeyboardButton(text="list"),
                    types.KeyboardButton(text="backup"),
                ],
                [
                    types.KeyboardButton(text="status"),
                    types.KeyboardButton(text="power on"),
                    types.KeyboardButton(text="power off"),
                ],
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer("mc_control:", reply_markup=keyboard)

        elif id in self.users_id:
            kb = [
                [
                    types.KeyboardButton(text="start"),
                    types.KeyboardButton(text="restart"),
                ],
                [
                    types.KeyboardButton(text="list"),
                    types.KeyboardButton(text="status"),
                ],
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer("mc_control:", reply_markup=keyboard)


class User_Commands(Telegram_Bot):
    def check_user_permission(self, usr_id):
        if usr_id == self.admin_id or usr_id in self.users_id:
            return True
        return False

    async def async_ping(self, host):
        process = await asyncio.create_subprocess_exec(
            "ping",
            "-c",
            "1",
            "-W",
            "2",
            host,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()
        return process.returncode == 0

    async def start_mc(self, message: types.Message):
        if self.check_user_permission(message.from_user.id):
            check_command = f"tmux has-session -t {self.tmux_session} 2>/dev/null && echo 'running' || echo 'stopped'"
            status = await self.run_remote(check_command)

            if "running" in status:
                await message.answer("server is already running")
                return

            await message.answer("starting...")
            res = await self.run_remote(
                f"cd {self.mc_dir} && tmux new-session -d -s {self.tmux_session} 'bash run.sh nogui' && echo 'success'"
            )

            if "success" in res:
                await asyncio.sleep(5)
                await message.answer("done!")
            else:
                if message.from_user.id == self.admin_id:
                    await message.answer(f"error: {res}")
                else:
                    await message.answer(
                        "error: server is already running or there is an issue with the server\nplease contact the admin"
                    )

    async def stop_mc(self, message: types.Message):
        if self.check_user_permission(message.from_user.id):
            await self.run_remote(f"mcrcon -P 25575 -p {self.rcon_pwd} 'stop'")
            await message.answer("shutdowning...")
            await asyncio.sleep(15)
            await message.answer("server is shutdowned")

    async def restart_mc(self, message: types.Message):
        if self.check_user_permission(message.from_user.id):
            for i in range(10, 0, -1):
                await self.run_remote(
                    f"mcrcon -P 25575 -p {self.rcon_pwd} 'say SERVER RESTART IN {i} SECONDS!'"
                )
                await asyncio.sleep(1)
            await self.run_remote(f"mcrcon -P 25575 -p {self.rcon_pwd} 'stop'")
            await message.answer("restarting...")

            res = await self.run_remote(
                f"cd {self.mc_dir} && tmux new-session -d -s {self.tmux_session} 'bash run.sh nogui' && echo 'success'"
            )
            if "success" in res:
                await asyncio.sleep(8)
                await message.answer("done!")
            else:
                if message.from_user.id == self.admin_id:
                    await message.answer(f"error: {res}")
                else:
                    await message.answer(
                        "error: server is already running or there is an issue with the server\nplease contact the admin."
                    )

    async def status_server(self, message: types.Message):
        if self.check_user_permission(message.from_user.id):
            status_msg = await message.answer(
                "checking if server connected to electricity"
            )
            pwr_status_raw = await self.idrac_remote("racadm serveraction powerstatus")

            if "ON" in pwr_status_raw:
                pwr_status = "server is powered ON"

                check_command = f"tmux has-session -t {self.tmux_session} 2>/dev/null && echo 'running' || echo 'stopped'"
                status = await self.run_remote(check_command)

                if "running" in status:
                    tmux_session_status = "minecraft is running"
                else:
                    tmux_session_status = "minecraft is NOT running"
            else:
                pwr_status = "server is powered OFF"
                tmux_session_status = "minecraft is NOT running"

            answer_user = f"{pwr_status}\n{tmux_session_status}"
            await status_msg.delete()
            await message.answer(answer_user)

    async def list_mc(self, message: types.Message):
        if self.check_user_permission(message.from_user.id):
            res = await self.run_remote(
                f"/usr/local/bin/mcrcon -P 25575 -p {self.rcon_pwd} 'list'"
            )
            if not res or res.strip() == "":
                res = "server is empty or server is starting"
                await message.answer(res)
            elif "Error" in res:
                await message.answer(
                    "error: server is not running or there is an issue with the server\nplease contact the admin"
                )
            else:
                await message.answer(res)


class Admin_Commands(User_Commands):
    def check_admin_permission(self, usr_id):
        if usr_id == self.admin_id:
            return True
        return False

    async def backup_mc(self, message: types.Message):
        if self.check_admin_permission(message.from_user.id):
            await message.answer("starting backup to 4 disks...")
            res = await self.run_remote(f"bash {self.mc_dir}/backup.sh")
            await message.answer(f"done! logs: {res[:50]}")

    async def stop_mc(self, message: types.Message):
        if self.check_admin_permission(message.from_user.id):
            await self.run_remote(f"mcrcon -P 25575 -p {self.rcon_pwd} 'stop'")
            await message.answer("shutdowning...")
            await asyncio.sleep(15)
            await message.answer("server is shutdowned")

    async def power_on_server(self, message: types.Message):
        if self.check_admin_permission(message.from_user.id):
            await message.answer("check if the server is connected to electricity")
            if await self.async_ping(self.ip_idrac):
                await message.answer("server is connected to electricity")
            else:
                await message.answer("server is NOT connected to electricity")
                return

            await message.answer("trying to power on")
            await self.idrac_remote("racadm serveraction powerup")
            await message.answer("bot will send a message when the server power on")
            await asyncio.sleep(240)
            for _ in range(10):
                if await self.async_ping(self.dell_host):
                    await message.answer("server is powered on")
                    break
                else:
                    temp_msg = await message.answer("no response, keep trying")
                    await asyncio.sleep(30)
                    await temp_msg.delete()

    async def power_off_server(self, message: types.Message):
        if message.from_user.id == self.admin_id:
            await message.answer("check if the server is connected to electricity")
            if await self.async_ping(self.ip_idrac):
                await message.answer("server is connected to electricity")
            else:
                await message.answer("server is NOT connected to electricity")
                return

            await message.answer("trying to power off")
            await self.idrac_remote("racadm serveraction gracefulshutdown")
            await asyncio.sleep(5)
            await self.idrac_remote("racadm serveraction powerdown")
            await message.answer("shutdowning...")
            await asyncio.sleep(10)
            await message.answer("server is powered off")
