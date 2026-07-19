import pytest
from django.core.exceptions import ValidationError
from abia.accounts.models import User


@pytest.mark.django_db
def test_user_role_validation():
    user = User(username="role_test", email="t@t.com", role="invalid_role")
    with pytest.raises(ValidationError) as exc:
        user.full_clean()
    assert "role" in exc.value.message_dict
