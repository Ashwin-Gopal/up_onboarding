#!/bin/bash

source .env
python -m celery -A onboarding worker -l info -Q orders
