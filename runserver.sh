#!/bin/bash
dir=$(dirname "${BASH_SOURCE[0]}")
"$dir"/venv/bin/python3 "$dir"/manage.py runserver
