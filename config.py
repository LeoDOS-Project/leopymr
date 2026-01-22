#! /usr/bin/env python3

from types import SimpleNamespace
import os

max_orb = os.getenv("MAX_ORB",100)
max_sat = os.getenv("MAX_SAT",100)
inclination = os.getenv("INCLINATION",87)
altitude = os.getenv("ALTITUDE",530)
min_communications_altitude = os.getenv("MIN_COMMUNICATIONS_ALTITUDE",100000)
earth_radius = os.getenv("EARTH_RADIUS", 6371)
processing_time = os.getenv("PROCESSING_TIME", 1)
reduce_processing_time = os.getenv("REDUCE_PROCESSING_TIME", 1)
hop_overhead = os.getenv("HOP_OVERHEAD", 3)
volume = os.getenv("VOLUME",10) # Gbytes
reduce_factor = os.getenv("REDUCE_FACTOR",5)
map_factor = os.getenv("MAP_FACTOR",5)
random_country = os.getenv("RANDOM_COUNTRY","false")

bandwidth = os.getenv("BANDWIDTH",1e10) # 10Ghz
transmit_power = os.getenv("TRANSMIT_POWER",5) # 5W
transmit_gain =  os.getenv("TRANSMIT_GAIN",62.5) # dBi 
receive_gain =  os.getenv("RECEIVE_GAIN",62.5) # dBi 
boltzmann = os.getenv("BOLTZMANN",1.38e-23) # J/K
noise_temp = os.getenv("NOISE_TEMP",300) # K
wavelength = os.getenv("WAVELENGTH",1.55e-6) # 8m

city = os.getenv("CITY","London")
country = os.getenv("COUNTRY","US")




config = SimpleNamespace(
        MAX_ORB=int(max_orb),
        MAX_SAT=int(max_sat),
        INCLINATION=int(inclination),
        ALTITUDE=int(altitude),
        MIN_COMMUNICATIONS_ALTITUDE=int(min_communications_altitude),
        EARTH_RADIUS=int(earth_radius),
        PROCESSING_TIME=float(processing_time),
        REDUCE_PROCESSING_TIME=float(reduce_processing_time),
        HOP_OVERHEAD=float(hop_overhead),
        BANDWIDTH=float(bandwidth),
        TRANSMIT_POWER=float(transmit_power),
        TRANSMIT_GAIN=float(transmit_gain),
        RECEIVE_GAIN=float(receive_gain),
        BOLTZMANN=float(boltzmann),
        NOISE_TEMP=float(noise_temp),
        WAVELENGTH=float(wavelength),
        VOLUME=float(volume),
        REDUCE_FACTOR=float(reduce_factor),
        MAP_FACTOR=float(map_factor),
        COUNTRY=country,
        CITY=city,
  )
