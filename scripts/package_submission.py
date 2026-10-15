"""Package source, final PDF and reproducible technical evidence."""
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def package():
    target=ROOT/'submission';target.mkdir(exist_ok=True)
    frozen={}
    def snapshot_json(path):
        if path not in frozen: frozen[path]=path.read_bytes()
        return json.loads(frozen[path].decode('utf-8-sig'))
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    selected={ROOT/name for name in tracked if name and not name.startswith(('reports/','outputs/','output/','artifacts/','submission/'))}
    current=['data_quality.json','raw_inspection.json','batch_success.json','cluster_metadata.json','demo_evidence.json',
             'persisted_validation.json','dashboard_preparation.json','dashboard_validation.json','sentiment_evaluation.json',
             'sentiment_model.json','dashboard_demo_validation.json','auto_filters_validation.json','live_dashboard_validation.json','clear_filters_validation.json','combined_source_validation.json','replay_browser_validation.json','replay_restart_validation.json','submission_validation.json','report_validation.json','spark_query_plan.txt',
             'quality_before_airflow.json','platform_summary.csv','monthly_summary.csv','rating_distribution.csv',
             'aspect_mentions.csv','unmatched_low_ratings.csv','spam_sensitivity.csv','review_length_summary.csv','dashboard_cube.csv']
    selected.update(ROOT/'outputs'/name for name in current)
    final=snapshot_json(ROOT/'output/pdf/report_manifest.json')
    selected.update([ROOT/final['pdf'],ROOT/'output/pdf/report_manifest.json'])
    selected.update(ROOT/name for name in final['artifact_hashes'])
    progress=snapshot_json(ROOT/'output/pdf/progress_report_manifest.json')
    progress_pdf=ROOT/progress['pdf']
    if hashlib.sha256(progress_pdf.read_bytes()).hexdigest()!=progress['pdf_sha256'] or not all(progress['checks'].values()) or not progress.get('visual_review_complete'):
        raise ValueError('Progress PDF validation missing or stale')
    template=ROOT/'docs/templates/01_Bao_cao_tien_do.pdf'
    if hashlib.sha256(template.read_bytes()).hexdigest()!=progress['template_sha256']:
        raise ValueError('Progress report template fingerprint differs')
    selected.update([progress_pdf,ROOT/'output/pdf/progress_report_manifest.json',template,ROOT/'scripts/build_progress_report.py'])
    selected.update(ROOT/name for name in progress['evidence_hashes'])
    from validate_final_report import secret_values, compact
    from pypdf import PdfReader
    values,_=secret_values()
    pdf_text='\n'.join(p.extract_text() or '' for p in PdfReader(ROOT/final['pdf']).pages)
    if any(value in pdf_text or compact(value) in compact(pdf_text) for value in values):
        raise ValueError('Credential leak found in PDF text; refusing package')
    if hashlib.sha256((ROOT/final['pdf']).read_bytes()).hexdigest()!=final['pdf_sha256']:
        raise ValueError('Final PDF differs from report manifest')
    selected.update((ROOT/'outputs').glob('stream_batch_*.json'))
    live=ROOT/'outputs/live'
    if (live/'current.json').exists():
        selected.update(live/name for name in ['current.json','collection_status.json','dag_evidence.json','observation_timeline.json'])
        selected.update(live.glob('stream_batch_*.json'))
        selected.update((live/'collection_runs').glob('*.json'))
        generations={snapshot_json(live/'current.json')['generation'],snapshot_json(ROOT/'outputs/live_dashboard_validation.json')['generation']}
        for name in ['clear_filters_validation.json','combined_source_validation.json']:
            generations.add(snapshot_json(ROOT/'outputs'/name)['generation'].split(':')[1])
        generations.add(final['live_generation'])
        for generation in generations:
            if generation=='none':continue
            snapshot=live/'generations'/generation
            selected.update(snapshot/name for name in ['dashboard_preparation.json','dashboard_cube.csv','data_quality.json','persisted_validation.json','dashboard_validation.json'])
    replay=ROOT/'outputs/replay'
    selected.update(replay.glob('*.json'))
    selected.update(replay.glob('runs/*/*.json'))
    selected.update(replay.glob('runs/*/*.log'))
    selected.update((ROOT/'outputs/logs/replay_airflow_tasks').rglob('*.log'))
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
    contents={}
    for file in sorted(selected):
        if not file.is_file(): raise ValueError(f'Missing requested evidence: {file.relative_to(ROOT)}')
        relative=file.relative_to(ROOT).as_posix()
        if file.name=='.env' or file.suffix in ['.sqlite','.db'] or file.name=='vietnamese_ecommerce_review.csv': raise ValueError('Disallowed data/secret file')
        content=frozen[file] if file in frozen else file.read_bytes()
        if file.suffix.lower()=='.pdf':
            text='\n'.join(page.extract_text() or '' for page in PdfReader(file).pages)
            if any(value in text or compact(value) in compact(text) for value in values):
                raise ValueError('Credential leak found in PDF text; refusing package')
        if any(secret in content for secret in secrets): raise ValueError(f'Credential leak found in {relative}; refusing package')
        contents[file]=content
        entries.append({'path':relative,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
    manifest={'prepared_utc':datetime.now(timezone.utc).isoformat(),'evidence_run_id':'validation_20261015','live_evidence':'outputs/live/dag_evidence.json',
              'scope':'Source, final and progress PDFs, technical evidence; member identity provided, individual contributions unverified',
              'credential_scan':'local .env values absent from every packaged file including Git bundle; final PDF text also scanned','entries':entries}
    (ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    archive=target/'Source_va_minh_chung_Bigdata.zip'
    candidate=target/'Source_va_minh_chung_Bigdata.zip.tmp'
    with zipfile.ZipFile(candidate,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for file in sorted(selected): z.writestr(file.relative_to(ROOT).as_posix(),contents[file])
        z.write(ROOT/'MANIFEST_SHA256.json','MANIFEST_SHA256.json')
    with zipfile.ZipFile(candidate) as z:
        if z.testzip(): raise ValueError('Archive integrity failed')
        for entry in entries:
            if hashlib.sha256(z.read(entry['path'])).hexdigest()!=entry['sha256']: raise ValueError('Archive fingerprint mismatch')
    if candidate.stat().st_size >= 20_000_000:
        raise ValueError('ZIP exceeds the strict 20 MB upload limit; previous ZIP preserved')
    candidate.replace(archive)
    validation={'verification':'passed','archive':str(archive.relative_to(ROOT)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'limit_bytes':20_000_000,'files':len(entries)+1,'credential_scan':'passed','zip_integrity':'passed','progress_pdf_included':progress['pdf'],'final_pdf_included':final['pdf']}
    (ROOT/'outputs/package_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(entries)+1,'credential_scan':'passed','zip_integrity':'passed'}))
if __name__=='__main__': package()
