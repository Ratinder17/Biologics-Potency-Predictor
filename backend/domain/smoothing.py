# domain/smoothing.py
# smoothing → thermal → degradation → forecasting → Flask
def exponential_smoothing(values, alpha):
    
    if not values:
        return []
    
    if not(0 < alpha <=1):
        return ValueError("alpha must be in (0, 1]")
    
    smoothed = [float(values[0])]

    for v in values[1:]:
        prev = smoothed[-1]
        smoothed.append(alpha * float(v) + (1 - alpha) * prev)

    return smoothed


"""
    Apply simple exponential smoothing to a time series.

    Purpose:
        Reduce short-term noise while preserving trend.

    Assumptions:
        - values are ordered in time
        - sampling interval is approximately constant
        - 0 < alpha <= 1

    Args:
        values (list[float]): raw sensor values
        alpha (float): smoothing factor

    Returns:
        list[float]: smoothed values (same length)
    """