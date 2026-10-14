#!/usr/bin/env python3
"""Imports dist/accessible-fragments.zip into a running Liferay, creates a
content page with every fragment, and checks the rendered markup.

    LIFERAY_URL=http://localhost:8081 LIFERAY_AUTH=test@liferay.com:test \
    python3 scripts/compat-smoke.py

Prints one PASS/FAIL line per check and exits non-zero on any FAIL.
Needs only the standard library.
"""
import http.cookiejar
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import uuid

BASE = os.environ.get('LIFERAY_URL', 'http://localhost:8080').rstrip('/')
LOGIN, PASSWORD = os.environ.get('LIFERAY_AUTH', 'test@liferay.com:test').split(':', 1)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP = os.path.join(ROOT, 'dist', 'accessible-fragments.zip')
SRC = os.path.join(ROOT, 'src', 'accessible-components')
PAGE_ERC = 'accessible-fragments-smoke'

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
results = []


def report(ok, name, detail=''):
    results.append(ok)
    print(('PASS ' if ok else 'FAIL ') + name + (': ' + detail if detail else ''))


auth_token = ''


def request(path, data=None, headers=None, method=None):
    url = path if path.startswith('http') else BASE + path
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    if auth_token:
        req.add_header('x-csrf-token', auth_token)
    global last_url
    try:
        with opener.open(req, timeout=120) as r:
            last_url = r.geturl()
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        last_url = e.geturl()
        return e.code, e.read().decode('utf-8', 'replace')


last_url = ''


def multipart(fields, file_field, file_path):
    boundary = uuid.uuid4().hex
    body = b''
    for k, v in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    with open(file_path, 'rb') as f:
        content = f.read()
    body += f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{os.path.basename(file_path)}"\r\nContent-Type: application/zip\r\n\r\n'.encode() + content + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()
    return body, f'multipart/form-data; boundary={boundary}'


# 1. Session login and auth token. Quarterly releases require the CSRF token
#    (p_auth) on the login action itself, so read it from the anonymous page.
def read_token(html):
    m = re.search(r"authToken\s*[:=]\s*'([^']+)'", html)
    return m.group(1) if m else ''

status, home = request('/web/guest')
auth_token = read_token(home)
status, _ = request('/c/portal/login?p_auth=' + auth_token, data=urllib.parse.urlencode({'login': LOGIN, 'password': PASSWORD, 'p_auth': auth_token}).encode())
status, home = request('/web/guest')
if not re.search(r'isSignedIn: \(\) => true|sign-out', home) and 'update_password' not in last_url:
    # A rerun against the same container: the first run already changed the password.
    status, home = request('/web/guest')
    auth_token = read_token(home)
    request('/c/portal/login?p_auth=' + auth_token, data=urllib.parse.urlencode({'login': LOGIN, 'password': 'Compat-test-2026!', 'p_auth': auth_token}).encode())
    status, home = request('/web/guest')
if 'update_password' in last_url:
    # Fresh Docker images force a password change on the first sign in. The
    # first response is an auto-submit form; posting it returns the real form.
    def inputs(html):
        return {n: v for n, v in re.findall(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html)}
    status, form = request('/c/portal/update_password', data=urllib.parse.urlencode(inputs(home)).encode())
    fields = inputs(form)
    fields.update({'password1': 'Compat-test-2026!', 'password2': 'Compat-test-2026!'})
    request('/c/portal/update_password', data=urllib.parse.urlencode(fields).encode())
    status, home = request('/web/guest')
auth_token = read_token(home)
signed_in = 'isSignedIn: () => true' in home or 'isSignedIn:function(){return true' in home or 'sign-out' in home
if not signed_in:
    report(False, 'session login', f'login POST returned {status}, still anonymous')
    sys.exit(1)
status, out = request('/api/jsonws/group/get-user-sites-groups?p_auth=' + auth_token)
try:
    group_id = next(str(g['groupId']) for g in json.loads(out) if g.get('friendlyURL') == '/guest')
except Exception:
    group_id = ''
report(bool(auth_token) and bool(group_id), 'session login', f'authToken {"found" if auth_token else "missing"}, Guest groupId {group_id or "missing"}')
if not auth_token or not group_id:
    sys.exit(1)

# 2. Import the collection (overwrite keeps re-runs idempotent).
body, ctype = multipart({'importType': 'overwrite', '_com_liferay_fragment_web_portlet_FragmentPortlet_importType': 'overwrite'}, 'file', ZIP)
status, out = request(
    '/group/guest/~/control_panel/manage?p_p_id=com_liferay_fragment_web_portlet_FragmentPortlet&p_p_lifecycle=2&p_p_resource_id=%2Ffragment%2Fimport&p_auth=' + auth_token,
    data=body, headers={'Content-Type': ctype})
try:
    imported = json.loads(out)['importResults']
except Exception:
    imported = {}
names = sorted(e['name'] for e in imported.get('success', []))
bad = {k: v for k, v in imported.items() if k != 'success' and v}
ok = status == 200 and len(names) == 9 and not bad
report(ok, 'import 9 fragments', f'{len(names)} ok {names}; other: {bad or "none"}' if imported else f'HTTP {status} {out[:300]!r}')
if not ok:
    sys.exit(1)

# The imported fragments, referenced by external reference code.
status, out = request(f'/api/jsonws/fragment.fragmentcollection/get-fragment-collections/group-id/{group_id}?p_auth={auth_token}')
collection = next((c for c in json.loads(out) if c['fragmentCollectionKey'] == 'accessible-components'), None)
status, out = request(f"/api/jsonws/fragment.fragmententry/get-fragment-entries/fragment-collection-id/{collection['fragmentCollectionId']}?p_auth={auth_token}")
ERC = {e['fragmentEntryKey']: e['externalReferenceCode'] for e in json.loads(out)}
report(len(ERC) == 9, 'imported fragments resolvable', ', '.join(sorted(ERC)))

# 3. Create a content page with every fragment (fragment sources inlined so
#    the page renders exactly the templates under test).
request('/o/com-liferay-feature-flag-web/set-enabled?p_auth=' + auth_token, data=b'key=LPD-35443&enabled=true')
status, _ = request('/o/headless-admin-site/v1.0/sites/L_GUEST/site-pages/' + PAGE_ERC, method='DELETE')

def text(v): return {'type': 'Text', 'value_i18n': {'en-US': v}}
def select(v): return {'type': 'Select', 'value': v}
def check(v): return {'type': 'Checkbox', 'value': v}

FRAGMENTS = [
    ('banner-slider', 'banner-slider', {'numberOfSlides': text('3'), 'ariaLabel': text('Highlights')}),
    ('accordion', 'accordion', {}),
    ('dropdown', 'dropdown', {}),
    ('dropdown-hover', 'dropdown', {'displayOnHover': check(True)}),
    ('button', 'button', {'accessibleDescription': text('about our pricing plans')}),
    ('card', 'card', {'headingLevel': select('h3')}),
    ('video', 'video', {'url': text('/documents/sample.mp4'), 'videoTitle': text('Product tour'), 'captionsUrl': text('/documents/sample.vtt')}),
    ('external-video', 'external-video', {'videoTitle': text('External tour')}),
    ('cookie-banner-simple', 'cookie-banner-simple', {}),
    ('social', 'social', {}),
]

def element(erc, key, cfg, i, suffix):
    read = lambda f: open(os.path.join(SRC, key, f)).read()
    return {
        'externalReferenceCode': f'{erc}-{suffix}', 'position': i,
        'pageElementDefinition': {'type': 'BasicFragment', 'fragmentInstance': {
            'fragmentInstanceExternalReferenceCode': f'{erc}-{suffix}-inst',
            'fragmentReference': {'fragmentReferenceType': 'FragmentItemExternalReference', 'externalReferenceCode': ERC[key]},
            'fragmentConfigurationFieldValues': cfg, 'fragmentEditableElements': [],
            'html': read('index.html'), 'css': read('index.css'), 'js': read('index.js'), 'configuration': read('configuration.json'),
        }},
    }

def spec(erc, status, suffix, draft=None):
    s = {'externalReferenceCode': erc, 'status': status, 'type': 'ContentPageSpecification', 'pageExperiences': [{
        'externalReferenceCode': erc + '-default', 'key': 'DEFAULT', 'name_i18n': {'en-US': 'Default'},
        'pageElements': [{'externalReferenceCode': 'section-' + suffix, 'position': 0,
                          'pageElementDefinition': {'type': 'Container', 'indexed': False, 'layout': {'widthType': 'Fixed'}},
                          'pageElements': [element(e, k, c, i, suffix) for i, (e, k, c) in enumerate(FRAGMENTS)]}]}]}
    if draft:
        s['draftContentPageSpecificationExternalReferenceCode'] = draft
    return s

page = {'externalReferenceCode': PAGE_ERC, 'friendlyUrlPath_i18n': {'en-US': '/' + PAGE_ERC},
        'name_i18n': {'en-US': 'Accessible Fragments smoke'}, 'type': 'ContentPage',
        'pageSpecifications': [spec(PAGE_ERC, 'Approved', 'a', PAGE_ERC + '-draft'), spec(PAGE_ERC + '-draft', 'Draft', 'd')]}
if os.environ.get('SMOKE_DUMP'):
    json.dump(page, open(os.environ['SMOKE_DUMP'], 'w'))
status, out = request('/o/headless-admin-site/v1.0/sites/L_GUEST/site-pages?privateLayout=false', data=json.dumps(page).encode(),
                      headers={'Content-Type': 'application/json'}, method='POST')
report(status == 200, 'create test page', f'HTTP {status}' + ('' if status == 200 else ' ' + out[:200]))

# 4. Rendered markup.
status, html = request('/web/guest/' + PAGE_ERC)
def has(name, pattern, count=None):
    found = re.findall(pattern, html, flags=re.S)
    ok = bool(found) if count is None else len(found) == count
    report(ok, name, f'{len(found)} match(es)')

has('carousel container with label', r'<div[^>]*aria-label="Highlights"[^>]*aria-roledescription="carousel"[^>]*role="group"')
has('inactive slides inert', r'<div[^>]*aria-hidden="true" inert [^>]*aria-roledescription="slide"', 2)
has('slides named by title', r'aria-labelledby="[^"]*-slide-title-0[123]"', 3)
has('pause and play labels localized', r'data-label-pause="Pause" data-label-play="Play"')
has('indicator labels and aria-current', r'<button[^>]*aria-current="(true|false)" aria-label="Go to Slide [123]"', 3)
has('accordion region', r'<div[^>]*aria-labelledby="accordion-title-[^"]+"[^>]*id="accordion-panel-[^"]+" role="region"')
has('dropdown labelledby fixed', r'<div aria-labelledby="dropdown-fragment-([^"]+)"[^>]*id="\1-dropdown-fragment-menu"', 2)
has('dropdown without aria-haspopup', r'dropdown-fragment-toggle[^>]*aria-haspopup', 0)
has('button accessible description', r'<a aria-describedby="fragment-([^"]+)-description"[^>]*>.*?</a>\s*<span class="sr-only" id="fragment-\1-description">about our pricing plans</span>')
has('card heading level', r'<h3>\s*<span[^>]*data-lfr-editable-id="02-title"')
has('cookie banner region', r'<div aria-label="Cookie consent" class="cookie-banner[^"]*" role="region">')
has('no empty title attributes', r'title=""', 0)
has('no FreeMarker errors', r'FreeMarker template error|freemarker\.core', 0)

print(f'\n{sum(results)} of {len(results)} checks passed; page {BASE}/web/guest/{PAGE_ERC}')
sys.exit(0 if all(results) else 1)
