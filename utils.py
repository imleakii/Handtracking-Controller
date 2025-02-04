def interpolate(value, a1, a2, b1, b2):
    """
    maps a value in the range[a1, a2] to [b1, b2]
    """

    # Figure out how 'wide' each range is
    a_span = a2 - a1
    b_span = b2 - b1

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - a1) / float(a_span)

    # Convert the 0-1 range into a value in the right range.
    return b1 + (value_scaled * b_span)