#!/bin/bash

source .env
celery -A onboarding flower --port=5555
