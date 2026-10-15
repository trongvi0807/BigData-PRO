"""Validate the final PDF against its immutable source/evidence manifest.

Run from the repository with Python 3 and pypdf installed. Poppler's pdftotext
adds word-boundary checks when available. The visual-review flag is a human
attestation and must only be used after every rendered page has been inspected.
No cluster process is started and no data or source files are modified.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = Path('output/pdf/report_manifest.json')
DEFAULT_OUTPUT = Path('outputs/report_validation.json')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def inside_root(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Manifest path leaves repository')
    return path


def compact(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFC', text))


def secret_values():
    """Read actual local secret values without reporting names or contents."""
    env_path = ROOT / '.env'
    if not env_path.exists():
        return [], False
    values = set()
    for raw in env_path.read_text(encoding='utf-8-sig').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        if line.startswith('export '):
            line = line[7:]
        name, value = line.split('=', 1)
        if not re.search(r'password|passwd|token|secret|(?:^|_)key(?:_|$)', name, re.I):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            value = re.split(r'\s+#', value, maxsplit=1)[0].strip()
        if len(value) < 8 or value.startswith(('$', '<')):
            continue
        if re.fullmatch(r'(?i)(?:change[ _-]?me.*|replace[ _-]?.*|your[ _-].*|example.*|placeholder.*|x+)', value):
            continue
        values.add(value)
    return sorted(values), True


def verify(manifest_arg, output_arg, visual_review_complete=False):
    checks = []

    def check(name, condition, **details):
        checks.append({'name': name, 'passed': bool(condition), **details})
        return bool(condition)

    manifest_path = inside_root(manifest_arg)
    output_path = inside_root(output_arg)
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    pdf_path = inside_root(manifest['pdf'])
    pdf_raw = pdf_path.read_bytes()
    pdf_sha = digest(pdf_raw)
    check('pdf_sha256_matches_manifest', pdf_sha == manifest.get('pdf_sha256'),
          actual=pdf_sha, expected=manifest.get('pdf_sha256'))
    check('pdf_signature', pdf_raw.startswith(b'%PDF-'))

    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    check('pdf_not_encrypted', not reader.is_encrypted)
    page_text = [unicodedata.normalize('NFC', page.extract_text() or '') for page in reader.pages]
    text = '\n'.join(page_text)
    dense_text = compact(text)
    check('pdf_pages_extracted', len(page_text) >= 15, page_count=len(page_text))
    empty_pages = [i + 1 for i, item in enumerate(page_text) if len(item.strip()) < 80]
    check('pages_contain_text', not empty_pages, empty_pages=empty_pages)
    bad_unicode = [{'page': i + 1, 'replacement_count': item.count('\ufffd'),
                    'null_count': item.count('\x00')} for i, item in enumerate(page_text)
                   if '\ufffd' in item or '\x00' in item]
    check('unicode_extraction', not bad_unicode, affected_pages=bad_unicode)

    headings = [
        'BÁO CÁO ĐỒ ÁN BIG DATA', 'Nguồn dữ liệu', 'HDFS: kiến thức',
        'PySpark đọc HDFS', 'Spark SQL', 'Machine Learning',
        'Kafka và Spark Structured Streaming', 'Airflow: DAG',
        'Dashboard', 'lệnh chạy từ đầu đến cuối', 'Nhật ký',
        'câu hỏi bảo vệ', 'Tài liệu tham khảo', 'Phụ lục',
    ]
    missing = [value for value in headings if compact(value).casefold() not in dense_text.casefold()]
    check('required_sections', not missing, missing=missing)
    check('unknown_identity_disclosed', 'Chưacungcấp' in dense_text)

    for key in ('historical_generation', 'live_generation'):
        expected = manifest.get(key)
        check(key + '_appears_in_pdf', bool(expected) and expected in dense_text)
    combined_generation = manifest.get('combined_generation', '')
    check('combined_generation_matches_components',
          combined_generation == ':'.join([manifest.get('historical_generation', ''),
                                           manifest.get('live_generation', '')]))
    for key in ('live_reviews', 'combined_reviews'):
        value = manifest.get(key)
        variants = [str(value), f'{value:,}', f'{value:,}'.replace(',', '.')] if isinstance(value, int) else []
        check(key + '_appears_in_pdf', any(compact(v) in dense_text for v in variants), expected=value)

    for kind in ('source_hashes', 'artifact_hashes'):
        entries = manifest.get(kind, {})
        check(kind + '_present', bool(entries), count=len(entries))
        for relative, expected in entries.items():
            try:
                raw = inside_root(relative).read_bytes()
                actual = digest(raw)
                check(kind + ':' + relative, actual == expected, expected=expected, actual=actual)
            except (OSError, ValueError):
                check(kind + ':' + relative, False, reason='File missing, unreadable or outside repository')

    snippets = manifest.get('snippets', [])
    check('snippets_present', bool(snippets), count=len(snippets))
    for index, snippet in enumerate(snippets, 1):
        relative = snippet.get('file', '')
        name = 'snippet_' + str(index)
        try:
            raw = inside_root(relative).read_bytes()
            lines = raw.decode('utf-8-sig').splitlines()
            start, end = snippet.get('start'), snippet.get('end')
            bounds = isinstance(start, int) and isinstance(end, int) and 1 <= start <= end <= len(lines)
            check(name + '_line_bounds', bounds, file=relative, start=start, end=end, file_lines=len(lines))
            source_sha = digest(raw)
            check(name + '_source_hash', source_sha == snippet.get('sha256')
                  == manifest.get('source_hashes', {}).get(relative), file=relative)
            if bounds:
                selected = '\n'.join(lines[start - 1:end])
                snippet_sha = digest(selected.encode('utf-8'))
                # The current manifest sha256 identifies the full source file.
                # Support an explicit fragment hash if a later builder adds it.
                check(name + '_content_hash', not snippet.get('snippet_sha256')
                      or snippet_sha == snippet['snippet_sha256'], file=relative,
                      content_sha256=snippet_sha,
                      expected_hash_available=bool(snippet.get('snippet_sha256')))
        except (OSError, UnicodeError, ValueError):
            check(name + '_readable', False, file=relative)

    # Cross-check report totals against the same immutable evidence used by the builder.
    quality = json.loads(inside_root('outputs/data_quality.json').read_text())
    for key in ('raw_rows', 'clean_rows', 'quarantined_rows', 'duplicate_valid_id_rows_removed'):
        value = quality[key]
        formatted = f'{value:,}'.replace(',', '.')
        check('historical_' + key + '_appears_in_pdf', formatted in dense_text, expected=value)
    live_meta_path = 'outputs/live/generations/' + manifest['live_generation'] + '/dashboard_preparation.json'
    live_meta = json.loads(inside_root(live_meta_path).read_text())
    check('live_count_matches_immutable_snapshot', live_meta['processed_rows'] == manifest['live_reviews'])
    combined = json.loads(inside_root('outputs/combined_source_validation.json').read_text())
    check('combined_snapshot_matches_manifest', combined['generation'] == combined_generation
          and combined['total_reviews'] == manifest['combined_reviews'])

    # Inspect positioned Poppler words for clipping beyond the physical page edge.
    # This is an automatic geometry check, not a substitute for visual inspection.
    geometry = {'available': bool(shutil.which('pdftotext')), 'method': 'pdftotext -bbox-layout'}
    if geometry['available']:
        process = subprocess.run(['pdftotext', '-bbox-layout', str(pdf_path), '-'],
                                 capture_output=True, check=False)
        if process.returncode:
            check('page_word_bounds', False, reason='Poppler extraction failed')
        else:
            doc = ET.fromstring(process.stdout)
            ns = {'x': 'http://www.w3.org/1999/xhtml'}
            overflows = []
            word_count = 0
            pages = doc.findall('.//x:page', ns)
            for number, page in enumerate(pages, 1):
                width, height = float(page.attrib['width']), float(page.attrib['height'])
                for word in page.findall('.//x:word', ns):
                    word_count += 1
                    box = [float(word.attrib[key]) for key in ('xMin', 'yMin', 'xMax', 'yMax')]
                    if box[0] < 10 or box[1] < 10 or box[2] > width - 10 or box[3] > height - 10:
                        # Never include extracted words: one could contain an exposed secret.
                        overflows.append({'page': number, 'bounds': box})
            geometry.update(pages=len(pages), words=word_count, overflow_count=len(overflows))
            check('page_word_bounds', not overflows and len(pages) == len(reader.pages)
                  and word_count > 0, affected_bounds=overflows[:50], **geometry)

    values, env_exists = secret_values()
    leaked = 0
    for value in values:
        encoded = value.encode('utf-8')
        if encoded in pdf_raw or value in text or compact(value) in dense_text:
            leaked += 1
    check('actual_env_values_absent', leaked == 0, env_file_present=env_exists,
          values_checked=len(values), exposed_value_count=leaked)

    success = all(item['passed'] for item in checks)
    report = {
        'verified_utc': datetime.now(timezone.utc).isoformat(),
        'verification': 'passed' if success else 'failed',
        'scope': 'PDF text, source/evidence fingerprints, snippet bounds, snapshots, secret scan and optional page geometry; no live cluster rerun',
        'pdf': str(pdf_path.relative_to(ROOT)), 'pdf_sha256': pdf_sha,
        'manifest': str(manifest_path.relative_to(ROOT)), 'manifest_sha256': digest(manifest_raw),
        'page_count': len(reader.pages), 'text_characters': len(text),
        'visual_review_complete': bool(visual_review_complete),
        'visual_review_basis': ('Operator explicitly attested that every rendered page was inspected'
                                if visual_review_complete else 'Not claimed by this automatic validator'),
        'geometry': geometry, 'checks': checks,
        'failed_checks': [item['name'] for item in checks if not item['passed']],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('verification', 'page_count', 'pdf_sha256',
                                                 'visual_review_complete', 'failed_checks')}, ensure_ascii=False))
    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--visual-review-complete', action='store_true',
                        help='Attest only AFTER inspecting every page rendered from this exact PDF')
    args = parser.parse_args()
    try:
        return verify(args.manifest, args.output, args.visual_review_complete)
    except Exception as exc:
        # Do not print exception text or input contents that could expose secrets.
        report = {'verified_utc': datetime.now(timezone.utc).isoformat(),
                  'verification': 'failed', 'error_type': type(exc).__name__,
                  'reason': 'Validation aborted; ensure PDF, manifest, evidence and pypdf are available',
                  'visual_review_complete': False}
        output = inside_root(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report))
        return 1


if __name__ == '__main__':
    sys.exit(main())
