from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ConfirmationCodeGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + user.email + str(timestamp)


confirmation_code_generator = ConfirmationCodeGenerator()
