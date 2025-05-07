import bot
import config
import database
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#asyncio.run(database.init_db())
bot.main(config._TOKEN)