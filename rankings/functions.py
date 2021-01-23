def calculate_points(record, seconds):
    return int(1000 * pow(record / seconds, 3))


def mk_int(s):
    if s is None:
        return 0
    return int('0' + s)


def try_parse_int(s, val=None):
    try:
        return int(s)
    except (ValueError, TypeError):
        return val
