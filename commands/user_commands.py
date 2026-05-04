from telegram_bot import Telegram_Bot
import asyncio
from aiogram import types


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
                await message.answer("server is empty or server is starting")
            elif "Error" in res:
                await message.answer(
                    "error: server is not running or there is an issue with the server\nplease contact the admin"
                )
            else:
                await message.answer(res)
