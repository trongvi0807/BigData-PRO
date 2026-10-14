"""Package current source and reproducible technical evidence; no final PDF at user's request."""
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def package():
    target=ROOT/'submission';target.mkdir(exist_ok=True)
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    selected={ROOT/name for name in tracked if name and not name.startswith(('reports/','outputs/','artifacts/','submission/'))}
    current=['data_quality.json','raw_inspection.json','batch_success.json','cluster_metadata.json','demo_evidence.json',
             'persisted_validation.json','dashboard_preparation.json','dashboard_validation.json','sentiment_evaluation.json',
             'sentiment_model.json','dashboard_demo_validation.json','auto_filters_validation.json','live_dashboard_validation.json','clear_filters_validation.json','combined_source_validation.json','submission_validation.json','spark_query_plan.txt',
             'quality_before_airflow.json','platform_summary.csv','monthly_summary.csv','rating_distribution.csv',
             'aspect_mentions.csv','unmatched_low_ratings.csv','spam_sensitivity.csv','review_length_summary.csv','dashboard_cube.csv']
    selected.update(ROOT/'outputs'/name for name in current)
    selected.update((ROOT/'outputs').glob('stream_batch_*.json'))
    live=ROOT/'outputs/live'
    if (live/'current.json').exists():
        selected.update(live/name for name in ['current.json','collection_status.json','dag_evidence.json'])
        selected.update(live.glob('stream_batch_*.json'))
        selected.update((live/'collection_runs').glob('*.json'))
        generation=json.loads((live/'current.json').read_text())['generation']
        snapshot=live/'generations'/generation
        selected.update(snapshot/name for name in ['dashboard_preparation.json','dashboard_cube.csv','data_quality.json','persisted_validation.json','dashboard_validation.json'])
    selected.update((ROOT/'outputs/logs/live_airflow_tasks').rglob('*.log'))
    selected.add(ROOT/'artifacts/audit/dataset_profile.json')
    selected.update((ROOT/'outputs/logs').glob('*20261015.*'))
    selected.update((ROOT/'outputs/logs/airflow_tasks').rglob('*.log'))
    selected.update((ROOT/'outputs/screenshots').glob('*20261015.png'))
    selected.update((ROOT/'outputs/report_charts').glob('*'))
    history=subprocess.check_output(['git','log','--date=iso-strict','--format=fuller','--stat'],cwd=ROOT)
    (target/'GIT_HISTORY.txt').write_bytes(history)
    selected.add(target/'GIT_HISTORY.txt')
    subprocess.run(['git','bundle','create',str(target/'source_history.bundle'),'--all'],cwd=ROOT,check=True)
    selected.add(target/'source_history.bundle')
    secrets=[]
    for line in (ROOT/'.env').read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            value=line.split('=',1)[1].strip()
            if value: secrets.append(value.encode())
    entries=[]
    for file in sorted(selected):
        if not file.is_file(): raise ValueError(f'Missing requested evidence: {file.relative_to(ROOT)}')
        relative=file.relative_to(ROOT).as_posix()
        if file.name=='.env' or file.suffix in ['.sqlite','.db'] or file.name=='vietnamese_ecommerce_review.csv': raise ValueError('Disallowed data/secret file')
        content=file.read_bytes()
        if any(secret in content for secret in secrets): raise ValueError(f'Credential leak found in {relative}; refusing package')
        entries.append({'path':relative,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
    manifest={'prepared_utc':datetime.now(timezone.utc).isoformat(),'evidence_run_id':'validation_20261015','live_evidence':'outputs/live/dag_evidence.json',
              'scope':'Source and technical verification only; no final PDF created at user request',
              'credential_scan':'local .env values absent from every packaged file including Git bundle','entries':entries}
    (ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    archive=target/'Source_va_minh_chung_Bigdata.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for file in sorted(selected): z.write(file,file.relative_to(ROOT).as_posix())
        z.write(ROOT/'MANIFEST_SHA256.json','MANIFEST_SHA256.json')
    with zipfile.ZipFile(archive) as z:
        if z.testzip(): raise ValueError('Archive integrity failed')
        for entry in entries:
            if hashlib.sha256(z.read(entry['path'])).hexdigest()!=entry['sha256']: raise ValueError('Archive fingerprint mismatch')
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(entries)+1,'credential_scan':'passed','zip_integrity':'passed'}))
if __name__=='__main__': package()
