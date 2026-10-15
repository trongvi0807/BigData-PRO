"""Updated 13-page progress report following the user-supplied PDF template."""
import csv,hashlib,json,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY,TA_LEFT,TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak,Image,KeepTogether
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'output/pdf/Bao_cao_tien_do_ReviewLens.pdf'
TEMPLATE=ROOT/'docs/templates/01_Bao_cao_tien_do.pdf'
NOW=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'))
EVIDENCE={};PAGE_HEADINGS=[]
def J(path):
 raw=(ROOT/path).read_bytes();EVIDENCE[path]=hashlib.sha256(raw).hexdigest();return json.loads(raw.decode('utf-8-sig'))
def C(path):
 raw=(ROOT/path).read_bytes();EVIDENCE[path]=hashlib.sha256(raw).hexdigest();return list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
def N(value):return f'{int(value):,}'.replace(',','.')
def D(value,k=2):return f'{float(value):.{k}f}'.replace('.',',')
def pc(value,k=2):return D(100*float(value),k)+'%'
quality=J('outputs/data_quality.json');audit=J('artifacts/audit/dataset_profile.json')
evidence=J('outputs/demo_evidence.json');persisted=J('outputs/persisted_validation.json')
ml=J('outputs/sentiment_evaluation.json');cluster=J('outputs/cluster_metadata.json')
browser=J('outputs/live_dashboard_validation.json');live_gen=browser['generation']
live=J('outputs/live/generations/'+live_gen+'/dashboard_preparation.json')
combined=J('outputs/combined_source_validation.json');clear=J('outputs/clear_filters_validation.json')
replay=J('outputs/replay/validation_054f7512feb1480c9d389ae11f4071e1.json')
replay_browser=J('outputs/replay_browser_validation.json');restart=J('outputs/replay_restart_validation.json')
dash=J('outputs/dashboard_validation.json');auto=J('outputs/auto_filters_validation.json')
platform=C('outputs/platform_summary.csv');unmatched=C('outputs/unmatched_low_ratings.csv');aspects=C('outputs/aspect_mentions.csv')
assert combined['generation']==clear['generation'] and combined['generation'].split(':')[1]==live_gen
low=sum(int(r['low_rating_reviews']) for r in platform);unmapped=sum(int(r['unmatched_reviews']) for r in unmatched)
matched=low-unmapped
by_platform={r['platform']:r for r in platform};order=['Shopee','Lazada','Sendo','Tiki']
by_aspect={}
for row in aspects:by_aspect[row['aspect']]=by_aspect.get(row['aspect'],0)+int(row['mention_reviews'])
MEMBERS=[['2001230757','Huỳnh Quang Sang','14DHTH13'],['2001230915','Phan Đức Thể','14DHTH13'],['2001231033','Đỗ Trọng Vĩ','14DHTH06']]
TEACHER='TS. Huỳnh Thái Học'
for name,file in [('T','times.ttf'),('TB','timesbd.ttf'),('TI','timesi.ttf'),('AB','arialbd.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/mnt/c/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('T',normal='T',bold='TB',italic='TI',boldItalic='TB')
BLACK=colors.HexColor('#111111');GRID=colors.HexColor('#c9c9c9');LIGHT=colors.HexColor('#eeeeee')
W,H=A4;CW=W-99-71
styles={
 'body':ParagraphStyle('body',fontName='T',fontSize=12.4,leading=17.4,spaceAfter=9,firstLineIndent=19,alignment=TA_JUSTIFY,allowWidows=0,textColor=BLACK),
 'plain':ParagraphStyle('plain',fontName='T',fontSize=12.2,leading=17.2,spaceAfter=8,alignment=TA_JUSTIFY,allowWidows=0,textColor=BLACK),
 'center':ParagraphStyle('center',fontName='T',fontSize=13,leading=19,spaceAfter=7,alignment=TA_CENTER,textColor=BLACK),
 'title':ParagraphStyle('title',fontName='TB',fontSize=17,leading=22,spaceAfter=12,alignment=TA_CENTER,textColor=BLACK),
 'topic':ParagraphStyle('topic',fontName='TB',fontSize=13.5,leading=19,spaceAfter=12,alignment=TA_CENTER,textColor=BLACK),
 'h1':ParagraphStyle('h1',fontName='TB',fontSize=14,leading=19,spaceBefore=8,spaceAfter=13,keepWithNext=True,textColor=BLACK),
 'h2':ParagraphStyle('h2',fontName='TB',fontSize=12.7,leading=17.5,spaceBefore=10,spaceAfter=8,keepWithNext=True,textColor=BLACK),
 'caption':ParagraphStyle('caption',fontName='T',fontSize=11.3,leading=15,spaceBefore=5,spaceAfter=8,alignment=TA_CENTER,textColor=BLACK),
 'small':ParagraphStyle('small',fontName='T',fontSize=9.4,leading=12.5,spaceAfter=7,textColor=BLACK),
 'cell':ParagraphStyle('cell',fontName='T',fontSize=11.3,leading=14.3,textColor=BLACK),
 'cellc':ParagraphStyle('cellc',fontName='T',fontSize=12,leading=15,alignment=TA_CENTER,textColor=BLACK),
 'toc':ParagraphStyle('toc',fontName='TB',fontSize=12,leading=17,textColor=BLACK),
 'tocr':ParagraphStyle('tocr',fontName='T',fontSize=12,leading=17,alignment=TA_RIGHT,textColor=BLACK),
}
story=[];table_number=0

def p(text,style='body'):story.append(Paragraph(text,styles[style]))
def h(text):story.append(Paragraph(text,styles['h2']))
def page(title):
 if story:story.append(PageBreak())
 PAGE_HEADINGS.append(title);story.append(Paragraph(title,styles['h1']))
def source(*paths):p('Minh chứng: '+escape('; '.join(paths))+'.','small')
def table(title,headers,rows,widths=None,center=False,padding=5):
 global table_number
 table_number+=1
 caption=Paragraph(f'Bảng {table_number}: '+title,styles['caption'])
 style=styles['cellc' if center else 'cell']
 cells=[[Paragraph('<b>'+escape(str(v))+'</b>',style) for v in headers]]
 cells += [[Paragraph(escape(str(v)).replace('\n','<br/>'),style) for v in row] for row in rows]
 t=Table(cells,colWidths=widths or [CW/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('GRID',(0,0),(-1,-1),.45,GRID),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding)]))
 story.extend([KeepTogether([caption,t]),Spacer(1,9)])
def figure(path,caption,max_height=260):
 from PIL import Image as PI
 raw=(ROOT/path).read_bytes();EVIDENCE[path]=hashlib.sha256(raw).hexdigest()
 with PI.open(ROOT/path) as im:iw,ih=im.size
 scale=min(CW/iw,max_height/ih)
 story.append(KeepTogether([Image(str(ROOT/path),width=iw*scale,height=ih*scale),Paragraph(caption,styles['caption'])]))
def architecture():
 d=Drawing(CW,175);boxw=98;step=(CW-boxw)/3
 rows=[['CSV lịch sử|1.300.086 review','HDFS raw|CSV + checksum','Spark batch|Clean / SQL / ML','HDFS output|Parquet / mô hình'],['Google Play|Review thật','Kafka|3 partition','Spark Streaming|Checkpoint riêng','HDFS live|Snapshot đã kiểm'],['HDFS theo tháng|Lô đã đối soát','Replay riêng|Copy + commit','Cube / chỉ mục|Generation','ReviewLens|Tự cập nhật']]
 for labels,y in zip(rows,[125,70,15]):
  for i,label in enumerate(labels):
   x=i*step;d.add(Rect(x,y,boxw,40,fillColor=colors.whitesmoke,strokeColor=colors.gray,strokeWidth=.7))
   for j,line in enumerate(label.split('|')):d.add(String(x+boxw/2,y+25-j*12,line,fontName='T',fontSize=9.2,textAnchor='middle'))
   if i<3:
    a=x+boxw+2;b=(i+1)*step-2;d.add(Line(a,y+20,b,y+20,strokeColor=colors.gray));d.add(Polygon([b,y+20,b-4,y+22,b-4,y+18],fillColor=colors.gray))
 story.append(d)

# Page 1: same institutional information and member table as the supplied template.
PAGE_HEADINGS.append('BÁO CÁO TIẾN ĐỘ ĐỒ ÁN BIGDATA')
p('TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH','center')
p('KHOA CÔNG NGHỆ THÔNG TIN','center')
p('BÁO CÁO TIẾN ĐỘ ĐỒ ÁN BIGDATA','title')
p('Phát hiện các khía cạnh gây không hài lòng của khách hàng từ dữ liệu phản hồi trên các sàn thương mại điện tử tại Việt Nam','topic')
p('Giảng viên: '+TEACHER,'center')
p('Thời điểm báo cáo: '+NOW.strftime('%d/%m/%Y'),'center')
table('Thành viên thực hiện',['MSSV','Họ và tên','Lớp'],MEMBERS,[94,222,CW-316],center=True)
story.append(Paragraph('1 MỤC TIÊU VÀ PHẠM VI',styles['h1']))
p('Nhóm đã triển khai CSV -> HDFS -> Spark và điều phối bằng Airflow; đồng thời bổ sung nguồn Google Play thật qua Kafka, mô hình LR/SVM và ReviewLens tự cập nhật. Báo cáo cập nhật kết quả có minh chứng đến ngày 15/10/2026.')
p('Mục tiêu là thống kê review sao thấp theo nền tảng/thời gian, nhận diện khía cạnh được nhắc và thử dự đoán nhóm sao từ văn bản. Kết quả phải liên kết được với mã, lệnh, log và số đếm đối soát; không chỉ dựa vào ảnh giao diện.')
p('Đơn vị quan sát là review ứng dụng Google Play của Shopee, Lazada, Sendo và Tiki. Nguồn lịch sử kết thúc 08/2022; nguồn thu thập thật được tách riêng. Khía cạnh theo luật và nhãn sao thay thế chưa chứng minh nguyên nhân khách quan hoặc cảm xúc tại từng khía cạnh.')

# Page 2: table of contents follows the same ten sections and five-week structure.
page('MỤC LỤC')
contents=[('1 MỤC TIÊU VÀ PHẠM VI',1),('2 NGUỒN VÀ CẤU TRÚC DỮ LIỆU',3),('3 KIẾN TRÚC HỆ THỐNG',4),('4 NỘI DUNG ĐÃ TRIỂN KHAI',5),('5 MINH CHỨNG HDFS VÀ XỬ LÝ BATCH',6),('6 MINH CHỨNG KAFKA VÀ AIRFLOW',7),('7 KẾT QUẢ PHÂN TÍCH HIỆN TẠI',8),('8 SẢN PHẨM REVIEWLENS VÀ KIỂM TRA HIỆN TẠI',9),('9 KHÓ KHĂN, PHẦN CHƯA HOÀN THÀNH VÀ KẾ HOẠCH TIẾP',10),('9.1 Phần chưa hoàn thành',10),('9.2 Kế hoạch hoàn thiện',10),('10 PHÂN CÔNG VÀ LỘ TRÌNH TRONG NĂM TUẦN',11),('10.1 Tuần 1: Khảo sát bài toán và chuẩn bị môi trường',11),('10.2 Tuần 2: Lưu trữ và làm sạch dữ liệu bằng Spark',11),('10.3 Tuần 3: Phân tích và tạo kết quả có thể kiểm chứng',12),('10.4 Tuần 4: Streaming và điều phối quy trình',12),('10.5 Tuần 5: Tích hợp sản phẩm và chuẩn bị nộp bài',13)]
t=Table([[Paragraph(escape(title),styles['toc']),Paragraph(str(number),styles['tocr'])] for title,number in contents],colWidths=[CW-25,25],hAlign='LEFT')
t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.append(t)

# Page 3.
page('2 NGUỒN VÀ CẤU TRÚC DỮ LIỆU')
p('Nguồn lịch sử là Vietnamese E-commerce Review trên Kaggle, tác giả hienbm. CSV UTF-8 có header và trường nhiều dòng; số review được đếm bằng parser CSV và Spark, không dùng số dòng văn bản thay số record.')
table('Quy mô và phạm vi nguồn lịch sử',['Chỉ số','Giá trị'],[['Dung lượng',N(audit['source_bytes'])+' byte, khoảng '+D(audit['source_bytes']/1048576)+' MiB'],['Record CSV',N(audit['csv_records'])],['Thời gian','10/06/2013 đến 27/08/2022'],['Nền tảng','Shopee, Lazada, Sendo, Tiki'],['Trường chính','appid, reviewid, content, score, at']],[105,CW-105])
table('Các trường CSV và cách sử dụng',['Trường','Ý nghĩa và cách xử lý'],[['csv_index','Chỉ số xuất CSV; không làm khóa'],['reviewid, appid','Mã review và ứng dụng; khóa khử trùng'],['username, userimage','Tên/avatar; bỏ khỏi dữ liệu phân tích'],['content','Giữ văn bản gốc và bản chuẩn hóa'],['score','Ép integer; kiểm tra sao 1-5'],['thumbsupcount','Lượt hữu ích; không phải giá trị đơn hàng'],['reviewcreatedversion','Phiên bản ứng dụng'],['at','Parse timestamp, tạo year/month'],['replycontent, repliedat','Phản hồi nhà phát triển; không làm nhãn']],[135,CW-135],padding=4)
p('Nguồn mới dùng google-play-scraper lấy tối đa 100 review/app/lượt, mỗi 5 phút. Event JSON có event_id, review_id, appid, content, score, event_time, ingested_at, source_mode, source_url và poll_id. Snapshot đối chiếu có 407 review, không phải giới hạn tổng lưu trữ.','plain')
source('https://www.kaggle.com/datasets/hienbm/vietnamese-ecommerce-review','artifacts/audit/dataset_profile.json','jobs/collect_live_reviews.py')

# Page 4.
page('3 KIẾN TRÚC HỆ THỐNG')
architecture();p('Hình 1: Kiến trúc lưu trữ, xử lý và phục vụ kết quả','caption')
table('Vai trò và cấu hình thành phần',['Thành phần','Cấu hình và trách nhiệm'],[['HDFS','Hadoop 3.3.6; 1 NameNode, 1 DataNode; raw/processed/output/models/checkpoint; replication=1'],['Spark','3.5.7 standalone; hai worker, mỗi worker 1 core/1 GiB theo cấu hình low-memory; batch, SQL, ML và streaming'],['Kafka','3.9.0 KRaft; một broker; topic 3 partition, replication=1; tách topic lịch sử và live'],['Airflow','2.10.5 LocalExecutor; PostgreSQL 16.6; DAG batch 10 task, live 4 task'],['Lớp phục vụ','Cube Spark và SQLite FTS5 tra cứu toàn tập; generation dùng để đối soát snapshot'],['ReviewLens','Python + HTML/CSS/JS; localhost:8090; bộ lọc tự áp dụng và đồ thị nạp dần']],[85,CW-85],padding=4)
p('Các container chạy trong WSL Ubuntu trên một máy Windows. Đây là mô hình học tập phân tán theo tiến trình, chưa phải cụm nhiều máy có HA. Replication bằng 1 không có bản sao dự phòng khi mất DataNode/broker.')
p('HDFS là kho dữ liệu xử lý; SQLite chỉ phục vụ tra cứu đầu ra. Airflow điều phối dependency/lịch/retry; Kafka vận chuyển event; Spark làm sạch và tổng hợp. Replay lịch sử nạp theo tháng được ghi rõ là demo riêng, không thay nguồn review thật.')
source('compose.yaml','compose.low-memory.yaml','infra/Dockerfile','dags/ecommerce_pipeline.py','dags/live_reviews_pipeline.py')

# Page 5.
page('4 NỘI DUNG ĐÃ TRIỂN KHAI')
table('Tiến độ theo các bước thực hành',['Bước','Thành phần','Kết quả và minh chứng'],[['1','Chuẩn bị HDFS','Tạo raw, processed, quarantine, output, models, checkpoints; có log kiểm tra.'],['2','Upload dữ liệu','CSV gốc khớp SHA-256; kiểm tra 5 block HDFS.'],['3','Đọc bằng Spark','Đọc HDFS đúng 1.300.086 record; schema tường minh, multiLine.'],['4','Làm sạch','74 quarantine, 139 bản sao ID; Parquet platform/year; 1.299.873 khóa duy nhất.'],['5','Spark SQL','Bảng theo nền tảng, tháng, sao và khía cạnh; có explain/query plan.'],['6','Khía cạnh/K-Means','7 khía cạnh theo luật; TF-IDF, K=8 trên 61.241 vector của mẫu hash.'],['6b','ML dự đoán nhóm sao','LR/SVM; split nhóm văn bản; chọn trên validation, test riêng, so baseline.'],['7','Lưu và phục vụ','Cube lịch sử 1.910 ô; chỉ mục 1.299.873 review cùng generation.'],['8','Kafka ingest','Replay lịch sử và producer review thật tách topic; consumer lưu HDFS, có checkpoint.'],['9','Airflow DAG','Run batch validation_20261015: 10/10 task success; live 4/4 task success.']],[43,95,CW-138],padding=4)
p('Các chức năng bổ sung: nguồn thật theo lịch 5 phút, thay phiên bản review sửa đổi, Clear trả về toàn bộ phạm vi, tự lọc/tìm kiếm và đồ thị trượt bốn nền tảng. Replay các tháng lịch sử đã đọc lại HDFS và đối soát đủ 1.299.873 dòng.','plain')
p('Các chức năng kỹ thuật đã có output và kiểm chứng. Mục tiêu phân tích khía cạnh còn giới hạn vì chưa có nhãn người đọc; không báo cáo hoàn thành 100% hoặc suy đóng góp cá nhân chỉ từ bảng phân công.','plain')
source('outputs/demo_evidence.json','outputs/sentiment_evaluation.json','outputs/live_dashboard_validation.json','outputs/replay_browser_validation.json')

# Page 6.
page('5 MINH CHỨNG HDFS VÀ XỬ LÝ BATCH')
table('Block thật của file raw HDFS',['Block','Số byte','Replica'],[[i,N(134217728 if i<4 else 106097069),1] for i in range(5)],[70,245,CW-315],center=True,padding=4)
p('Lệnh hdfs fsck ghi HEALTHY, không có block thiếu/hỏng. Tổng năm block bằng 642.967.981 byte. Mỗi block có một replica trên DataNode; đây không phải minh chứng chịu lỗi nhiều node.')
table('Đối soát số dòng sau làm sạch',['Thành phần','Record','Diễn giải'],[['Raw',N(quality['raw_rows']),'Khớp audit và count Spark'],['Quarantine',N(quality['quarantined_rows']),'72 nội dung rỗng sau chuẩn hóa + 2 sao=0'],['Bản sao ID',N(quality['duplicate_valid_id_rows_removed']),'Khóa appid + reviewid'],['Processed',N(quality['clean_rows']),'Đọc lại HDFS: số dòng = số khóa duy nhất']],[86,81,CW-167],padding=4)
p('Phương trình đối soát: 1.300.086 = 74 + 139 + 1.299.873. Raw ban đầu có 71 nội dung rỗng; một chuỗi chỉ có ký tự vô hình trở thành rỗng sau chuẩn hóa, nên có 72. Review khác ID nhưng trùng câu ngắn vẫn được giữ.')
p('CSV nhiều dòng được đọc một partition trước khi repartition(8); 5 block HDFS không tự tạo 5 task parse CSV. Parquet theo platform/year hỗ trợ partition pruning; query plan có PartitionFilters, ReadSchema và Exchange.')
p('<b>Lệnh đối chiếu:</b> hdfs dfs -ls -h /ecommerce/raw; hdfs dfsadmin -report; hdfs fsck /ecommerce/raw/reviews.csv -files -blocks -locations. Browser: http://localhost:9870 -> Utilities -> Browse the file system.','plain')
source('outputs/logs/hdfs_blocks_20261015.txt','outputs/logs/hdfs_raw_sha256_20261015.txt','outputs/persisted_validation.json','outputs/spark_query_plan.txt')

# Page 7.
page('6 MINH CHỨNG KAFKA VÀ AIRFLOW')
table('Kafka lịch sử và nhánh thu thập thật',['Chỉ số','Kết quả'],[['Replay lịch sử','2 lượt, mỗi lượt 1.000 review; tổng 2.000 offsets; HDFS còn 1.000 khóa duy nhất.'],['Checkpoint/dedup','6 microbatch, 3 batch không có event mới; tiến độ và state được giữ qua các lượt.'],['Nguồn thật','Google Play -> ecommerce-live-reviews -> HDFS; mỗi 5 phút, tối đa 100/app/lượt.'],['Snapshot đối chiếu','407 review; run live 4/4 task success lúc khoảng 08:05-08:06 ngày 15/10/2026.']],[108,CW-108],padding=3)
p('Review mới/sửa tạo event phiên bản; publisher chọn bản mới nhất theo review_key. Không có review mới/sửa thì số đếm giữ nguyên. availableNow xử lý hữu hạn rồi kết thúc để Airflow chạy bước publish/verify.','plain')
table('DAG batch validation_20261015',['STT','Task ID','Trạng thái'],[[i+1,t['task_id'],'Success'] for i,t in enumerate(evidence['airflow']['tasks'])],[32,309,CW-341],padding=3)
p('DAG live có 4 bước: collect_real_reviews -> kafka_to_hdfs -> publish_verified_snapshot -> verify_live_results; catchup=False, max_active_runs=1, retry một lần. Checkpoint live tách khỏi replay; chưa tuyên bố exactly-once toàn hệ thống trong mọi tình huống lỗi.','plain')
source('dags/ecommerce_pipeline.py','dags/live_reviews_pipeline.py','outputs/demo_evidence.json','outputs/logs/live_airflow_tasks','outputs/live_dashboard_validation.json')

# Page 8.
page('7 KẾT QUẢ PHÂN TÍCH HIỆN TẠI')
table('Review sau làm sạch theo nền tảng',['Nền tảng','Review','Review 1-2 sao','Tỷ lệ'],[[name,N(by_platform[name]['reviews']),N(by_platform[name]['low_rating_reviews']),pc(by_platform[name]['low_rating_rate'])] for name in order]+[['Toàn tập',N(quality['clean_rows']),N(low),pc(low/quality['clean_rows'])]],[78,104,139,CW-321],padding=4)
figure('outputs/report_charts/01_platform_low_rating.png','Hình 2: Tỷ lệ review sao thấp theo nền tảng',185)
p(f'Bộ luật gán ít nhất một đề cập cho {N(matched)} review sao thấp ({pc(matched/low)}); còn {N(unmapped)} chưa gán. Ba khía cạnh nhiều đề cập nhất là ứng dụng {N(by_aspect["app"])}, vận chuyển {N(by_aspect["delivery"])} và sản phẩm {N(by_aspect["product"])}. Một review có thể nhắc nhiều khía cạnh.')
p(f'K-Means: K=8 trên {N(cluster["training_rows"])} vector; silhouette cosine {D(cluster["silhouette_cosine"],5)}, phân tách yếu. Baseline dự đoán nhóm sao chọn Logistic Regression: test accuracy {pc(ml["test"]["accuracy"])}, F1 sao thấp {D(ml["test"]["f1_negative"],4)}; majority baseline accuracy 73,63%, F1 sao thấp bằng 0.')
p('Split train/validation/test: 54.818/3.105/12.993 dòng, chia theo nhóm nội dung để tránh cùng văn bản lọt nhiều tập. Nhãn sao là proxy; metric này không phải F1 nhận diện khía cạnh hoặc chứng minh cảm xúc thực.','plain')
source('outputs/platform_summary.csv','outputs/aspect_mentions.csv','outputs/cluster_metadata.json','outputs/sentiment_evaluation.json')

# Page 9.
page('8 SẢN PHẨM REVIEWLENS VÀ KIỂM TRA HIỆN TẠI')
figure('outputs/screenshots/14-four-platform-replay-20261015.png','Hình 3: ReviewLens và đồ thị nạp dần của bốn nền tảng',235)
p('ReviewLens có Tổng quan, Khía cạnh, Tra cứu phản hồi, Luồng dữ liệu và Đồ thị nạp dần. Bộ lọc tự áp dụng; tìm kiếm tự chạy khi nhập; tổng quan tự kiểm tra snapshot mới mỗi 10 giây, giữ lựa chọn và bỏ response cũ.')
p('Snapshot nguồn gộp được đối chiếu: 1.299.873 lịch sử + 407 live - 6 khóa trùng = 1.300.274 review. Bản live thay bản lịch sử trùng ID; 1.972 ô tổng hợp x 9 số đếm khớp phép kiểm độc lập. Clear xóa điều kiện, trở về toàn bộ thời gian, không dừng ở 400 review preview.')
p('Đồ thị nạp dần mặc định cả bốn nền tảng, cửa sổ trượt 12 tháng. Replay copy lô tháng thật sang vùng HDFS run riêng; cuối lượt đối soát đủ 1.299.873 dòng. Nút chuyển xem nguồn thật dùng các mốc thu thập đã kiểm chứng; không có thay đổi thì đường có thể phẳng.')
p('Các số trên thuộc snapshot bất biến lúc 08:06 ngày 15/10/2026, generation '+live_gen+'. Pipeline thật có thể tiếp tục tăng sau mốc này; báo cáo không coi snapshot là số đếm trực tiếp tại lúc đọc.','small')
source('outputs/clear_filters_validation.json','outputs/combined_source_validation.json','outputs/replay_browser_validation.json','outputs/replay_restart_validation.json')

# Page 10.
page('9 KHÓ KHĂN, PHẦN CHƯA HOÀN THÀNH VÀ KẾ HOẠCH TIẾP')
table('Khó khăn đã gặp và cách xử lý',['Vấn đề','Cách xử lý và bằng chứng'],[['CSV nhiều dòng / Unicode','multiLine, schema rõ; phân biệt 71 rỗng raw và 72 sau chuẩn hóa.'],['Tài nguyên / quyền ghi','Chạy WSL Linux, cấu hình low-memory; tệp tạm và thay thế nguyên tử.'],['Cube và chỉ mục lệch','Đối soát mọi ô và generation trước công bố; kiểm tra nguồn gộp.'],['Clear chỉ thấy mẫu','Xóa toàn bộ điều kiện, tra cứu trên chỉ mục đầy đủ; có browser check.'],['Review mới ít hoặc sửa','Lưu tích lũy, chọn phiên mới; không bơm lặp review để tăng tổng.'],['Đồ thị quá dày','Cửa sổ 12 mốc; tách replay lịch sử và timeline thu thập thật.']],[105,CW-105],padding=3)
h('9.1 Phần chưa hoàn thành')
p('Mẫu 1.000 review chưa có nhãn người đọc độc lập để đánh giá F1 khía cạnh. Cần gán nhãn và phân xử bất đồng; 55,95% sao thấp chưa gán không đồng nghĩa không có vấn đề.')
p('Chưa benchmark nhiều máy, thử mất node hoặc state retention dài hạn. Nguồn thật chỉ lấy cửa sổ 100/app/lượt. Chưa có log đơn hàng để xác minh nguyên nhân; chưa fine-tune PhoBERT.')
h('9.2 Kế hoạch hoàn thiện')
p('Ưu tiên nhãn độc lập, phân tích lỗi, cải thiện luật/mô hình và thử khôi phục. Tập demo có source-lệnh-log-output; giữ dữ liệu gốc, checkpoint và bằng chứng trước khi chạy lại.')
p('Đã có kiểm thử runtime, browser, Clear và restart replay. Trước khi nộp, xác nhận nhật ký cá nhân; kiểm tra PDF/source/README/log/ảnh/Git và loại bí mật. Commit tự động không thay bằng chứng đóng góp cá nhân.','plain')
source('docs/ANNOTATION_GUIDE.md','docs/IMPLEMENTATION_JOURNAL.md','docs/MEMBER_TASK_AUDIT.md','outputs/replay_restart_validation.json')

# Page 11: preserve the member responsibility plan from the template, label it as a plan.
page('10 PHÂN CÔNG VÀ LỘ TRÌNH TRONG NĂM TUẦN')
p('Nhóm tổ chức năm tuần theo mốc tương đối, mỗi người phụ trách một gói chính và rà soát chéo mỗi tuần. Tỷ trọng dự kiến bằng nhau, mỗi người 1/3; đây là kế hoạch trách nhiệm, không phải số giờ hoặc mức đóng góp cá nhân đã xác nhận.')
h('10.1 Tuần 1: Khảo sát bài toán và chuẩn bị môi trường')
table('Phân công tuần 1',['Thành viên','Công việc chính','Đầu ra kiểm chứng'],[['Huỳnh Quang Sang','Xác định câu hỏi phân tích, phạm vi và chỉ số sao thấp.','Đề cương, định nghĩa mẫu số và giới hạn nguồn.'],['Phan Đức Thể','Khảo sát schema CSV, số record, rỗng và trùng.','Script audit, hồ sơ dữ liệu và SHA-256.'],['Đỗ Trọng Vĩ','Chuẩn bị Docker Compose, HDFS và Spark hai worker.','Cấu hình dịch vụ, worker và kiểm tra HDFS.']],[95,166,CW-261],padding=5)
h('10.2 Tuần 2: Lưu trữ và làm sạch dữ liệu bằng Spark')
table('Phân công tuần 2',['Thành viên','Công việc chính','Đầu ra kiểm chứng'],[['Huỳnh Quang Sang','Tạo vùng HDFS, upload raw và kiểm tra block.','Bootstrap, fsck và checksum nguồn.'],['Phan Đức Thể','Đọc CSV nhiều dòng, chuẩn hóa, tách quarantine.','PySpark, reason lỗi, count raw/quarantine.'],['Đỗ Trọng Vĩ','Khử trùng ID, ghi Parquet và đối soát số dòng.','Window dedup, partition platform/year, unique key.']],[95,166,CW-261],padding=5)
p('Rà soát chéo: Sang kiểm tra gói của Thể; Thể kiểm tra gói của Vĩ; Vĩ kiểm tra gói của Sang. Hai tuần đầu chốt hợp đồng dữ liệu và đối soát raw trước phân tích.','plain')
p('Các đầu ra kỹ thuật đã có trong dự án không tự xác nhận người thực hiện. Khi nghiệm thu nội bộ, từng người ghi ngày, file/commit, lệnh chạy, kết quả và xác nhận rà soát; không tạo lịch sử hồi tố.','small')

# Page 12.
page('10.3 Tuần 3: Phân tích và tạo kết quả có thể kiểm chứng')
table('Phân công tuần 3',['Thành viên','Công việc chính','Đầu ra kiểm chứng'],[['Huỳnh Quang Sang','Spark SQL theo nền tảng, thời gian và số sao.','Bảng thống kê, mẫu số và explain.'],['Phan Đức Thể','Luật đề cập bảy khía cạnh; rà soát phần chưa gán.','Cấu hình luật, bảng đề cập, độ bao phủ và mẫu nhãn.'],['Đỗ Trọng Vĩ','TF-IDF/K-Means; bổ sung baseline LR/SVM và split nhóm.','Model HDFS, silhouette, metric validation/test, kiểm tra leakage.']],[95,166,CW-261],padding=5)
h('10.4 Tuần 4: Streaming và điều phối quy trình')
table('Phân công tuần 4',['Thành viên','Công việc chính','Đầu ra kiểm chứng'],[['Huỳnh Quang Sang','Kafka topic/producer; replay lịch sử và collector review thật.','Topic tách riêng, event ID ổn định, poll/producer log.'],['Phan Đức Thể','Structured Streaming, checkpoint, dedup và phiên bản review.','Microbatch, dữ liệu HDFS, số unique và kiểm tra review sửa.'],['Đỗ Trọng Vĩ','DAG batch/live, dependency, retry và quyền ghi.','Batch 10 task, live 4 task; log theo run ID và kiểm đầu ra.']],[95,166,CW-261],padding=5)
p('Tiêu chí cuối tuần 3: thống kê có mẫu số; giải thích SQL, split/feature/metric và giới hạn khía cạnh. Tiêu chí cuối tuần 4: replay không tăng unique sai, checkpoint khôi phục tiến độ và nguồn thật không bị thay bằng dữ liệu mô phỏng.')
p('Hệ thống đã có hai nhánh lịch sử và thu thập thật. Các gói phụ trách được cập nhật theo tính năng mới; các thành viên cần tự chạy và giải thích gói phụ trách, kèm bằng chứng cá nhân thực tế.','plain')

# Page 13.
page('10.5 Tuần 5: Tích hợp sản phẩm và chuẩn bị nộp bài')
table('Phân công tuần 5',['Thành viên','Công việc chính','Đầu ra kiểm chứng'],[['Huỳnh Quang Sang','Cube, chỉ mục, hợp nhất nguồn và đối soát lớp phục vụ.','Cube/index cùng generation; kiểm total/unique và dữ liệu gộp.'],['Phan Đức Thể','Biểu đồ, bộ lọc tự động, Clear và đồ thị nạp dần.','ReviewLens, ảnh demo, kiểm browser và xuất CSV/SVG.'],['Đỗ Trọng Vĩ','Báo cáo, source/log, nhật ký và kịch bản bảo vệ.','PDF tiến độ, README, ZIP minh chứng và giải thích HDFS/Kafka/Airflow.']],[95,166,CW-261],padding=5)
table('Cân bằng khối lượng theo kế hoạch',['Thành viên','Gói chính','Rà soát chéo','Tỷ trọng'],[['Huỳnh Quang Sang',5,5,'1/3'],['Phan Đức Thể',5,5,'1/3'],['Đỗ Trọng Vĩ',5,5,'1/3']],[160,78,108,CW-346],center=True,padding=5)
p('Cuối mỗi tuần, nhóm đối chiếu đầu ra và kiểm tra chéo code/kết quả. Khi một gói phát sinh lỗi hạ tầng hoặc xử lý phức tạp, nhóm điều chỉnh phần hỗ trợ để cân bằng; không chỉ chia theo số dòng code hoặc số trang báo cáo.')
p('Bộ nộp gồm PDF tiến độ, source hoặc repository, README và minh chứng HDFS/Spark/Kafka/Airflow, dashboard, Git history và nhật ký. CSV gốc, SQLite, volumes và .env không đóng gói; dataset tải lại từ Kaggle theo README.')
p('HDFS: localhost:9870; Spark: localhost:8081; Airflow: localhost:8080; ReviewLens: localhost:8090. Khi demo phải mở đúng run/generation và đối chiếu log, không dùng ảnh đơn lẻ để kết luận pipeline đang hoạt động.','plain')
p('Năm tuần là lộ trình tương đối, chưa gán ngày bắt đầu hoặc hồi tố thành lịch sử làm việc; đóng góp cá nhân cần nhóm xác nhận.','small')
source('README.md','docs/IMPLEMENTATION_JOURNAL.md','docs/PHAN_CONG_GOC.txt','outputs/submission_validation.json')

class NumberedCanvas(canvas.Canvas):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.states=[]
 def showPage(self):self.states.append(dict(self.__dict__));self._startPage()
 def save(self):
  total=len(self.states)
  for state in self.states:
   self.__dict__.update(state);self.saveState();self.setFont('T',10.5)
   self.drawCentredString(W/2,31,f'Trang {self._pageNumber} / {total}');self.restoreState();super().showPage()
  super().save()

DEST.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(DEST),pagesize=A4,leftMargin=99,rightMargin=71,topMargin=68,bottomMargin=60,title='Bao cao tien do do an Bigdata - ReviewLens',author='Huynh Quang Sang; Phan Duc The; Do Trong Vi',subject='Progress report based on verified project evidence')
doc.build(story,canvasmaker=NumberedCanvas)
from pypdf import PdfReader
reader=PdfReader(DEST);texts=[page.extract_text() or '' for page in reader.pages]
checks={'page_count_13':len(texts)==13,'all_planned_headings_on_correct_page':len(texts)==13 and all(''.join(title.split()) in ''.join(text.split()) for title,text in zip(PAGE_HEADINGS,texts)),'identity_matches_template':all(value in texts[0] for row in MEMBERS for value in row) and TEACHER in texts[0],'unicode_text_valid':all(chr(0) not in text and chr(65533) not in text for text in texts)}
from validate_final_report import secret_values,compact
values,_=secret_values();raw=DEST.read_bytes();all_text='\n'.join(texts)
checks['local_secret_values_absent']=not any(value.encode() in raw or value in all_text or compact(value) in compact(all_text) for value in values)
for path in ['jobs/batch_pipeline.py','jobs/collect_live_reviews.py','jobs/stream_reviews.py','jobs/train_sentiment.py','dags/ecommerce_pipeline.py','dags/live_reviews_pipeline.py','compose.yaml','compose.low-memory.yaml']:
 EVIDENCE[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
manifest={'created_local':NOW.isoformat(),'pdf':str(DEST.relative_to(ROOT)),'pdf_sha256':hashlib.sha256(raw).hexdigest(),'template':'01_Bao_cao_tien_do.pdf','template_sha256':hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'teacher':TEACHER,'members':[{'mssv':row[0],'name':row[1],'class':row[2]} for row in MEMBERS],'historical_generation':combined['generation'].split(':')[0],'live_generation':live_gen,'live_reviews':live['processed_rows'],'combined_reviews':combined['total_reviews'],'evidence_hashes':EVIDENCE,'planned_page_headings':PAGE_HEADINGS,'checks':checks,'individual_contribution_status':'Responsibility plan; personal contribution not independently verified','visual_review_complete':False}
(DEST.parent/'progress_report_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pdf':str(DEST),'pages':len(texts),'bytes':len(raw),'checks':checks},ensure_ascii=False))
if not all(checks.values()):
 for i,text in enumerate(texts,1):print(i,len(text),repr(text[:110]))
 raise SystemExit('Report requires layout/content correction before delivery')
