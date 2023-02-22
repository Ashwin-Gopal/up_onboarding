#!/bin/bash

source .env
python -m celery -A onboarding beat -l info
