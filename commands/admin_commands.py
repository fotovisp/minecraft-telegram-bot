import logging
from user_commands import User_Commands
import asyncio
from aiogram import types

logger = logging.getLogger(__name__)


class Admin_Commands(User_Commands):
    async def backup_mc(self, message: types.Message):
        if self.check_admin_permission(message.from_user.id):
            await message.answer("starting backup to 4 disks...")
            res = await self.run_remote(f"bash {self.mc_dir}/backup.sh")
            await message.answer(f"done! logs: {res[:50]}")
            logger.info(
                f"backup command executed by admin {message.from_user.id}, logs: {res[:50]}"
            )

    async def stop_mc(self, message: types.Message):
        if self.check_admin_permission(message.from_user.id):
            await self.run_remote(f"mcrcon -P 25575 -p {self.rcon_pwd} 'stop'")
            await message.answer("shutdowning...")
            await asyncio.sleep(15)
            await message.answer("server is shutdowned")
            logger.info(f"stop command executed by admin {message.from_user.id}")

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
                    logger.info(f"admin {message.from_user.id} started server")
                    break
                else:
                    temp_msg = await message.answer("no response, keep trying")
                    await asyncio.sleep(30)
                    await temp_msg.delete()
            logger.error(f"admin {message.from_user.id} powered on the server")

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
            logger.info(f"admin {message.from_user.id} powered off the server")
