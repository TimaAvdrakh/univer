from datetime import date


def get_current_study_year():
    """Возвращает текущий учебный год"""

    current_year = date.today().year
    current_month = date.today().month
    current_day = date.today().day

    if current_month >= 9 and current_day >= 1:
        current_study_year = {
            'start': current_year,
            'end': current_year + 1
        }
    else:
        current_study_year = {
            'start': current_year - 1,
            'end': current_year
        }
    return current_study_year


