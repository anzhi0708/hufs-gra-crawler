#!/usr/bin/python

import os
import sys
import time
import requests
import re
from bs4 import BeautifulSoup
from faker import Faker

COLS, LINES = os.get_terminal_size()

GRA_URL = "https://builder.hufs.ac.kr/user/indexSub.action?framePath=unknownboard&siteId=gra&dum=dum&boardId=91435460&page=1&command=list"

HEADERS = {"User-Agent": Faker().user_agent()}

NUM_READY = 0
NUM_ALL = 0

FLAG_1_by_1 = False 

if len(sys.argv) > 0:
    if sys.argv[1] == "-n":
        FLAG_1_by_1 = True
    else:
        sys.exit("Invalid argv[1]")


class NoticeBoard:
    """Gets each notification's title and link then store'em into a dict"""

    def __init__(self):
        global NUM_ALL
        self.base_url = "https://builder.hufs.ac.kr/user/"
        self.nodes = {}
        self.titles = []
        self.page = requests.get(GRA_URL, headers=HEADERS).text
        self.soup = BeautifulSoup(self.page, "html.parser")
        self.titles_target = self.soup.find_all("td", "title")
        del self.soup
        NUM_ALL = len(self.titles_target)
        self.link_pattern = re.compile(r"title\">[\s]*<a href=.*>")
        self.links = self.link_pattern.findall(self.page)
        for each_target in self.titles_target:
            self.titles.append(
                "".join(list(each_target.strings))
                .replace("\t", "")
                .replace("\n", "")
                .replace("\\xa0", "")
                .strip()
            )
        for index in range(NUM_ALL):
            self.nodes[self.titles[index]] = self.base_url + self.links[index].replace(
                'title">', ""
            ).replace("\n", "").replace("\t", "").replace("<a href=", "").replace(
                ">", ""
            ).replace(
                " ", ""
            ).replace(
                "'", ""
            )
        """Now adding Notification objects to list"""
        """We can get rid of everything else except {self.nodes}"""
        del self.titles_target, self.page, self.titles, self.links, self.link_pattern
        self._nodes = []
        for title in self.nodes.keys():
            self._nodes.append(Notification(title=title, link=self.nodes[title]))
        if not FLAG_1_by_1:
            self._load_all_then_print()

    def _load_all_then_print(self):
        for noti_obj in self._nodes:
            print()
            print(noti_obj)


class Notification:
    """Notification object"""

    def __init__(
        self, title=None, upload_time=None, views=None, has_file=None, link=None
    ):
        global NUM_READY
        global FLAG_1_by_1
        self.title = title
        self.upload_time = upload_time
        self.views = views
        self.has_file = has_file
        self.link = link
        self.text = ""
        if FLAG_1_by_1:
            self._get_notification()
            print(f"{'=' * COLS}\n\033[1m{self.title}\033[0m\n{self.link}\n{self.text}\n{'=' * COLS}\n")
        else:
            self._get_notification()
            NUM_READY += 1
            print(f"[!] {NUM_READY} / {NUM_ALL} been loaded")

    def _get_notification(self):
        self.page = requests.get(
            self.link, headers={"User-Agent": Faker().user_agent()}
        ).text
        self.soup = BeautifulSoup(self.page, "html.parser")
        self.target = self.soup.find_all("div", id="divView")
        text = self.target[0].findChildren("p")
        for each_child in text:
            self.text += "".join(
                list("".join(list(each_child.strings)).replace("\n", ""))
            )

    def __repr__(self):
        global COLS
        return f"{'=' * COLS}\n\033[1m{self.title}\033[0m\n{self.link}\n{self.text}\n{'=' * COLS}\n"


class App:
    def __init__(self):
        board = NoticeBoard()
        pass


if __name__ == "__main__":
    app = App()
