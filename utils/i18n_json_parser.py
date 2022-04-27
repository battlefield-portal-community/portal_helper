import re
import requests
import json
import functools
from loguru import logger

from helper import project_base_path


class Parser:
    def __init__(self):
        self.version = "2507586"
        self.json_file = project_base_path / "data" / f"{self.version}.json"
        self.raw_json: dict
        self.raw_json = dict()
        self.parsed_json = dict()

    def get_json(self, force=False):
        if not self.json_file.exists() and not force:
            if force:
                logger.info("Force download i18n json")
            else:
                logger.info("New Version of i18n json found downloading...")
            self.raw_json = requests.get(f"https://portal.battlefield.com/{self.version}/assets/i18n/en-US.json").json()
            with open((project_base_path / "data" / f"raw_{self.version}.json"), 'w') as JSON_FILE:
                json.dump(self.raw_json, JSON_FILE)
            self.parse_json()
        else:
            logger.info("Version already exists... skipping download")
            with open(self.json_file) as JSON_FILE:
                self.parsed_json = json.load(JSON_FILE)

    def parse_json(self):
        if self.raw_json:
            logger.debug(f"Parsing JSON v.{self.version}")
            self.raw_json: dict
            self.raw_json['PYRITE_TYPE_TEXT'] = 'TEXT'
            help_json = self.raw_json['help']
            for key, val in help_json.items():
                if key is not "common":
                    summary: str
                    summary = val.get('summary', '')
                    pyrite_keys = re.finditer(r'\**\**%{(.*?)}\**\**', summary)
                    match: re.Match
                    for match in pyrite_keys:
                        group = match.groups()[0]
                        if group.startswith("ID"):
                            # ID_ARRIVAL_BLOCK_SHOWNOTIFICATIONMESSAGE
                            new_str = group.split("_")[-1]
                        elif group.startswith("help"):
                            # help.common.value-true
                            new_str = functools.reduce(dict.get, group.split(".")[1:], help_json)
                        else:
                            # anything else PYRITE_ACTIONS
                            new_str = self.raw_json[group]
                        summary = summary.replace(match.group(), f"**{new_str}**")
                    self.parsed_json[key] = summary
            logger.debug(f"Parsed {len(self.parsed_json.keys())} blocks")
            self.save_json()

    def save_json(self):
        with open(self.json_file, 'w') as JSON_FILE:
            json.dump(self.parsed_json, JSON_FILE)
        logger.debug(f"saved json for v.{self.version}")


if __name__ == '__main__':
    p = Parser()
    p.parse_json()
