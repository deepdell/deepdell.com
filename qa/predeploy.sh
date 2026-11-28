#!/usr/bin/env bash
# DEEPDELL pre-deploy gate. Nothing goes to main until this passes.
#   bash qa/predeploy.sh          # full: security + all-device responsive/UI/brand check
#   bash qa/predeploy.sh --quick  # security + 6 representative devices (while iterating)
set -u
cd "$(dirname "$0")/.."
FLAG="${1:-}"
fail=0
echo "== 1/3 Rebuild generated pages =="
python3 tools/gen_pages.py >/dev/null && python3 tools/gen_tools.py >/dev/null && python3 tools/gen_blog.py | tail -1 && python3 tools/i18n_extract.py >/dev/null && python3 tools/i18n_build.py | tail -1
if [ -n "$(git status --porcelain)" ]; then echo "NOTE: rebuild changed files. Review and commit them before deploying."; fi
echo; echo "== 2/3 Security and hack-proofing check =="
python3 qa/security.py || fail=1
echo; echo "== 3/3 Responsive, UI/UX and brand check on all device profiles =="
NODE_PATH="${NODE_PATH:-$(npm root -g)}" node qa/responsive.js $FLAG || fail=1
echo
if [ $fail -eq 0 ]; then echo "PRE-DEPLOY GATE: PASSED"; else echo "PRE-DEPLOY GATE: FAILED. Fix every FAIL above, then run again."; fi
exit $fail
