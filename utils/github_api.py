from requests import get
import json
import base64
from pathlib import Path
from markdown import markdown
from bs4 import BeautifulSoup
from loguru import logger


class DataHandler:
    def __init__(self, update: bool = True):
        self.github_endpoint = r"https://api.github.com/repos/LennardF1989/BF2042-Portal-Docs/git/trees/master?recursive=1"
        self.github_sha_base_url = r"https://api.github.com/repos/LennardF1989/BF2042-Portal-Docs/git/blobs/{}"
        self.local_file_path = Path(__file__).parents[1] / "data/blocks_info"
        Path(self.local_file_path).parent.mkdir(exist_ok=True)
        Path(self.local_file_path).touch(exist_ok=True)
        self.__md = markdown
        self.docs_dict = dict()
        if update:
            self.update_data()

    def update_data(self):
        logger.debug("Updating GitHub data")
        git_tree_json = get(self.github_endpoint).json()["tree"]
        for item in git_tree_json:
            path = Path(item["path"])
            if path.match("docs/blocks/*.md"):
                if path.name in ["index.md", "IndexOfFirstTrue.md"]:
                    pass
                else:
                    self.docs_dict.update({path.stem.lower(): [item["sha"], path.stem]})
        self.docs_dict.update({
            "countof":
                [
                    "bb74624e448dee2d919aa0d071ab16374c5e4c32",
                    "CountOf"
                ]
        })
        with open(self.local_file_path, 'w') as FILE:
            json.dump(self.docs_dict, FILE)
        logger.debug("Updating GitHub Complete")

    def load_data(self):
        logger.debug("Loading GitHub Data")
        with open(self.local_file_path) as FILE:
            tmp = FILE.read()
        try:
            json_data = json.loads(tmp)
        except json.JSONDecodeError:
            raise

        self.docs_dict = json_data
        logger.debug("Loading GitHub Data Complete")

    def get_doc(self, target):
        if target not in self.docs_dict.keys():
            return ValueError("Specified Block not found")
        url = self.github_sha_base_url.format(self.docs_dict[target][0])

        try:
            data = get(url).json()
            if data.get("message") == "Not Found":
                raise ValueError("incorrect sha value")
            content = base64.b64decode(data["content"]).decode('utf-8')
        except ValueError:
            raise
        html = BeautifulSoup(markdown(content), features="html.parser")
        for tag in html.find_all("code"):
            tag.decompose()
        return html.text


if __name__ == "__main__":
    DataHandler().update_data()
    # dh = DataHandler()
    # dh.update_data()
    # doc_list = dh.get_doc("countof").split('\n')
    # content = ''
    # inputs = ''
    # output = ''
    # title = doc_list[0]
    # if "Inputs" in doc_list:
    #     content = doc_list[1:doc_list.index("Inputs")]
    # else:
    #     content = doc_list[1:]
    # if "Output" in doc_list:
    #     inputs = doc_list[doc_list.index("Inputs")+1:doc_list.index("Output")]
    #     output = doc_list[doc_list.index("Output") + 1:]
    # else:
    #     inputs = doc_list[doc_list.index("Inputs") + 1:]
    #
    # print(title, content, inputs, output)
    # print(doc_list)
