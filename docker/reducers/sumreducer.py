#! /usr/bin/env python3

class SumReducer:
    def __init__(self):
        pass

    def reduce(self, payloads):
        data = {}
        for payload in payloads:
            for k in payload["data"].keys():
                if k not in data:
                    data[k] = 0
                data[k] += payload["data"][k]
        return data


def get_task():
    return SumReducer()
