#!/bin/bash
echo "export requirements.txt"
poetry export -o requirements.txt --without-hashes
poetry export -o requirements-dev.txt --dev --without-hashes
echo "autoflake"
autoflake --recursive --in-place  \
        --remove-unused-variables \
        --remove-all-unused-imports  \
        --ignore-init-module-imports \
        respo tests docs
echo "black"
black respo tests docs
echo "isort"
isort respo tests docs
echo "flake8"
flake8 respo tests docs --count --statistics
echo "OK"