from ddf import G
from rest_framework.test import APITestCase
from .models import *


class NewsTestCase(APITestCase):
    def setUp(self):
        self.news: News = News.objects.create(title='title', content='content', author=G(User))
        self.roles = Role.get_role_types()
        [G(Group) for _ in range(5)]
        [G(Profile) for _ in range(5)]
        [G(Faculty) for _ in range(5)]
        [G(Cathedra) for _ in range(5)]
        [G(PreparationLevel) for _ in range(5)]
        [G(EducationProgram) for _ in range(5)]
        self.addressees = Profile.objects.all()
        self.courses = [1, 2, 3, 4]
        self.faculties = Faculty.objects.all()
        self.cathedras = Cathedra.objects.all()
        self.education_programs = EducationProgram.objects.all()
        self.prep_levels = PreparationLevel.objects.all()
        self.groups = Group.objects.all()

    def test_set_news_for_roles(self):
        """Протестировать, что новость должна быть указана для типов ролей"""
        self.news.set_for_roles(self.roles)
        self.assertListEqual(
            sorted(self.news.roles),
            sorted(self.roles),
            f"Roles were not set. Expected {self.roles}, got: {self.news.roles}"
        )
        self.assertCountEqual(
            self.news.roles,
            self.roles,
            f"Count does not match. Expected: {len(self.roles)}, got: {len(self.news.roles)}"
        )

    def test_set_news_for_course(self):
        """Протестировать, что новость должна быть указана для курсов"""
        self.news.set_news_for_courses(self.courses)
        self.assertEqual(
            sorted(self.news.courses),
            sorted(self.courses),
            f"Course was not set. Expected: {self.courses}, got: {self.news.courses}"
        )
        self.assertCountEqual(
            self.news.courses,
            self.courses,
            f"Count does not match. Expected: {len(self.courses)}, got: {len(self.news.courses)}"
        )

    def test_set_news_for_addressees(self):
        """Протестировать, что новость должна быть указана для определенных людей"""
        self.news.set_news_for_addressees(self.addressees)
        self.assertListEqual(
            list(self.news.addressees.order_by('created')),
            list(self.addressees.order_by('created')),
            f"Profiles were not set. Expected: {self.news.addressees}, got: {self.addressees}"
        )
        self.assertCountEqual(
            self.news.addressees,
            self.addressees,
            f"Count does not match. Expected: {len(self.addressees)}, got: {len(self.news.addressees)}"
        )

    def test_set_news_for_prep_level(self):
        """Протестировать, что новость должна быть указана для уровней образования"""
        self.news.set_news_for_prep_levels(self.prep_levels)
        self.assertListEqual(
            list(self.news.prep_levels.order_by('created')),
            list(self.prep_levels.order_by('created')),
            f"Preparation level was not set. Expected: {self.prep_levels}, got: {self.prep_levels}"
        )
        self.assertCountEqual(
            self.news.prep_levels,
            self.prep_levels,
            f"Count does not match. Expected: {len(self.prep_levels)}, got: {len(self.news.prep_levels)}"
        )

    def test_set_news_for_faculty(self):
        """Протестировать, что новость должна быть указана для факультетов"""
        self.news.set_news_for_faculties(self.faculties)
        self.assertListEqual(
            list(self.news.faculties.order_by('created')),
            list(self.faculties.order_by('created')),
            f"Faculty was not set. Expected: {self.faculties}, got: {self.news.faculties}"
        )
        self.assertCountEqual(
            self.news.faculties,
            self.faculties,
            f"Count does not match. Expected: {len(self.faculties)}, got: {len(self.news.faculties)}"
        )

    def test_set_news_for_cathedra(self):
        """Протестировать, что новость должна быть указана для кафдер"""
        self.news.set_news_for_cathedras(self.cathedras)
        self.assertListEqual(
            list(self.news.cathedras.order_by('created')),
            list(self.cathedras.order_by('created')),
            f"Cathedra was not set. Expected: {self.cathedras}, got: {self.news.cathedras}"
        )
        self.assertCountEqual(
            self.news.cathedras,
            self.cathedras,
            f"Count does not match. Expected: {len(self.cathedras)}, got: {len(self.news.cathedras)}"
        )

    def test_set_news_for_education_program(self):
        """Протестировать, что новость должна быть указана для образовательных программ"""
        self.news.set_news_for_education_programs(self.education_programs)
        self.assertListEqual(
            list(self.news.education_programs.order_by('created')),
            list(self.education_programs.order_by('created')),
            f"Education program was not set. Expected: {self.news.education_programs}, got: {self.education_programs}"
        )
        self.assertCountEqual(
            self.news.education_programs,
            self.education_programs,
            f"Count does not match. Expected: {len(self.education_programs)}, got: {len(self.news.education_programs)}"
        )

    def test_set_news_for_group(self):
        """Протестировать, что новость должна быть указана для групп"""
        self.news.set_news_for_groups(self.groups)
        self.assertListEqual(
            list(self.news.groups.order_by('created')),
            list(self.groups.order_by('created')),
            f"Group was not set. Expected: {self.news.groups}, got: {self.groups}"
        )
        self.assertCountEqual(
            self.news.groups,
            self.groups,
            f"Count does not match. Expected: {len(self.groups)}, got: {len(self.news.groups)}"
        )

    # def test_create(self):
    #     pass
    #
    # def test_update(self):
    #     pass
    #
    # def test_filter(self):
    #     pass
