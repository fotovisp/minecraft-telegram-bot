from commands.admin_commands import (
    Admin_Commands,
)  # importing admin_commands, because it contains other files
import asyncio


async def main():
    app = Admin_Commands()
    await app.dp.start_polling(app.bot)


if __name__ == "__main__":
    asyncio.run(main())
