from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

__all__ = ['token_generator']


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )


token_generator = TokenGenerator()
