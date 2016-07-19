"""
Util functions
"""
import datetime

PRECISION_PERSON = 5

PRECISION_TABLE = {
    0: [111.32 * 1000, 102.47 * 1000, 78.71 * 1000, 43.496 * 1000],
    1: [11.132 * 1000, 10.247 * 1000, 7.871 * 1000, 4.3496 * 1000],
    2: [1.1132 * 1000, 1.0247 * 1000, 787.1, 434.96 * 1000],
    3: [111.32, 102.47, 78.71, 43.496 * 1000],
    4: [11.132, 10.247, 7.871, 4.3496 * 1000],
    5: [1.1132, 1.0247, 787.1 / 1000, 434.96 / 1000],
    6: [111.32 / 1000, 102.47 / 1000, 78.71 / 1000, 43.496 / 1000],
    7: [11.132 / 1000, 10.247 / 1000, 7.871 / 1000, 4.3496 / 1000],
    8: [1.1132 / 1000, 1.0247 / 1000, 787.1 / (1000 ** 2), 434.96 / (1000 ** 2)]
    }

def estimate_meters_to_deg(meters, precision=PRECISION_PERSON):
    """ Meters to degrees estimation

    See https://en.wikipedia.org/wiki/Decimal_degrees

    Args:
        meters (float)
        precision (float)
    Returns:
        float: meters in degrees approximation
    """
    line = PRECISION_TABLE[precision]
    dec = 1/float(10 ** precision)
    return meters / line[3] * dec

def isostr_to_datetime(dt_str):
    """ Converts iso formated text string into a datetime object

    Args:
        dt_str (str): ISO formated text string
    Returns:
        :obj:`datetime.datetime`
    """
    delta_t, _, us_m = dt_str.partition(".")
    delta_t = datetime.datetime.strptime(delta_t, "%Y-%m-%dT%H:%M:%S")
    us_m = int(us_m.rstrip("Z"), 10)
    return delta_t + datetime.timedelta(microseconds=us_m)
