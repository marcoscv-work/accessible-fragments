#!/usr/bin/env bash
#
# Boots an official Liferay DXP Docker image, imports the collection, renders
# every fragment on a page and checks the markup (scripts/compat-smoke.py).
# One line per version is appended to marketplace/compatibility.log and the
# full output lands in marketplace/compat-<tag>.txt.
#
#   scripts/compat-test.sh 2026.q3.6 [port] [keep]
#
set -uo pipefail

TAG="${1:?image tag, e.g. 2026.q3.6}"
PORT="${2:-8081}"
KEEP="${3:-}"
NAME="accessible-fragments-${TAG//./-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${ROOT}/marketplace/compatibility.log"
OUT="${ROOT}/marketplace/compat-${TAG}.txt"

cd "${ROOT}"
./build.sh >/dev/null

docker rm -f "${NAME}" >/dev/null 2>&1
docker run -d --name "${NAME}" -p "${PORT}:8080" -m 6g \
	-e LIFERAY_JVM_OPTS="-Xms2g -Xmx4g" \
	-e LIFERAY_SETUP_PERIOD_WIZARD_PERIOD_ENABLED=false \
	-e LIFERAY_TERMS_PERIOD_OF_PERIOD_USE_PERIOD_REQUIRED=false \
	-e LIFERAY_USERS_PERIOD_REMINDER_PERIOD_QUERIES_PERIOD_ENABLED=false \
	-e LIFERAY_PASSWORDS_PERIOD_DEFAULT_PERIOD_POLICY_PERIOD_CHANGE_PERIOD_REQUIRED=false \
	"liferay/dxp:${TAG}" >/dev/null || { echo "docker run failed"; exit 1; }

echo "[$TAG] waiting for the portal on :${PORT}"
code=0
for i in $(seq 1 120); do
	code=$(curl -sL -o /dev/null -w '%{http_code}' "http://localhost:${PORT}/web/guest")
	[ "${code}" = "200" ] && break
	sleep 10
done
if [ "${code}" != "200" ]; then
	echo "[$TAG] portal did not start" | tee "${OUT}"
	docker logs --tail 80 "${NAME}" >> "${OUT}" 2>&1
	echo "${TAG} $(date +%F) FAIL portal did not start" >> "${LOG}"
	[ -z "${KEEP}" ] && docker rm -f "${NAME}" >/dev/null
	exit 1
fi
sleep 20

echo "[$TAG] running the smoke test (import + markup through the site-pages API)"
LIFERAY_URL="http://127.0.0.1:${PORT}" LIFERAY_AUTH="test@liferay.com:test" python3 scripts/compat-smoke.py > "${OUT}" 2>&1
status=$?
cat "${OUT}"

# Releases whose site-pages API cannot create a page with fragments (2026.Q2
# and older) are rendered through the real page editor instead.
if [ ${status} -ne 0 ] && grep -q '^PASS import 9 fragments' "${OUT}" && grep -q '^FAIL create test page' "${OUT}"; then
	echo "[$TAG] the site-pages API cannot create the page here; rendering through the page editor"
	NODE_PATH="${NODE_PATH:-$HOME/projects/liferay-portal/modules/node_modules}" LIFERAY_URL="http://127.0.0.1:${PORT}" LIFERAY_AUTH="test@liferay.com:Compat-test-2026!" node scripts/compat-editor.mjs > "${ROOT}/marketplace/compat-editor-${TAG}.txt" 2>&1
	status=$?
	cat "${ROOT}/marketplace/compat-editor-${TAG}.txt"
fi
{
	echo "---- server errors mentioning fragments"
	docker logs "${NAME}" 2>&1 | grep -iE "ERROR|Exception" | grep -iE "fragment|freemarker" | tail -20
} >> "${OUT}"
if [ ${status} -eq 0 ]; then
	echo "${TAG} $(date +%F) PASS $(cat "${OUT}" "${ROOT}/marketplace/compat-editor-${TAG}.txt" 2>/dev/null | grep -c '^PASS') checks" >> "${LOG}"
else
	echo "${TAG} $(date +%F) FAIL $(grep '^FAIL' "${OUT}" | cut -c6- | paste -sd';' -)" >> "${LOG}"
fi
[ -z "${KEEP}" ] && docker rm -f "${NAME}" >/dev/null
exit ${status}
