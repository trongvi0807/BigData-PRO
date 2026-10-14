"""Verify submission consistency, fingerprints, tasks and references without claiming live HDFS."""
import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(name): return json.loads((ROOT/name).read_text())
def require(condition,message):
    if not condition: raise ValueError(message)

def verify():
    quality=read('outputs/data_quality.json')
    require(quality['raw_rows']==quality['clean_rows']+quality['quarantined_rows']+quality['duplicate_valid_id_rows_removed'],'Row imbalance')
    require(read('artifacts/audit/dataset_profile.json')['sha256']==read('outputs/raw_inspection.json')['source_sha256'],'Source fingerprints disagree')
    for name in ['platform_summary','monthly_summary','rating_distribution','review_length_summary']:
        with (ROOT/'outputs'/f'{name}.csv').open(encoding='utf-8-sig',newline='') as handle: rows=list(csv.DictReader(handle))
        require(sum(int(r['reviews']) for r in rows)==quality['clean_rows'],f'{name} total mismatch')
    evidence=read('outputs/demo_evidence.json')
    tasks=evidence['airflow']['tasks']
    require(len(tasks)==10 and all(t['state']=='success' for t in tasks),'Airflow new DAG not successful')
    require(all(evidence['repeated_batch_counts_unchanged'].values()),'Rerun changed row counts')
    require(evidence['kafka_total_offsets']>=2000,'No Kafka replay evidence')
    persisted=read('outputs/persisted_validation.json')
    require(persisted['processed_rows']==persisted['processed_unique_keys']==quality['clean_rows'],'Processed uniqueness failed')
    require(persisted['streaming_rows']==persisted['streaming_unique_keys']==1000,'Streaming uniqueness failed')
    ml=read('outputs/sentiment_evaluation.json')
    require(not any(ml['leakage_checks'].values()) and ml['portable_predictions_checked']>0,'Model split/serving validation failed')
    require(read('outputs/dashboard_validation.json')['all_spark_cube_counts_match_full_index'] is True,'Dashboard counts failed')
    commits=subprocess.check_output(['git','log','--format=%h %s'],cwd=ROOT,text=True)
    require(bool(commits.strip()),'Missing actual Git history')
    report={'verified_utc':datetime.now(timezone.utc).isoformat(),'verification':'passed','scope':'Technical saved artifacts and source/log cross-checks; final report excluded at user request; not a live cluster check',
            'airflow_tasks':len(tasks),'clean_rows':quality['clean_rows'],'ml_label_source':ml['label_source'],
            'final_report':'Not created at user request',
            'individual_contributions':'Not independently attributable from the supplied plan; no fabricated member commits'}
    (ROOT/'outputs/submission_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': verify()
