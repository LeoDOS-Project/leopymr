#! /sr/bin/env python3
from config import config
import time

def log(msg,sat=None,context=None,verbosity=1):
  if verbosity > config.VERBOSITY:
    return
  if not sat is None:
    target = f"(sat={sat.get_id()}) "
  else:
    target = ""
  if not context is None:
    if "action" in context: 
      action = f"(action={context['action']}) "
  else:
    action = ""
  print(f"COMPDEBUG: [{time.time()}] (level={verbosity}) {target}{action}{msg}")

