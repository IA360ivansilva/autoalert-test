#!/usr/bin/env bash
BASE="https://ia360ivansilva.github.io/autoalert-test/top200"
for slug in douglas-8717 chelsea-6310 fabio-0289 marilynn-7428 christopher-8685 heidi-0353 richard-0341 jason-3756 iris-1475 riva-9586 christopher-8212; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" -L "$BASE/$slug.html")
  echo "$slug.html -> $code"
done
