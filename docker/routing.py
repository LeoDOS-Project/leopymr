#! /usr/bin/env python3

from config import config
from utils import log
import math
import traceback

NORTH = (0, -1)
SOUTH = (0, 1)
WEST = (-1, 0)
EAST = (1, 0)
ZERO = (0, 0)


def north_distance(orb, target_orb):
    max_orb = config.MAX_ORB
    if target_orb < orb:
        return orb - target_orb
    if target_orb > orb:
        return orb + max_orb - target_orb
    return 0


def south_distance(orb, target_orb):
    max_orb = config.MAX_ORB
    if target_orb > orb:
        return target_orb - orb
    if target_orb < orb:
        return max_orb - orb + target_orb
    return 0


def west_distance(sat, target_sat):
    max_sat = config.MAX_SAT
    if target_sat < sat:
        return sat - target_sat
    if target_sat > sat:
        return sat + max_sat - target_sat
    return 0


def east_distance(sat, target_sat):
    max_sat = config.MAX_SAT
    if target_sat > sat:
        return target_sat - sat
    if target_sat < sat:
        return max_sat - sat + target_sat
    return 0


def get_vertical_direction(orb, target_orb):
    north = north_distance(orb, target_orb)
    south = south_distance(orb, target_orb)
    if north == south == 0:
        return ZERO
    if north < south:
        return NORTH
    return SOUTH


def get_horizontal_direction(sat, target_sat):
    west = west_distance(sat, target_sat)
    east = east_distance(sat, target_sat)
    if east == west == 0:
        return ZERO
    if west < east:
        return WEST
    return EAST


def get_direction(from_sat, to_sat):
    (sat, orb) = from_sat
    (target_sat, target_orb) = to_sat
    vertical_direction = get_vertical_direction(orb, target_orb)
    horizontal_direction = get_horizontal_direction(sat, target_sat)
    max_sat = config.MAX_SAT
    max_orb = config.MAX_ORB
    log(f"MAX_SAT {max_sat} MAX_ORB {max_orb} VERTICAL {vertical_direction} HORIZONTAL {horizontal_direction} from {from_sat} to {to_sat}", verbosity=6)

    west_distance = orb_distance(add_direction(from_sat, WEST)[0])
    my_distance = orb_distance(from_sat[0])
    east_distance = orb_distance(add_direction(from_sat, EAST)[0])
    log(f"WEST {west_distance} MY {my_distance} EAST {east_distance}", verbosity=6)

    cross_over = west_distance > my_distance and east_distance > my_distance

    if horizontal_direction[0] != 0:
        if cross_over:
            return horizontal_direction
        if horizontal_direction == WEST:
            if my_distance > west_distance:
                return horizontal_direction
        if horizontal_direction == EAST:
            if my_distance > east_distance:
                return horizontal_direction

    if vertical_direction[1] == 0:
        return horizontal_direction

    return vertical_direction


def adjust_overflow(s):
    if s[0] == 0:
        return (config.MAX_SAT, s[1])
    if s[0] > config.MAX_SAT:
        return (1, s[1])
    if s[1] == 0:
        return (s[0], config.MAX_ORB)
    if s[1] > config.MAX_ORB:
        return (s[0], 1)
    return (s[0], s[1])


def valid_sat(sat):
    if sat[0] < 1:
        return False
    if sat[0] > config.MAX_SAT:
        return False
    if sat[1] < 1:
        return False
    if sat[1] > config.MAX_ORB:
        return False
    return True


def sat_distance():
    N = config.MAX_SAT
    rE = config.EARTH_RADIUS * 1000
    h = config.ALTITUDE * 1000
    return (rE + h) * math.sqrt(2 * (1 - math.cos(2 * math.pi / N)))


def orb_distance(sat):
    N = config.MAX_ORB
    M = config.MAX_SAT
    i = config.INCLINATION
    tT = sat / M
    tAngle = 2 * math.pi * tT
    nAngle = 2 * math.pi / N
    rE = config.EARTH_RADIUS * 1000
    h = config.ALTITUDE * 1000
    s1 = (rE + h) * math.sqrt(2 * (1 - math.cos(nAngle)))
    s2 = math.sqrt(math.cos(tAngle)**2 + math.cos(i)**2 * math.sin(tAngle)**2)
    return s1 * s2


def get_distance(direction, distances):
    d = [a * b for a, b in zip(direction, distances)]
    return abs(d[0] + d[1])


def add_direction(sat, direction):
    return adjust_overflow([a + b for a, b in zip(sat, direction)])


def to_str(direction):
    if direction == WEST:
        return "WEST"
    if direction == EAST:
        return "EAST"
    if direction == NORTH:
        return "NORTH"
    if direction == SOUTH:
        return "SOUTH"
    return "ZERO"


def get_dist_hops(from_sat, to_sat):
    import sys
    if not valid_sat(from_sat) or not valid_sat(to_sat):
        log(f"Invalid from to sats {from_sat} {to_sat}", verbosity=0)
        traceback.print_stack()
        sys.exit(1)
    sats_passed = []
    tot_distance = 0
    distances = []
    direction = get_direction(from_sat, to_sat)
    distance = get_distance(
        direction,
        (sat_distance(),
         orb_distance(
            from_sat[0])))
    distances.append(distance)
    tot_distance += distance
    from_sat = add_direction(from_sat, direction)
    if distance != 0:
        sats_passed.append(from_sat)
    i = 1
    log(f"HOP {i} {to_str(direction)} DISTANCE {distance} DIRECTION {direction} NEW SAT {from_sat} TO SAT {to_sat}", verbosity=6)
    while to_sat != from_sat:
        direction = get_direction(from_sat, to_sat)
        distance = get_distance(
            direction, (sat_distance(), orb_distance(from_sat[0])))
        tot_distance += distance
        distances.append(distance)
        from_sat = add_direction(from_sat, direction)
        sats_passed.append(from_sat)
        i += 1
        log(
            f"HOP {i} {
                to_str(direction)} DISTANCE {distance} DIRECTION {direction} NEW SAT {from_sat} TO SAT {to_sat}",
            verbosity=6)

    log(f"Total Distance {tot_distance}m Hops {i}", verbosity=6)
    return (tot_distance, i, distances, sats_passed)


def node_to_sat(node):
    orb_index = math.ceil(node / config.MAX_SAT)
    sat_index = node - (orb_index - 1) * config.MAX_SAT
    return (sat_index, orb_index)


def sat_to_node(sat):
    orb_index = sat[1]
    sat_index = sat[0]
    return (orb_index - 1) * config.MAX_SAT + sat_index


def get_node_dist_hops(node1, node2):
    sat1 = node_to_sat(node1)
    sat2 = node_to_sat(node2)
    return get_dist_hops(sat1, sat2)


if __name__ == "__main__":
    import sys
    from_sat = (int(sys.argv[1]), int(sys.argv[2]))
    to_sat = (int(sys.argv[3]), int(sys.argv[4]))
    print(get_dist_hops(from_sat, to_sat))
