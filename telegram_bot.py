import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from fabric import Connection
from config import Config


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
