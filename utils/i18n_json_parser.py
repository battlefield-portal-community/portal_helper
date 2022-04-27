import re
from typing import TypedDict

import requests
import json
import functools
from loguru import logger

from helper import project_base_path


class RawJson(TypedDict):
    summary: dict
    keywords: dict
    case: dict


class TransDict(TypedDict):
    sid: str
    localizedText: str
    categoryId: int


class Parser:
    def __init__(self):
        self.version = "2507586"
        self.json_file = project_base_path / "data" / f"{self.version}.json"
        self.raw_json = dict()
        self.parsed_json = dict()

    def get_json(self):
        self.raw_json: RawJson
        trans: TransDict
        huge_trans: dict
        k: str
        v: str

        self.raw_json["summary"] = {}
        self.raw_json["keywords"] = {}
        self.raw_json["case"] = {}

        with open(project_base_path / "data" / "translations.json", 'w') as JSON_FILE:
            logger.debug("Getting latest translations")
            huge_trans = requests.get("https://api.gametools.network/bf2042/translations/?lang=en-us").json()[
                "localizedTexts"]
            logger.debug("Got it.....")
            for trans in huge_trans:
                if trans['sid'].startswith(('ID_ARRIVAL_BLOCK', 'ID_ARRIVAL_MODBUILDER')):
                    self.raw_json["keywords"].update({trans['sid']: trans['localizedText']})
                    self.raw_json["case"].update({trans['localizedText'].lower(): trans['localizedText']})

                elif trans['sid'].startswith("PYRITE"):
                    self.raw_json["keywords"].update({trans['sid']: trans['localizedText']})
                elif trans['sid'].startswith("help."):
                    self.raw_json["summary"].update({trans['sid']: trans['localizedText']})

            for key in self.raw_json.keys():
                self.raw_json[key] = dict(sorted(self.raw_json[key].items()))

            # add custom keys

            self.raw_json['case'].update({
                "controlselse": "Else",
                "condition": "CONDITION",
                "controlselseif": "ElseIf",
                "controlsif": "If",
                "showgamemodemessage": "DisplayGameModeMessage",
                "showhighlightedmessage": "DisplayHighlightedWorldLogMessage",
            })

            json.dump(self.raw_json, JSON_FILE)
        logger.info("Filtered and saved Translations")
        self.parse_json()

    def parse_json(self):
        key: str
        val: str
        trans: RawJson

        logger.debug(f"Parsing JSON v.{self.version}")
        with open(project_base_path / "data" / "translations.json") as TRANS_FILE:
            trans = json.load(TRANS_FILE)

        skip_list = [f"help.{i}.summary" for i in ["enablevospawning", "getvehiclestate"]]
        rule_content = []
        rule_summary = ''

        for key, val in trans['summary'].items():
            key_parts = key.split(".")
            if not key.startswith("help.common") and key not in skip_list and val:
                pyrite_keys = re.finditer(r'\**\**%{(.*?)}\**\**', val)
                match: re.Match
                new_str = ''
                nm = ''
                for match in pyrite_keys:
                    group = match.groups()[0]
                    if group.startswith(("ID", "PY")):
                        # ID_ARRIVAL_BLOCK_SHOWNOTIFICATIONMESSAGE, PYRITE_ACTIONS
                        new_str = trans['keywords'][group]
                    elif group.startswith("help"):
                        # help.common.value-true
                        new_str = trans['summary'][group]

                    val = val.replace(match.group(), f"**{new_str}**")

                if key_parts[1] == 'rule':
                    if key_parts[-1] not in ["summary", "typesofrule"]:
                        if key_parts[-1] == "ongamemodeending":
                            key_parts[-1] = "ONGAMEMODE"
                        base_name = key_parts[-1].upper()
                        try:
                            event_name = trans['keywords'][f'ID_ARRIVAL_MODBUILDER_EVENT_{base_name}']
                        except KeyError:
                            event_name = trans['keywords'][f'PYRITE_EVENT_{base_name}']
                        val = f"**{event_name}**\n"+val

                    if key_parts[-1] != "summary":
                        rule_content.append(val)
                    else:
                        rule_summary = val



                else:
                    block = key_parts[1]
                    if new_name := trans['keywords'].get(f"ID_ARRIVAL_BLOCK_{block.upper()}", None):
                        nm = new_name
                    elif new_name := trans['keywords'].get(f"PYRITE_TYPE_{block.upper()}", None):
                        nm = new_name
                    elif new_name := trans['keywords'].get(f"PYRITE_{block.upper()}", None):
                        nm = new_name
                    else:
                        nm = block

                    try:
                        trans_key = trans['case'][nm.lower()]
                    except KeyError:
                        trans['case'][nm.lower()] = nm
                        trans_key = nm
                    self.parsed_json[trans_key] = val
        rule_content.append(rule_summary)
        self.parsed_json['Rule'] = '\n'.join(rule_content[::-1])
        logger.debug(f"Parsed {len(self.parsed_json.keys())} blocks")
        self.save_json()

    def save_json(self):
        with open(self.json_file, 'w') as JSON_FILE:
            json.dump(self.parsed_json, JSON_FILE)
        logger.debug(f"saved json for v.{self.version}")


if __name__ == '__main__':
    p = Parser()
    # p.get_json()
    p.parse_json()
