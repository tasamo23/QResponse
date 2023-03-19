
# Below functions are adapted from https://en.m.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders#RS_encoding

def rs_encode_msg(msg_in: list[int], numEccSyms: int):
    # Main encoding function (polynomial division in galois field)

    # Check that the message is not too long
    if (len(msg_in) + numEccSyms) > 255:
        raise ValueError("Message is too long (%i when max is 255)" % (len(msg_in)+numEccSyms))
    gen = rs_generator_poly(numEccSyms)

    # Initialize msg_out with the values inside msg_in and pad with len(gen)-1 bytes (which is the number of RS symbols).
    msg_out = [0] * (len(msg_in) + len(gen)-1)

    # Initializing the Synthetic Division with the dividend (= input message polynomial)
    msg_out[:len(msg_in)] = msg_in

    # Synthetic division main loop
    for i in range(len(msg_in)):
        # Declare coefficient
        coef = msg_out[i]

        # Check for log(0) as that would be undefined
        if coef != 0:
            # Skip first coefficient
            for j in range(1, len(gen)):
                msg_out[i+j] ^= gf_mul(gen[j], coef)

    # The message composed of the input message + the RS code as array of bytes
    msg_out[:len(msg_in)] = msg_in

    return msg_out


def gf_mul(x: int, y: int):
    # Check for multiplication by 0
    if x == 0 or y == 0:
        return 0
    return gf_exp[gf_log[x] + gf_log[y]]


def rs_generator_poly(numEccSyms: int):
    # Generate a generator polynomial (necessary to encode a message into Reed-Solomon)
    gen = [1]
    for i in range(0, numEccSyms):
        gen = gf_poly_mul(gen, [1, gf_pow(2, i)])
    return gen


def gf_pow(x: int, power: int):
    return gf_exp[(gf_log[x] * power) % 255]


def gf_inverse(x: int):
    return gf_exp[255 - gf_log[x]]


# Initialize array for the lookup tables, which speed up computation
gf_exp = [0] * 512
gf_log = [0] * 256


def init_lookup_tables(prim=0x11d):
    # Precompute the logarithm and anti-log tables for faster computation later, using the provided primitive polynomial (prim)
    global gf_exp, gf_log
    gf_exp = [0] * 512  # anti-log (exponential) table
    gf_log = [0] * 256  # log table

    # For each possible value in the galois field 2^8, we will pre-compute the logarithm and anti-logarithm (exponential) of this value
    x = 1
    for i in range(0, 255):
        gf_exp[i] = x  # compute anti-log for this value and store it in a table
        gf_log[x] = i  # compute log at the same time
        x = gf_mult_noLUT(x, 2, prim)

    for i in range(255, 512):
        gf_exp[i] = gf_exp[i - 255]
    return [gf_log, gf_exp]


def gf_mult_noLUT(x: int, y: int, prim=0, field_charac_full=256, carryless=True):
    result = 0
    while y:  # while y is above 0
        if y & 1:
            # y is odd, then add the corresponding x to r (the sum of all x's corresponding to odd y's will give the final product). Note that since we're in GF(2), the addition is in fact an XOR (very important because in GF(2) the multiplication and additions are carry-less, thus it changes the result!).
            result = result ^ x if carryless else result + x
        y = y >> 1
        x = x << 1
        if prim > 0 and x & field_charac_full:
            x = x ^ prim

    return result


# Generate lookup tables
init_lookup_tables()


def gf_poly_mul(p: list[int], q: list[int]):
    '''Multiply two polynomials, inside Galois Field'''

    # Pre-allocate the result array
    result = [0] * (len(p)+len(q)-1)

    # Compute the polynomial multiplication (just like the outer product of two vectors,
    # we multiply each coefficients of p with all coefficients of q)
    for j in range(0, len(q)):
        for i in range(0, len(p)):
            result[i+j] ^= gf_mul(p[i], q[j])
    return result


class ReedSolomonError(Exception):
    pass


# A table listing the amount of codewords a certain code version requires
# Calculated with the table "RS block size" https://en.m.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders/Additional_information#RS_block_size
EC_CODEWORDS_TABLE = (
    # L, M, Q, H (These are the error correction levels)
    (7, 10, 13, 17),  # Version 1
    (10, 16, 22, 28),  # Version 2
    (15, 26, 36, 44),  # Version 3
    (20, 36, 52, 64),  # Version 4
    (26, 48, 72, 88),  # Version 5
    (36, 64, 96, 112),  # Version 6
    (40, 72, 108, 130),  # Version 7
    (48, 88, 132, 156),  # Version 8
    (60, 110, 160, 192),  # Version 9
    (72, 130, 192, 224),  # Version 10
    (80, 150, 224, 264),  # Version 11
    (96, 176, 260, 308),  # Version 12
    (104, 198, 288, 352),  # Version 13
    (120, 216, 320, 384),  # Version 14
    (132, 240, 360, 432),  # Version 15
    (144, 280, 408, 480),  # Version 16
    (168, 308, 448, 532),  # Version 17
    (180, 338, 504, 588),  # Version 18
    (196, 364, 546, 650),  # Version 19
    (224, 416, 600, 700),  # Version 20
    (224, 442, 644, 750),  # Version 21
    (252, 476, 690, 816),  # Version 22
    (270, 504, 750, 900),  # Version 23
    (300, 560, 810, 960),  # Version 24
    (312, 588, 870, 1050),  # Version 25
    (336, 644, 952, 1110),  # Version 26
    (360, 700, 1020, 1200),  # Version 27
    (390, 728, 1050, 1260),  # Version 28
    (420, 784, 1140, 1350),  # Version 29
    (450, 812, 1200, 1440),  # Version 30
    (480, 868, 1290, 1530),  # Version 31
    (510, 924, 1350, 1620),  # Version 32
    (540, 980, 1440, 1710),  # Version 33
    (570, 1036, 1530, 1800),  # Version 34
    (570, 1064, 1590, 1890),  # Version 35
    (600, 1120, 1680, 1980),  # Version 36
    (630, 1204, 1770, 2100),  # Version 37
    (660, 1260, 1860, 2220),  # Version 38
    (720, 1316, 1950, 2310),  # Version 39
    (750, 1372, 2040, 2430),  # Version 40
)
