#! /sr/bin/env python3
from config import config
import time


def log(msg, sat=None, context=None, verbosity=1):
    if verbosity > config.VERBOSITY:
        return
    action = ""
    target = ""
    msg_id = ""
    if sat is not None:
        target = f"(sat={sat.get_id()}) "
    if context is not None:
        if "action" in context:
            action = f"(action={context['action']}) "
        if "target_sat" in context and target == "":
            target = f"(sat={context['target_sat'].get_id()}) "
        if "isl_msgid" in context:
            msg_id = f"(msg={context['isl_msgid']}) "

    print(
        f"COMPDEBUG: [{
            time.time()}] (level={verbosity}) {target}{action}{msg_id}{msg}")
