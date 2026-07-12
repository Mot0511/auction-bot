async def get_str_time(seconds: int):
    print(seconds)
    hours = 0
    minutes = 0

    if seconds >= 3600:
        hours = seconds // 3600
        seconds = seconds % 3600
    if seconds >= 60:
        minutes = seconds // 60
        seconds = seconds % 60
    
    s = ''
    if hours:
        s += f'{hours} ч. '
    if minutes:
        s += f'{minutes} мин. '
    if seconds:
        s += f'{seconds} сек.'

    print(hours, minutes, seconds)
    print(s)
    return s
