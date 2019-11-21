import calendar
import datetime
from datetime import date


# def get_weeks_in_year(year):
#     weeks = []
#
#     for month in range(1, 13):
#         mondays = [
#             day.split()[0] for day in calendar.month(year, month).split("\n")[2:-1]
#             if not day.startswith("  ")
#         ]
#
#         for monday in mondays:
#             monday_d = datetime.datetime(year, int(month), int(monday))
#             sunday_d = monday_d + datetime.timedelta(days=6)
#
#             last_day_of_month = calendar.monthrange(year, int(month))[-1]
#
#             if sunday_d.month > int(month) and sunday_d.year == year:
#                 week = [datetime.datetime(year, int(month), day)
#                         for day in range(monday_d.day, last_day_of_month + 1)]
#
#                 extra = [datetime.datetime(year, int(sunday_d.month), day)
#                          for day in range(1, sunday_d.day + 1)]
#                 week += extra
#
#             elif sunday_d.year > year:
#                 week = [datetime.datetime(year, int(month), day)
#                         for day in range(monday_d.day, last_day_of_month + 1)]
#
#                 extra = [datetime.datetime(sunday_d.year, int(sunday_d.month), day)
#                          for day in range(1, sunday_d.day + 1)]
#                 week += extra
#
#             else:
#                 week = [datetime.datetime(year, int(month), int(day))
#                         for day in range(monday_d.day, sunday_d.day + 1)]
#
#             weeks.append(week)
#
#             # print(week)
#     return weeks


def get_weeks_of_year(year):
    c = calendar.Calendar()
    weeks = list()
    for i, month in enumerate(c.yeardatescalendar(year, width=1)):
        # print(i + 1)
        for week in month[0]:
            # print(week)
            if not week in weeks:
                weeks.append(week)
    return weeks

