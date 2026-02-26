#! /usr/bin/env python3

class WordCountMapper:
    def __init__(self):
        pass

    def run_map(self, payload):
        data = {}
        for line in payload["data"]:
            for word in line.split(" "):
                if word not in data:
                    data[word] = 0
                data[word] += 1
        yield data


def get_task():
    return WordCountMapper()
