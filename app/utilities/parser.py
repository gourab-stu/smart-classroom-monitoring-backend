from datetime import timedelta


def parse_duration(duration_str: str) -> timedelta:
    value = int(duration_str[:-1])
    unit = duration_str[-1]

    if unit == "s":
        return timedelta(seconds=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    else:
        raise ValueError(f"Unsupported time format: {duration_str}")


def parse_file_size(size: str) -> int:
    value = int(size[:-2])
    unit = size[-2:]

    if unit == "KB":
        return value * 1024
    elif unit == "MB":
        return value * 1024 * 1024
    elif unit == "GB":
        return value * 1024 * 1024 * 1024
    else:
        raise ValueError(f"Unsupported file size: {size}")
