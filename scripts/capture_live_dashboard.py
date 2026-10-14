"""Real-source browser and HDFS-derived snapshot checks; no generated review input."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8090';ROOT=Path('/workspace');OUT=ROOT/'outputs'

def main():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1000})
        page.on('pageerror',lambda e:errors.append(str(e)))
        boot=page.request.get(BASE+'/api/bootstrap?source=live').json()
        meta=boot['metadata'];collection=boot['collection']
        if meta['source_mode']!='google_play_live' or not meta['processed_rows']: raise ValueError('No real live publication')
        overview=page.request.get(BASE+'/api/overview?source=live').json()
        if overview['stats']['reviews']!=meta['processed_rows']: raise ValueError('Real-source API count mismatch')
        page.goto(BASE+'/?source=live',wait_until='networkidle')
        page.wait_for_function('(n)=>state.data && state.data.stats.reviews===n',arg=meta['processed_rows'])
        page.screenshot(path=str(OUT/'screenshots/08-real-live-overview-20261015.png'),full_page=True)
        page.locator('[data-view=pipeline]').click()
        if page.locator('#dag-steps .dag-step').count()!=4 or '4/4' not in page.locator('#dag-badge').inner_text(): raise ValueError('No successful live DAG evidence')
        page.screenshot(path=str(OUT/'screenshots/09-real-live-pipeline-20261015.png'),full_page=True)
        page.locator('[data-view=reviews]').click()
        page.locator('#review-score').select_option('all')
        page.wait_for_function('state.reviewResult && state.reviewResult.total===state.boot.metadata.processed_rows')
        page.screenshot(path=str(OUT/'screenshots/10-real-live-reviews-20261015.png'),full_page=True)
        if errors: raise ValueError(errors)
        result={'verification':'passed','source_mode':'google_play_live','generation':meta['generation'],
                'real_review_count':meta['processed_rows'],'source_month_min':meta['month_min'],'source_month_max':meta['month_max'],
                'collection_poll_id':collection['poll_id'],'source_errors':collection['errors'],
                'dag':boot['evidence']['airflow'],'browser_errors':errors,'auto_filter_buttons_removed':page.get_by_role('button',name='Áp dụng',exact=True).count()==0}
        browser.close()
    (OUT/'live_dashboard_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__': main()
