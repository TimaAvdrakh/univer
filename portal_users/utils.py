# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
# django.setup()

from datetime import date
# from organizations.models import StudyYearCourse, StudyPeriod


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


def get_course(study_period, study_year):
    """Расчитать курс. Принимает объект период обучения и учебный год"""
    study_year_tuple = (study_year.start, study_year.end)

    start = study_period.start
    end = study_period.end

    study_years_list = []

    for i in range(start, end):
        study_year_item = (i, i + 1)
        study_years_list.append(study_year_item)

    if study_year_tuple in study_years_list:
        course = study_years_list.index(study_year_tuple) + 1
    else:
        course = None

    return course


def divide_to_study_years(study_period):
    start = study_period.start
    end = study_period.end

    study_years = []

    for i in range(start, end):
        study_year = (i, i + 1)
        study_years.append(study_year)

    return study_years
