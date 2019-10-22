from portal.curr_settings import load_types2
from . import models
from common.models import CreditCoeff
from django.db.models import Sum
from django.utils import timezone


def calculate_credit(discipline, student, acad_period):
    """Расчитает кредит для дисциплины"""
    coeff = CreditCoeff.objects.filter(start_year__lte=timezone.now().year).latest('start_year').coeff

    student_disciplines = models.StudentDiscipline.objects.filter(
        discipline=discipline,
        student=student,
        acad_period=acad_period,
        is_active=True,
    )

    lecture_hours = student_disciplines.filter(
        load_type__load_type2__number=load_types2['lecture'],
    ).aggregate(hours=Sum('hours'))['hours'] or 0

    lab_hours = student_disciplines.filter(
        load_type__load_type2__number=load_types2['lab'],
    ).aggregate(hours=Sum('hours'))['hours'] or 0

    seminar_hours = student_disciplines.filter(
        load_type__load_type2__number=load_types2['seminar'],
    ).aggregate(hours=Sum('hours'))['hours'] or 0

    study_hours = student_disciplines.filter(
        load_type__load_type2__number=load_types2['study'],
    ).aggregate(hours=Sum('hours'))['hours'] or 0

    credit = (lecture_hours + lab_hours + seminar_hours + study_hours +
              (lecture_hours + lab_hours + seminar_hours + study_hours) * 2) / coeff

    return credit
