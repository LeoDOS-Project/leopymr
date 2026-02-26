#! /usr/bin/env python3

class MergeCombiner:
    def __init__(self):
        pass

    def combine(self, data, payload):
        result = {}
        for d in data:
            for k in d:
                if k not in result:
                    result[k] = 0
                result[k] += d[k]
        return result


def get_task():
    return MergeCombiner()
