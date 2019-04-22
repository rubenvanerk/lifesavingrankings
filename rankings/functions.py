def calculate_points(record, seconds):
    points = 0
    quotient = seconds / record

    if quotient <= 2:
        r1 = 467 * quotient * quotient
        r2 = 2001 * quotient
        points = round((r1 - r2 + 2534.0) * 100.0) / 100.0
    elif quotient <= 5:
        r1 = 2000.0 / 3.0
        r2 = (400.0 / 3.0) * quotient
        points = r1 - r2
        points = round(100.0 * points) / 100.0

    return points


def mk_int(s):
    if s is None:
        return 0
    return int('0' + s)
