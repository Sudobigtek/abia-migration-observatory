#!/bin/bash
# Auto-generated fix script by Codebase Doctor

echo 'Running isort...'
isort . --profile black 2>/dev/null || true
echo 'Running black...'
black . 2>/dev/null || true
echo 'Running autopep8...'
autopep8 --in-place --recursive . 2>/dev/null || true
echo 'Running Django migrations if needed...'
python manage.py makemigrations 2>/dev/null || true
python manage.py migrate 2>/dev/null || true
echo 'Running tests to verify fixes...'
pytest 2>/dev/null || true
echo 'Fix script completed.'