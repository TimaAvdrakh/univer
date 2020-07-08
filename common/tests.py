from django.test import TestCase
from ddf import G
from .models import EmailTemplate, InstitutionConfig


class EmailTemplateTestCase(TestCase):
    def setUp(self) -> None:
        config = G(InstitutionConfig)
        self.template = EmailTemplate.objects.create(
            config=config,
            is_dynamic=True,
            subject='Подтверждение регистрации',
            type='REG_VERIFIED',
            template='Ваш логин: {{ user }}\nВаш пароль: {{ password }}\nДля подтверждения регистрации необходимо пройти по ссылке\n{{ link }}\n\nВНИМАНИЕ!!!\nРегистрация должна быть подтверждена в течении 1 дня.\nПо истечении этого срока Ваши данные будут удалены и потребуется повторная регистрация.',
        )
        self.data = {
            'user': 'johndoe',
            'password': 'guacamole nibba painis',
            'link': 'https://test.com/qw41ch2/1441dxv/'
        }

    def test_variables_not_null(self):
        """В этом шаблоне должны быть переменные"""
        variables = self.template.get_variables()
        self.assertIsNotNone(variables, 'Variables are none')

    def test_gets_all_variables(self):
        """Указанные переменные в шаблоне должны быть контейнере"""
        variables = self.template.get_variables()
        self.assertIn('user', variables, 'user not in variables')
        self.assertIn('password', variables, 'password not in variables')
        self.assertIn('link', variables, 'link not in variables')
        self.assertEqual(3, len(variables), f'Length of variables not equal {len(variables)}')

    def test_template_building(self):
        """Переменные и их значения посылаются как словари и значения ключей должны подставляться на место ключей"""
        actual_result = self.template.build_template(**self.data)
        expected_result = 'Ваш логин: johndoe\nВаш пароль: guacamole nibba painis\nДля подтверждения регистрации необходимо пройти по ссылке\nhttps://test.com/qw41ch2/1441dxv/\n\nВНИМАНИЕ!!!\nРегистрация должна быть подтверждена в течении 1 дня.\nПо истечении этого срока Ваши данные будут удалены и потребуется повторная регистрация.'
        self.assertEqual(actual_result, expected_result, 'Build is a failure')

    def test_sending(self):
        """Отрендеренные шаблоны должны отправляться получателям"""
        result = EmailTemplate.send_template(self.template.type, 'test@gmail.com', **self.data)
        self.assertEqual(result, 1, 'Something went wrong')
