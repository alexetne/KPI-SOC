#!/usr/bin/env sh
set -eu

APP_ENV=prod docker compose --profile prod up --build
