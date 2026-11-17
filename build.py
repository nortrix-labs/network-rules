#!/usr/bin/env python3
"""Build a domain-only Shadowrocket feed. No device configs or credentials."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

SOURCES = {
    'hagezi-pro': ('https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/pro-onlydomains.txt', 'domains', 50000),
    'anti-ad': ('https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-surge.txt', 'surge', 30000),
}
ROOT = Path(__file__).resolve().parent
MAX_BYTES = 16 * 1024 * 1024


def canonical(value):
    name = value.strip().lower().removeprefix('*.').removeprefix('.').rstrip('.')
    name = name.encode('idna').decode('ascii')
    if len(name) > 253 or '.' not in name or not re.fullmatch(r'[a-z0-9.-]+', name):
        raise ValueError('Invalid domain input')
    for label in name.split('.'):
        if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label):
            raise ValueError('Invalid domain label')
    try:
        ipaddress.ip_address(name)
    except ValueError:
        return name
    raise ValueError('IP literals are outside this domain-only feed')


def parse(raw, kind):
    domains = set()
    for line in raw.decode('utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith(('#', '!')):
            continue
        if kind == 'surge':
            fields = line.split(',')
            if len(fields) != 2 or fields[0] != 'DOMAIN-SUFFIX':
                raise ValueError('Upstream syntax changed; review before publishing')
            line = fields[1]
        domains.add(canonical(line))
    return domains


def ancestors(domain):
    labels = domain.split('.')
    return ('.'.join(labels[index:]) for index in range(1, len(labels)))


def consolidate(domains, protected):
    retained = set()
    for name in sorted(domains, key=lambda x: (x.count('.'), x)):
        # Exclude both a protected namespace and any broad parent that would
        # swallow it. A child exception must not be defeated by a parent block.
        if any(name == p or name.endswith('.' + p) or p.endswith('.' + name) for p in protected):
            continue
        if not any(parent in retained for parent in ancestors(name)):
            retained.add(name)
    return sorted(retained)


def check_size(name, count, previous, minimum):
    if count < minimum:
        raise ValueError(name + ': suspiciously small input; keeping previous published feed')
    if previous and not .70 <= count / previous <= 1.50:
        raise ValueError(name + ': large count drift requires review; keeping previous feed')


def retrieve(item):
    name, (url, kind, minimum) = item
    for attempt in range(3):
        try:
            with urlopen(url, timeout=30) as response:
                if response.geturl() != url:
                    raise ValueError('Unexpected upstream redirect')
                raw = response.read(MAX_BYTES + 1)
            break
        except (HTTPError, URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code < 500 and error.code != 429:
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    if len(raw) > MAX_BYTES:
        raise ValueError('Upstream exceeded bounded download size')
    domains = parse(raw, kind)
    check_size(name, len(domains), None, minimum)
    return name, domains, {'url': url, 'sha256': hashlib.sha256(raw).hexdigest(), 'domain_count': len(domains)}


def build(output, previous=None):
    old = json.loads(previous.read_text()) if previous and previous.exists() else {}
    protected = {canonical(x) for x in (ROOT / 'protected-domains.txt').read_text().splitlines() if x and not x.startswith('#')}
    all_domains, metadata = set(), {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for name, domains, source in pool.map(retrieve, SOURCES.items()):
            check_size(name, len(domains), old.get('sources', {}).get(name, {}).get('domain_count'), SOURCES[name][2])
            all_domains.update(domains); metadata[name] = source
    merged = consolidate(all_domains, protected)
    check_size('merged', len(merged), old.get('domain_count'), 50000)
    # A positive block sentinel and protected negative controls catch accidental
    # empty/allow-all output; these are policy checks, not live ad efficacy tests.
    if not any('doubleclick.net' == x or 'doubleclick.net'.endswith('.' + x) for x in merged):
        raise ValueError('Known ad sentinel missing')
    output.mkdir(parents=True, exist_ok=True)
    body = '# Nortrix domain-only ad feed; GPL-3.0. See LICENSE and SOURCES.md.\n'
    body += '\n'.join('.' + name for name in merged) + '\n'
    manifest = {'built_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'builder_revision': os.environ.get('GITHUB_SHA', 'local-validation'),
                'domain_count': len(merged), 'sources': metadata,
                'protected_namespaces': sorted(protected),
                'feed_sha256': hashlib.sha256(body.encode()).hexdigest()}
    (output / 'ads.list').write_text(body)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for name in ('LICENSE', 'SOURCES.md'):
        shutil.copyfile(ROOT / name, output / name)
    shutil.copytree(ROOT / 'licenses', output / 'licenses', dirs_exist_ok=True)
    print(json.dumps({'domain_count': len(merged), 'source_counts': {k: v['domain_count'] for k, v in metadata.items()}}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--previous', type=Path)
    args = parser.parse_args()
    build(args.output, args.previous)
