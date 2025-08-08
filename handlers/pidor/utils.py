def get_russian_plural(n, singular, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return singular
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return few
    else:
        return many


def format_timedelta_ru(delta):
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    if seconds % 3600 != 0:
        hours += 1  # If there's a remainder, add one hour to round up
    singular, few, many = 'час', 'часа', 'часов'
    plural = get_russian_plural(hours, singular, few, many)
    return f'{hours} {plural}'
