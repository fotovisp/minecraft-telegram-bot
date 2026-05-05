from commands.admin_commands import (
    Admin_Commands,
)  # importing admin_commands, because it contains other files
import asyncio
import logging

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(filename="mc-tg-bot.log", level=logging.INFO)
    app = Admin_Commands()
    await app.dp.start_polling(app.bot)
    logger.info("Bot started polling")


if __name__ == "__main__":
    asyncio.run(main())
