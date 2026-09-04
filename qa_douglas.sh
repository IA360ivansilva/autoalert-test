#!/usr/bin/env bash
PAGE="https://ia360ivansilva.github.io/autoalert-test/top200/douglas-8717.html"
AUDIO="https://ia360ivansilva.github.io/autoalert-test/audios/douglas-8717-natural-female.mp3"
echo "[PAGE]     $(curl -sS -o /dev/null -w '%{http_code}' -L "$PAGE")"
echo "[AUDIO]    $(curl -sS -o /dev/null -w '%{http_code} %{content_type}' -L "$AUDIO")"
H=$(curl -sS -L "$PAGE")
echo "[PHONE]    $(echo "$H" | grep -q 'tel:19548600537' && echo PASS || echo FAIL)"
echo "[PHONECOL] $(echo "$H" | grep -q 'var(--phone)' && echo PASS || echo FAIL)"
echo "[AUDIOSRC] $(echo "$H" | grep -qi 'douglas-8717-natural-female.mp3' && echo PASS || echo FAIL)"
echo "[PLAYER]   $(echo "$H" | grep -qi 'Play Douglas' && echo PASS || echo FAIL)"
echo "[MODELS]   $(echo "$H" | grep -qi '2027 Kia Telluride\|2026 Kia Sorento\|2026 Kia Sportage' && echo PASS || echo FAIL)"
echo "[CTA]      $(echo "$H" | grep -q 'Book My Appraisal' && echo PASS || echo FAIL)"
echo "[DUR]      $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /Users/clawbotlocal/autoalert-pages/audios/douglas-8717-natural-female.mp3)s"
echo "[ROBOT]    $(echo "$H" | grep -qi 'douglas-8717.mp3' && echo 'WARN old robotic linked' || echo 'OK no robotic link')"
