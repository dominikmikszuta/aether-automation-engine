#!/bin/bash
set -e
cd "$HOME/aether"
echo "Token (scope: repo): https://github.com/settings/tokens"
read TOKEN
LOGIN=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/user | grep '"login"' | cut -d'"' -f4)
[ -z "$LOGIN" ] && { echo "bad token"; exit 1; }
echo "OK: $LOGIN"
BIO="Creator of AETHER-QM - offline-first automation. Systems Architect. C++23/26 - Python - Linux. Patent Holder. Open to Redmond."
curl -s -X PATCH -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" -d "{\"bio\":\"$BIO\"}" https://api.github.com/user > /dev/null
CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $TOKEN" "https://api.github.com/repos/$LOGIN/aether-automation-engine")
if [ "$CODE" = "404" ]; then
  curl -s -X POST -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" -d "{\"name\":\"aether-automation-engine\",\"private\":false}" https://api.github.com/user/repos > /dev/null
  sleep 3
fi
git init -q 2>/dev/null || true
git config user.name "$LOGIN"
git config user.email "$LOGIN@users.noreply.github.com"
git add -A
git commit -q -m "Initial commit: AETHER-QM v26.0.0" 2>/dev/null || true
git remote remove origin 2>/dev/null || true
git remote add origin "https://$TOKEN@github.com/$LOGIN/aether-automation-engine.git"
git branch -M main
git push -u origin main --force
unset TOKEN
echo ""
echo "DONE: https://github.com/$LOGIN/aether-automation-engine"
echo "DELETE TOKEN NOW: https://github.com/settings/tokens"
termux-open "https://github.com/$LOGIN/aether-automation-engine"
