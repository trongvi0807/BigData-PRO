"""Headless browser QA of the real HDFS-derived dashboard and prediction endpoint."""
import json
from datetime import datetime,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path('/workspace')
OUT=ROOT/'outputs'

def main():
    evidence={'verified_utc':datetime.now(timezone.utc).isoformat(),'base':'http://127.0.0.1:8090','browser':'Chromium headless'}
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(evidence['base']+'/?source=historical',wait_until='networkidle')
        page.wait_for_timeout(1500)
        overview=page.request.get(evidence['base']+'/api/overview?source=historical').json()
        if overview['stats']['reviews']!=1299873: raise ValueError('Overview total differs from HDFS')
        bootstrap=page.request.get(evidence['base']+'/api/bootstrap?source=historical').json()
        evidence['generation']=bootstrap['metadata']['generation']
        if len(bootstrap['evidence']['airflow']['tasks'])!=10: raise ValueError('Missing new DAG evidence')
        page.screenshot(path=str(OUT/'screenshots/04-overview-20261015.png'),full_page=True)
        page.locator('[data-view=pipeline]').click()
        if page.locator('#dag-steps .dag-step').count()!=10: raise ValueError('DAG row count in UI differs from actual tasks')
        if '10/10' not in page.locator('#dag-badge').inner_text(): raise ValueError('DAG UI denominator differs from actual run')
        page.screenshot(path=str(OUT/'screenshots/06-pipeline-20261015.png'),full_page=True)
        page.goto(evidence['base']+'/demo.html',wait_until='networkidle')
        text='Hàng tốt nhưng giao hàng quá chậm, ứng dụng thường xuyên bị lỗi.'
        page.locator('#review').fill(text)
        page.get_by_role('button',name='Phân tích').click()
        page.wait_for_function("document.querySelector('#technical-result').textContent.includes('sentiment')")
        result=json.loads(page.locator('#technical-result').text_content())
        if not {'app','delivery'}.issubset(result['aspects_mentioned']): raise ValueError('Missing demo aspects')
        if result['label_source']!='star_rating_proxy': raise ValueError('Missing label provenance')
        page.screenshot(path=str(OUT/'screenshots/05-model-demo-20261015.png'),full_page=True)
        invalid=page.request.post(evidence['base']+'/api/predict',data={'review':''})
        if invalid.status!=400: raise ValueError('Blank input not rejected')
        reviews=page.request.get(evidence['base']+'/api/reviews?source=historical&q=dang%20nhap&aspect=app').json()
        if reviews['total']<=0: raise ValueError('Unaccented search failed')
        evidence.update({'overview_rows':overview['stats']['reviews'],'prediction':result,'unaccented_search_matches':reviews['total'],
                         'invalid_input_status':invalid.status,'browser_errors':errors,'verification':'passed'})
        if errors: raise ValueError(errors)
        browser.close()
    (OUT/'dashboard_demo_validation.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
    print(json.dumps(evidence,ensure_ascii=False))
if __name__=='__main__': main()
