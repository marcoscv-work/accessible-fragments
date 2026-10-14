#!/usr/bin/env python3
"""Creates the demo page used for the storefront screenshots on a local
portal where the collection is imported and the demo artwork is uploaded.

    LIFERAY_URL=http://localhost:8080 LIFERAY_AUTH=test@liferay.com:test \
    SLIDE_1=/documents/... SLIDE_2=... SLIDE_3=... CARD=... python3 scripts/demo-page.py
"""
import base64
import json
import os
import urllib.request

BASE = os.environ.get('LIFERAY_URL', 'http://localhost:8080').rstrip('/')
AUTH = os.environ.get('LIFERAY_AUTH', 'test@liferay.com:test')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'accessible-components')
PAGE_ERC = os.environ.get('PAGE_ERC', 'accessible-fragments-test')
IMAGES = {k: os.environ.get(k, '') for k in ('SLIDE_1', 'SLIDE_2', 'SLIDE_3', 'CARD')}


def api(path, data=None, method=None):
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header('Authorization', 'Basic ' + base64.b64encode(AUTH.encode()).decode())
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


status, out = api('/api/jsonws/group/get-user-sites-groups')
group_id = next(str(g['groupId']) for g in json.loads(out) if g.get('friendlyURL') == '/guest')
status, out = api(f'/api/jsonws/fragment.fragmentcollection/get-fragment-collections/group-id/{group_id}')
collection = next(c for c in json.loads(out) if c['fragmentCollectionKey'] == 'accessible-components')
status, out = api(f"/api/jsonws/fragment.fragmententry/get-fragment-entries/fragment-collection-id/{collection['fragmentCollectionId']}")
ERC = {e['fragmentEntryKey']: e['externalReferenceCode'] for e in json.loads(out)}


def text(v): return {'type': 'Text', 'value_i18n': {'en-US': v}}
def select(v): return {'type': 'Select', 'value': v}
def t(id_, value):
    return {'id': id_, 'fragmentEditableElementValue': {'type': 'Text', 'fragmentLinkTextValue': {'textFragmentValue': {'type': 'Inline', 'fragmentInlineValue': {'value_i18n': {'en-US': value}}}}}}
def rich(id_, html):
    return {'id': id_, 'fragmentEditableElementValue': {'type': 'RichText', 'htmlFragmentValue': {'type': 'Inline', 'fragmentInlineValue': {'value_i18n': {'en-US': html}}}}}
def link(id_, value, href):
    return {'id': id_, 'fragmentEditableElementValue': {'type': 'Link', 'fragmentLinkTextValue': {
        'textFragmentValue': {'type': 'Inline', 'fragmentInlineValue': {'value_i18n': {'en-US': value}}},
        'fragmentEditableElementValueFragmentLink': {'fragmentLink': {'target': 'Self', 'value': {'type': 'FragmentInlineValue', 'value_i18n': {'en-US': href}}}}}}}
def image(id_, url, alt):
    return {'id': id_, 'fragmentEditableElementValue': {'type': 'Image', 'fragmentImage': {
        'description_i18n': {'en-US': alt},
        'fragmentImageValue': {'type': 'Direct', 'value_i18n': {'en-US': {'type': 'URL', 'url': url}}}}}}


FRAGMENTS = [
    ('banner-slider', {'numberOfSlides': text('3'), 'ariaLabel': text('Highlights')}, [
        image('01-01-image', IMAGES['SLIDE_1'], ''), rich('01-02-title', '<p>Pause when you need to</p>'), rich('01-03-subtitle', '<p>The slider only moves when the visitor lets it, and never under reduced motion.</p>'), link('01-04-link', 'See how it works', '/web/guest/home'),
        image('02-01-image', IMAGES['SLIDE_2'], ''), rich('02-02-title', '<p>Keyboard first</p>'), rich('02-03-subtitle', '<p>Every control is reachable, named, and shows where the focus is.</p>'), link('02-04-link', 'Try it with Tab', '/web/guest/home'),
        image('03-01-image', IMAGES['SLIDE_3'], ''), rich('03-02-title', '<p>Captions included</p>'), rich('03-03-subtitle', '<p>Videos carry a title and a captions track in the visitor language.</p>'), link('03-04-link', 'Read the guide', '/web/guest/home'),
    ]),
    ('card', {'headingLevel': select('h3')}, [
        image('01-img', IMAGES['CARD'], 'Abstract indigo artwork'), rich('02-title', 'Headings that follow the page'), rich('03-content', '<p>Pick the heading level of each card so screen reader users get one consistent outline, whatever the section it sits in.</p>'), link('04-link', 'Learn more', '/web/guest/home'),
    ]),
    ('button', {'accessibleDescription': text('about the Accessible Fragments fragment set')}, [link('link', 'Read more', '/web/guest/home')]),
    ('video', {'url': text('/documents/sample.mp4'), 'videoTitle': text('Product tour'), 'captionsUrl': text('/documents/sample.vtt')}, []),
    ('cookie-banner-simple', {}, [rich('01-text', '<p>This site uses cookies to remember your preferences. <a href="/web/guest/home">Learn more</a>.</p>'), link('02-link', 'Accept', '')]),
]


def element(key, cfg, editables, i, suffix):
    read = lambda f: open(os.path.join(SRC, key, f)).read()
    return {'externalReferenceCode': f'{key}-{suffix}', 'position': i, 'pageElementDefinition': {'type': 'BasicFragment', 'fragmentInstance': {
        'fragmentInstanceExternalReferenceCode': f'{key}-{suffix}-inst',
        'fragmentReference': {'fragmentReferenceType': 'FragmentItemExternalReference', 'externalReferenceCode': ERC[key]},
        'fragmentConfigurationFieldValues': cfg, 'fragmentEditableElements': editables,
        'html': read('index.html'), 'css': read('index.css'), 'js': read('index.js'), 'configuration': read('configuration.json')}}}


def spec(erc, status, suffix, draft=None):
    s = {'externalReferenceCode': erc, 'status': status, 'type': 'ContentPageSpecification', 'pageExperiences': [{
        'externalReferenceCode': erc + '-default', 'key': 'DEFAULT', 'name_i18n': {'en-US': 'Default'},
        'pageElements': [{'externalReferenceCode': 'section-' + suffix, 'position': 0,
                          'pageElementDefinition': {'type': 'Container', 'indexed': False, 'layout': {'widthType': 'Fixed'}},
                          'pageElements': [element(k, c, e, i, suffix) for i, (k, c, e) in enumerate(FRAGMENTS)]}]}]}
    if draft:
        s['draftContentPageSpecificationExternalReferenceCode'] = draft
    return s


page = {'externalReferenceCode': PAGE_ERC, 'friendlyUrlPath_i18n': {'en-US': '/accessible-fragments-demo'},
        'name_i18n': {'en-US': 'Accessible Fragments demo'}, 'type': 'ContentPage',
        'pageSpecifications': [spec(PAGE_ERC, 'Approved', 'a', PAGE_ERC + '-draft'), spec(PAGE_ERC + '-draft', 'Draft', 'd')]}
api('/o/headless-admin-site/v1.0/sites/L_GUEST/site-pages/' + PAGE_ERC, method='DELETE')
status, out = api('/o/headless-admin-site/v1.0/sites/L_GUEST/site-pages', data=json.dumps(page).encode(), method='POST')
print('HTTP', status, '' if status == 200 else out[:400])
print(f'{BASE}/web/guest/accessible-fragments-demo')
