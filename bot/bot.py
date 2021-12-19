import os
import random
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from discord import Embed
from discord.ext.commands import Bot
from discord.commands import slash_command, option, permissions

from utils import helper
from utils.github_api import DataHandler
from utils.helper import project_base_path


class PortalDocsBot(Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        load_dotenv(dotenv_path=str(project_base_path / ".env"))
        self.token = os.getenv("PD_DISCORD_TOKEN")
        self.dh = DataHandler(False if os.getenv("PD_DEVELOPMENT") else True)
        self.colors = ["011C26", "025159", "08A696", "26FFDF", "F26A1B", "FF2C10"]
        self.cogs_list = [
            f"bot.cogs.{i.stem}"
            for i in (project_base_path / "bot" / "cogs").glob("*.py")
            if i.name != "__init__.py"
        ]

    async def on_ready(self):
        logger.info("Bot Started Successfully")

    def load_custom_cogs(self):
        f"""
        Loads all the custom cogs defined in cogs/ 
        {self.cogs_list}
        :return: 
        """
        logger.debug(self.cogs_list)
        for cog in self.cogs_list:
            try:
                logger.debug(f"Trying to load {cog}")
                self.load_extension(cog)
            except BaseException as e:
                logger.critical(f"Failed Loading {cog} because of error {e}")
                raise
        logger.debug(f"Loading of all cogs successful")
