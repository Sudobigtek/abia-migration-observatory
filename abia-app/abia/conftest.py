import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from abia.accounts.models import User
from abia.migrants.models import Migrant, LGA
from abia.cases.models import Case
from abia.referrals.models import Referral


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='testadmin',
        email='test@example.com',
        password='testpass123',
        role='super_admin'
    )


@pytest.fixture
def auth_client(api_client, admin_user):
    token, _ = Token.objects.get_or_create(user=admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def test_lga(db):
    return LGA.objects.create(name='Test LGA', code='TST')


@pytest.fixture
def test_migrant(db, test_lga):
    return Migrant.objects.create(
        full_name='Test Migrant',
        gender='male',
        phone='+2348012345678',
        current_lga=test_lga,
        status='active'
    )


@pytest.fixture
def test_case(db, test_migrant, admin_user):
    return Case.objects.create(
        title='Test Case',
        case_type='medical',
        priority='medium',
        status='open',
        migrant=test_migrant,
        assigned_to=admin_user,
        description='Test case description'
    )


@pytest.fixture
def test_referral(db, test_migrant, test_case, admin_user):
    return Referral.objects.create(
        migrant=test_migrant,
        case=test_case,
        referred_by=admin_user,
        referral_type='medical',
        priority='medium',
        status='pending',
        notes='Test referral'
    )
