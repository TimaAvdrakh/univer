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


def get_current_course(study_period):
    """Расчитать текуший курс. Принимает объект StudyPeriod"""
    current_study_year_dict = get_current_study_year()
    current_study_year = (current_study_year_dict['start'], current_study_year_dict['end'])

    start = study_period.start
    end = study_period.end

    study_years_list = []

    for i in range(start, end):
        study_year = (i, i + 1)
        study_years_list.append(study_year)

    if current_study_year in study_years_list:
        course = study_years_list.index(current_study_year) + 1
    else:
        course = None

    return course
