import json
from pathlib import Path
root=Path('/exports/live')
pointer=json.loads((root/'current.json').read_text())
folder=root/'generations'/pointer['generation']
meta=json.loads((folder/'dashboard_preparation.json').read_text())
check=json.loads((folder/'dashboard_validation.json').read_text())
if meta['source_mode']!='google_play_live' or check['generation']!=meta['generation'] or not check['all_spark_cube_counts_match_full_index']: raise ValueError('Invalid live publication')
if meta['processed_rows']!=check['indexed_reviews']: raise ValueError('Live count mismatch')
print(json.dumps({'verification':'passed','source_mode':meta['source_mode'],'real_reviews':meta['processed_rows'],'generation':meta['generation']}))
