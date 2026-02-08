#! /sr/bin/env python3
from config import config
import time

def log(msg,sat=None,context=None,verbosity=1):
  if verbosity > config.VERBOSITY:
    return
  action = ""
  target = ""
  if not sat is None:
    target = f"(sat={sat.get_id()}) "
  if not context is None:
    if "action" in context: 
      action = f"(action={context['action']}) "
    if "target_sat" in context and target == "": 
      target = f"(sat={context['target_sat'].get_id()}) "
  print(f"COMPDEBUG: [{time.time()}] (level={verbosity}) {target}{action}{msg}")

