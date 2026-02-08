#! /usr/bin/env python3

from types import SimpleNamespace
import os

max_orb = os.getenv("MAX_ORB",100)
max_sat = os.getenv("MAX_SAT",100)
inclination = os.getenv("INCLINATION",87)
altitude = os.getenv("ALTITUDE",530)
earth_radius = os.getenv("EARTH_RADIUS",6371)
verbosity = os.getenv("VERBOSITY",1)

config = SimpleNamespace(
        MAX_ORB=int(max_orb),
        MAX_SAT=int(max_sat),
        INCLINATION=int(inclination),
        ALTITUDE=int(altitude),
        EARTH_RADIUS=int(earth_radius),
        VERBOSITY=int(verbosity),
  )
