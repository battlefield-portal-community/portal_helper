import os
import sys
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    logger.add(sys.stderr, format="{time}{level}{message}", filter="my_module", level=int(os.getenv("PD_LOG_LEVEL")))
    Path("logs").mkdir(exist_ok=True)
    logger.add(r"logs\log_{time}", retention=7, rotation="500 MB", level="DEBUG")
    logger.info("Starting Bot ...")
    try:
        from .bot import PortalDocsBot
        bot = PortalDocsBot(command_prefix="!")
        bot.load_custom_cogs()
        bot.run(bot.token)
    except ConnectionError as e:
        logger.critical(f"Unable to connect to Discord. exit error {e}")
        raise
    except KeyboardInterrupt as e:
        logger.info(f"Exiting app...")
        exit(0)

    except BaseException as e:
        logger.critical(f"Error {e} happened when stating the bot ")
        raise
