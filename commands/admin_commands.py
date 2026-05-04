from user_commands import User_Commands
import asyncio
from aiogram import types

class Admin_Commands(User_Commands):
    def check_admin_permission(self, usr_id):
        if usr_id == self.admin_id:
            return True
        return False
    async def backup_mc(self, message: types.Message):
        if self.check_admin_permission(message.from_[user.id](http://user.id)):
            await message.answer("starting backup to 4 disks...")
            res = await [self.run](http://self.run)_remote(f"bash {[self.mc](http://self.mc)_dir}/[backup.sh](http://backup.sh)")
            await message.answer(f"done! logs: {res[:50]}")
    async def stop_mc(self, message: types.Message):
        if self.check_admin_permission(message.from_[user.id](http://user.id)):
            await [self.run](http://self.run)_remote(f"mcrcon -P 25575 -p {self.rcon_pwd} 'stop'")
            await message.answer("shutdowning...")
            await asyncio.sleep(15)
            await message.answer("server is shutdowned")
    async def power_on_server(self, message: types.Message):
        if self.check_admin_permission(message.from_[user.id](http://user.id)):
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
                if await self.async_ping([self.dell](http://self.dell)_host):
                    await message.answer("server is powered on")
                    break
                else:
                    temp_msg = await message.answer("no response, keep trying")
                    await asyncio.sleep(30)
                    await temp_msg.delete()
    async def power_off_server(self, message: types.Message):
        if message.from_[user.id](http://user.id) == self.admin_id:
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

