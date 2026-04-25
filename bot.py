import os
import asyncio
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
from fabric import Connection

load_dotenv()

dell_host = os.getenv("dell_host")
dell_user = os.getenv("dell_user")
mc_dir = os.getenv("mc_dir")
rcon_pwd = os.getenv("rcon_pwd")
token = os.getenv("token")
admin_id = int(os.getenv("admin_id"))
users_id = [int(uid) for uid in json.loads(os.getenv("users_id", "[]"))]
tmux_session = os.getenv("tmux_session", "mc")
mc_dir = os.getenv("mc_dir")
ip_idrac = os.getenv("ip_idrac")
user_idrac = os.getenv("user_idrac")
password_idrac = os.getenv("password_idrac")


bot = Bot(token=token)
dp = Dispatcher()


async def run_remote(command):
    def sync_run():
        try:
            with Connection(host=dell_host, user=dell_user) as c:
                result = c.run(command, hide=True)
                return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    return await asyncio.to_thread(sync_run)


async def idrac_remote(command):
    def sync():
        try:
            # i made ssh connection to idrac without password using ssh keys, so there is no need to pass user and password in the command
            with Connection(host="idrac", connect_timeout=20) as c:
                result = c.run(command, hide=True, pty=True, timeout=30)
                return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    return await asyncio.to_thread(sync)


@dp.message(Command("start"))
async def start(message: types.Message):
    id = message.from_user.id
    if id == admin_id:
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

    elif id in users_id:
        kb = [
            [types.KeyboardButton(text="start"), types.KeyboardButton(text="restart")],
            [types.KeyboardButton(text="list"), types.KeyboardButton(text="status")],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("mc_control:", reply_markup=keyboard)


@dp.message(F.text == "list")
async def list_mc(message: types.Message):
    if message.from_user.id == admin_id or message.from_user.id in users_id:
        res = await run_remote(f"/usr/local/bin/mcrcon -P 25575 -p {rcon_pwd} 'list'")
        if not res or res.strip() == "":
            res = "server is empty or server is starting"
            await message.answer(res)
        elif "Error" in res:
            await message.answer(
                "error: server is not running or there is an issue with the server\nplease contact the admin"
            )
        else:
            await message.answer(res)


@dp.message(F.text == "start")
async def start_mc(message: types.Message):
    if message.from_user.id == admin_id or message.from_user.id in users_id:
        check_command = f"tmux has-session -t {tmux_session} 2>/dev/null && echo 'running' || echo 'stopped'"
        status = await run_remote(check_command)

        if "running" in status:
            await message.answer("server is already running")
            return

        await message.answer("starting...")
        res = await run_remote(
            f"cd {mc_dir} && tmux new-session -d -s {tmux_session} 'bash run.sh nogui' && echo 'success'"
        )

        if "success" in res:
            await asyncio.sleep(5)
            await message.answer("done!")
        else:
            if message.from_user.id == admin_id:
                await message.answer(f"error: {res}")
            else:
                await message.answer(
                    "error: server is already running or there is an issue with the server\nplease contact the admin"
                )


@dp.message(F.text == "restart")
async def restart_mc(message: types.Message):
    if message.from_user.id == admin_id or message.from_user.id in users_id:
        for i in range(10, 0, -1):
            await run_remote(
                f"mcrcon -P 25575 -p {rcon_pwd} 'say SERVER RESTART IN {i} SECONDS!'"
            )
            await asyncio.sleep(1)
        await run_remote(f"mcrcon -P 25575 -p {rcon_pwd} 'stop'")
        await message.answer("restarting...")

        res = await run_remote(
            f"cd {mc_dir} && tmux new-session -d -s {tmux_session} 'bash run.sh nogui' && echo 'success'"
        )
        if "success" in res:
            await asyncio.sleep(8)
            await message.answer("done!")
        else:
            if message.from_user.id == admin_id:
                await message.answer(f"error: {res}")
            else:
                await message.answer(
                    "error: server is already running or there is an issue with the server\nplease contact the admin."
                )


@dp.message(F.text == "stop")
async def stop_mc(message: types.Message):
    if message.from_user.id == admin_id:
        await run_remote(f"mcrcon -P 25575 -p {rcon_pwd} 'stop'")
        await message.answer("shutdowning...")
        await asyncio.sleep(15)
        await message.answer("server is shutdowned")


@dp.message(F.text == "backup")
async def backup_mc(message: types.Message):
    if message.from_user.id == admin_id:
        await message.answer("starting backup to 4 disks...")
        res = await run_remote(f"bash {mc_dir}/backup.sh")
        await message.answer(f"done! logs: {res[:50]}")


async def async_ping(host):
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


@dp.message(F.text == "power on")
async def power_on_server(message: types.Message):
    if message.from_user.id == admin_id:
        await message.answer("check if the server is connected to electricity")
        if await async_ping(ip_idrac):
            await message.answer("server is connected to electricity")
        else:
            await message.answer("server is NOT connected to electricity")
            return

        await message.answer("trying to power on")
        await idrac_remote("racadm serveraction powerup")
        await message.answer("bot will send a message when the server power on")
        await asyncio.sleep(240)
        for i in range(10):
            if await async_ping(dell_host):
                await message.answer("server is powered on")
                break
            else:
                temp_msg = await message.answer("no response, keep trying")
                await asyncio.sleep(30)
                temp_msg.delete()


@dp.message(F.text == "power off")
async def power_off_server(message: types.Message):
    if message.from_user.id == admin_id:
        await message.answer("check if the server is connected to electricity")
        if async_ping(ip_idrac):
            await message.answer("server is connected to electricity")
        else:
            await message.answer("server is NOT connected to electricity")
            return

        await message.answer("trying to power off")
        await idrac_remote("racadm serveraction gracefulshutdown")
        await asyncio.sleep(5)
        await idrac_remote("racadm serveraction powerdown")
        await message.answer("shutdowning...")
        await asyncio.sleep(10)
        await message.answer("server is powered off")


@dp.message(F.text == "status")
async def status_server(message: types.Message):
    if message.from_user.id == admin_id or message.from_user.id in users_id:
        status_msg = await message.answer("checking if server connected to electricity")
        pwr_status_raw = await idrac_remote("racadm serveraction powerstatus")

        if "ON" in pwr_status_raw:
            pwr_status = "server is powered ON"

            check_command = f"tmux has-session -t {tmux_session} 2>/dev/null && echo 'running' || echo 'stopped'"
            status = await run_remote(check_command)

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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
