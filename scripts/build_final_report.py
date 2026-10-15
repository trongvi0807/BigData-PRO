"""Vietnamese PDF from immutable evidence and exact repository source."""
import ast,csv,hashlib,json,re,subprocess,textwrap
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Table,TableStyle,Preformatted,XPreformatted,Image,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'output/pdf/Bao_cao_Big_Data_ReviewLens.pdf'
NOW=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'));SOURCES={};ARTIFACTS={}
def content(path):
 raw=(ROOT/path).read_bytes();SOURCES[path]=hashlib.sha256(raw).hexdigest();return raw.decode('utf-8-sig')
def J(path):
 raw=(ROOT/path).read_bytes();ARTIFACTS[path]=hashlib.sha256(raw).hexdigest();return json.loads(raw.decode('utf-8-sig'))
def CSV(path):
 raw=(ROOT/path).read_bytes();ARTIFACTS[path]=hashlib.sha256(raw).hexdigest();return list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
def N(n):return f'{int(n):,}'.replace(',','.')
def D(n,k=2):return f'{float(n):.{k}f}'.replace('.',',')
def PCT(n):return D(100*float(n))+'%'
def local(v):return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%H:%M:%S %d/%m/%Y')
audit=J('artifacts/audit/dataset_profile.json');quality=J('outputs/data_quality.json')
ml=J('outputs/sentiment_evaluation.json');cluster=J('outputs/cluster_metadata.json')
evidence=J('outputs/demo_evidence.json');persisted=J('outputs/persisted_validation.json')
dash=J('outputs/dashboard_validation.json');dash_meta=J('outputs/dashboard_preparation.json')
live_browser=J('outputs/live_dashboard_validation.json');live_gen=live_browser['generation']
live_meta=J('outputs/live/generations/'+live_gen+'/dashboard_preparation.json')
live_quality=J('outputs/live/generations/'+live_gen+'/data_quality.json')
combined=J('outputs/combined_source_validation.json');clear=J('outputs/clear_filters_validation.json');assert combined['generation']==clear['generation']
replay=J('outputs/replay/validation_054f7512feb1480c9d389ae11f4071e1.json')
replay_browser=J('outputs/replay_browser_validation.json');restart=J('outputs/replay_restart_validation.json')
platforms=CSV('outputs/platform_summary.csv');aspects=CSV('outputs/aspect_mentions.csv');unmatched=CSV('outputs/unmatched_low_ratings.csv')
rows={r['platform']:r for r in platforms};order=['Shopee','Lazada','Sendo','Tiki'];config=json.loads(content('config/aspects.json'))
git_rows=subprocess.check_output(['git','log','--date=iso-strict','--format=%h|%ad|%an|%s'],cwd=ROOT,text=True).strip().splitlines()
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Italic','DejaVuSans-Oblique.ttf'),('Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
INK=colors.HexColor('#193c49');TEAL=colors.HexColor('#16776d');GRAY=colors.HexColor('#657984');LIGHT=colors.HexColor('#eff5f4')
styles={'body':ParagraphStyle('Body',fontName='Body',fontSize=9.6,leading=15,spaceAfter=7,allowWidows=0,alignment=TA_JUSTIFY,textColor=INK),'h1':ParagraphStyle('H1',fontName='Bold',fontSize=17,leading=23,spaceBefore=6,spaceAfter=14,textColor=INK,keepWithNext=True),'h2':ParagraphStyle('H2',fontName='Bold',fontSize=12,leading=17,spaceBefore=13,spaceAfter=8,textColor=TEAL,keepWithNext=True),'small':ParagraphStyle('Small',fontName='Body',fontSize=7.8,leading=11.5,spaceAfter=6,textColor=GRAY),'table':ParagraphStyle('Table',fontName='Body',fontSize=8.1,leading=12,textColor=INK),'code':ParagraphStyle('Code',fontName='Mono',fontSize=7.4,leading=10.2,spaceBefore=4,spaceAfter=8,backColor=colors.HexColor('#f4f7f8'),borderPadding=7),'toc':ParagraphStyle('TOC',fontName='Body',fontSize=9.1,leading=12.5,spaceBefore=1.5,textColor=INK),'cover':ParagraphStyle('Cover',fontName='Bold',fontSize=25,leading=35,textColor=INK,spaceAfter=20),'subcover':ParagraphStyle('Subcover',fontName='Body',fontSize=12,leading=19,textColor=TEAL,spaceAfter=16)}
W,H=A4;CW=W-96;story=[];chapter_index=0;snippets=[]
def p(text,style='body'):story.append(Paragraph(text,styles[style]))
def h(text):story.append(Paragraph(text,styles['h2']))
def chapter(text,new_page=True):
 global chapter_index
 if story and new_page:story.append(PageBreak())
 chapter_index+=1;node=Paragraph(text,styles['h1']);node.bookmark='chapter'+str(chapter_index);story.append(node)
def table(headers,data,widths=None):
 cells=[[Paragraph('<b>'+escape(str(v))+'</b>',styles['table']) for v in headers]]
 cells += [[Paragraph(escape(str(v)).replace('\n','<br/>'),styles['table']) for v in row] for row in data]
 t=Table(cells,colWidths=widths or [CW/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.8,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#dce6e8')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.extend([t,Spacer(1,10)])
def cite(paths):p('Đối chiếu: '+escape(' | '.join(paths)), 'small')
def block(text,numbered=False):
 lines=[]
 for number,line in enumerate(text.splitlines(),1):
  width=96 if numbered else 100;prefix=f'{number:03d}  ' if numbered else ''
  pieces=textwrap.wrap(line.expandtabs(4),width=width,replace_whitespace=False,drop_whitespace=False,break_long_words=True,break_on_hyphens=False) or ['']
  lines.append(prefix+pieces[0]);lines.extend(('  |  ' if numbered else '   | ')+v for v in pieces[1:])
 rendered='\n'.join(lines)
 mono_chars=pdfmetrics.getFont('Mono').face.charWidths
 body_chars=pdfmetrics.getFont('Body').face.charWidths
 missing={char for char in rendered if not char.isspace() and ord(char) not in body_chars}
 if missing:raise ValueError('Unsupported code glyphs: '+repr(missing))
 markup=''.join(escape(char) if char.isspace() or ord(char) in mono_chars else '<font name="Body">'+escape(char)+'</font>' for char in rendered)
 story.append(XPreformatted(markup,styles['code']))
def shell(text):
 """Wrap commands at unquoted spaces with executable shell continuations."""
 lines=[]
 for original in text.splitlines():
  line=original.lstrip()
  if line.startswith('#'):
   lines.extend(textwrap.wrap(line,width=95,subsequent_indent='# ') or ['#']);continue
  while len(line)>95:
   quote=None;escaped=False;spaces=[]
   for i,char in enumerate(line):
    if escaped:escaped=False;continue
    if char==chr(92) and quote!=chr(39):escaped=True;continue
    if quote:
     if char==quote:quote=None
    elif char in (chr(34),chr(39)):quote=char
    elif char==' ' and 4<i<93:spaces.append(i)
   if not spaces:break
   at=spaces[-1];lines.append(line[:at].rstrip()+' '+chr(92));line='    '+line[at:].lstrip()
  lines.append(line)
 block(chr(10).join(lines))

def excerpt(path,start,end,explanation):
 source=content(path);selected='\n'.join(source.splitlines()[start-1:end]);block(selected);p(explanation);cite([f'{path}:{start}-{end}']);snippets.append({'file':path,'start':start,'end':end,'sha256':SOURCES[path]})
def function(path,name,explanation):
 source=content(path);node=next(n for n in ast.parse(source).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name);excerpt(path,node.lineno,node.end_lineno,explanation)
def figure(path,caption,height=330):
 from PIL import Image as PI
 raw=(ROOT/path).read_bytes();ARTIFACTS[path]=hashlib.sha256(raw).hexdigest()
 with PI.open(ROOT/path) as im:iw,ih=im.size
 scale=min(CW/iw,height/ih);image=Image(str(ROOT/path),width=iw*scale,height=ih*scale)
 story.append(KeepTogether([image,Spacer(1,7),Paragraph(caption,styles['small'])]))
def architecture():
 d=Drawing(CW,240)
 def box(x,y,label):
  d.add(Rect(x,y,112,44,rx=5,ry=5,fillColor=LIGHT,strokeColor=TEAL,strokeWidth=.7))
  for i,line in enumerate(label.split('|')):d.add(String(x+56,y+28-i*13,line,fontName='Body',fontSize=8.5,textAnchor='middle',fillColor=INK))
 def arrow(x,y):
  d.add(Line(x,y,x+14,y,strokeColor=GRAY,strokeWidth=1));d.add(Polygon([x+14,y,x+9,y+3,x+9,y-3],fillColor=GRAY,strokeColor=GRAY))
 labels=[['CSV Kaggle|2013 - 08/2022','HDFS raw|CSV + fingerprint','Spark|Clean / SQL / ML','HDFS / API|Parquet / cube'],['Google Play|Thu thập thật','Kafka|3 partition','Spark Streaming|Checkpoint HDFS','HDFS live|Snapshot kiểm tra'],['HDFS prepared|Lô theo tháng','HDFS replay|Copy + commit lô','Snapshot tiến độ|Số đếm thật','Dashboard|Cửa sổ 12 mốc']]
 for row,y in zip(labels,[165,95,25]):
  for i,label in enumerate(row):box(i*128,y,label)
  for i in range(3):arrow(i*128+113,y+22)
 d.add(String(CW/2,225,'AIRFLOW: LỊCH - DEPENDENCY - RETRY - LOG',fontName='Bold',fontSize=9.3,textAnchor='middle',fillColor=TEAL));story.append(d)
class Report(BaseDocTemplate):
 def afterFlowable(self,flowable):
  if isinstance(flowable,Paragraph) and flowable.style.name=='H1':
   name=flowable.getPlainText();key=flowable.bookmark;self.canv.bookmarkPage(key);self.canv.addOutlineEntry(name,key,level=0,closed=False);self.notify('TOCEntry',(0,name,self.page,key))
def page(canvas,doc):
 canvas.saveState();canvas.setStrokeColor(colors.HexColor('#dce6e8'));canvas.line(48,H-33,W-48,H-33);canvas.setFont('Body',8);canvas.setFillColor(GRAY)
 if doc.page>1:canvas.drawString(48,H-26,'ReviewLens | Báo cáo đồ án Big Data')
 canvas.drawString(48,28,'Ngày lập: '+NOW.strftime('%d/%m/%Y')+' | Giờ Việt Nam');canvas.drawRightString(W-48,28,'Trang '+str(doc.page));canvas.restoreState()

# Cover and reading guide
story.extend([Spacer(1,42),Paragraph('BÁO CÁO ĐỒ ÁN BIG DATA',styles['subcover']),Paragraph('REVIEWLENS',styles['cover'])])
p('Phân tích các khía cạnh được nhắc trong phản hồi sao thấp của ứng dụng thương mại điện tử Việt Nam','cover')
p('Hadoop / HDFS - PySpark - Kafka - Airflow<br/>Phân tích dữ liệu, baseline Machine Learning và dashboard tự cập nhật','subcover')
table(['Thông tin hồ sơ','Nội dung'],[['Trường / Lớp','Chưa cung cấp'],['Giảng viên','Chưa cung cấp'],['Thành viên 1 / MSSV','Chưa cung cấp'],['Thành viên 2 / MSSV','Chưa cung cấp'],['Thành viên 3 / MSSV','Chưa cung cấp'],['Ngày lập',NOW.strftime('%d/%m/%Y')+' (giờ Việt Nam)']],[155,CW-155])
p('Báo cáo được dựng từ mã nguồn, bảng kết quả và log thực tế. Dataset lịch sử, review thật và demo nạp lại được phân biệt rõ. Đóng góp cá nhân chưa xác nhận được ghi trung thực.','small')
p('Phiên bản mã đối chiếu: '+escape(commit),'small')
chapter('Tóm tắt và cách đọc báo cáo')
p(f'Dự án sử dụng {N(audit["csv_records"])} review gốc, dung lượng {N(audit["source_bytes"])} byte ({D(audit["source_bytes"]/1048576)} MiB), từ Google Play qua dataset Vietnamese E-commerce Review. Spark đọc CSV trực tiếp từ HDFS, quarantine 74 record và loại 139 bản sao ID; giữ {N(quality["clean_rows"])} review sạch. Phân tích tập trung vào tỷ lệ đánh giá thấp, nền tảng, thời gian và khía cạnh được đề cập.')
p(f'Nhánh thu thập Google Play thật truyền qua Kafka, lưu HDFS, tổng hợp bằng Spark và được Airflow kích hoạt mỗi 5 phút. Snapshot dùng trong báo cáo có {N(live_meta["processed_rows"])} review, generation {live_gen}, công bố lúc {local(live_meta["prepared_utc"])}. Đây là mốc có minh chứng browser/cube; dữ liệu đang chạy có thể tiếp tục thay đổi.')
p(f'Baseline TF-IDF + Logistic Regression/SVM dự đoán nhóm sao thấp/cao từ văn bản. Mô hình chọn có test accuracy {PCT(ml["test"]["accuracy"])} và F1 lớp sao thấp {D(ml["test"]["f1_negative"],4)}. Nhãn 1-2 sao/4-5 sao là nhãn thay thế, không phải cảm xúc được con người xác thực. Hướng phân tích dữ liệu là hướng nghiệm thu chính; ML là phần bổ sung.')
p('Báo cáo gồm kiến trúc, schema, kết quả, mã PySpark có giải thích, lệnh chạy, ma trận minh chứng, nhật ký và câu hỏi bảo vệ. Phụ lục in đầy đủ các file PySpark quan trọng. Ký hiệu | ở đầu dòng tiếp trong khối mã chỉ là bọc dòng bản in; lấy mã thực thi nguyên bản từ repository/ZIP.')
cite(['outputs/demo_evidence.json','outputs/sentiment_evaluation.json','outputs/live_dashboard_validation.json','outputs/combined_source_validation.json'])
chapter('Mục lục')
toc=TableOfContents();toc.levelStyles=[styles['toc']];story.append(toc)
chapter('1. Bài toán, mục tiêu và đối chiếu yêu cầu')
h('1.1 Bài toán thực tế')
p('Review ứng dụng Shopee, Lazada, Sendo và Tiki chứa ý kiến về thao tác ứng dụng, vận chuyển, hàng hóa, hỗ trợ, thanh toán, khuyến mãi và đổi trả. Đọc thủ công toàn bộ khó tái hiện khi số lượng lớn. Pipeline cần lưu trữ, làm sạch, tổng hợp và trình bày tín hiệu để rà soát; đồng thời thử dự đoán nhóm sao từ văn bản.')
p('Mục tiêu phân tích: đếm review và sao thấp theo nền tảng/tháng; tính tỷ lệ 1-2 sao, điểm trung bình, độ bao phủ khía cạnh và độ nhạy khi bỏ ứng viên spam. Mục tiêu dự đoán: phân biệt nhóm 1-2 sao với 4-5 sao, loại sao 3 khỏi huấn luyện. Không kết luận nhân quả hoặc mức hài lòng của toàn bộ khách hàng.')
h('1.2 Phạm vi đúng với nguồn')
p('Đây là đánh giá ứng dụng Google Play, không phải bảng giao dịch hay review từng sản phẩm đã xác nhận mua hàng. Không có ngành hàng, doanh thu hoặc customer ID đáng tin cậy. Tên người viết và avatar không đưa vào dữ liệu phục vụ. Bảy khía cạnh là nhãn đề cập theo luật, chưa có polarity độc lập theo từng khía cạnh.')
table(['Yêu cầu của thầy','Thực hiện và bằng chứng'],[['1. Bài toán / nguồn / schema / số lượng / dung lượng','Mục 1-2; audit_dataset.py; dataset_profile.json và SHA-256.'],['2. HDFS và Kafka cho thu thập liên tục','CSV raw trên HDFS; collector thật -> topic live -> Spark Streaming -> HDFS. Demo batch lịch sử được tách riêng.'],['3. Spark đọc HDFS; clean / transform / SQL','read_raw, enrich, validation_reasons, deduplicate_valid, analyze; Parquet và query plan.'],['4a. Phân tích có bảng / biểu đồ / insight','platform/month/rating/aspect/length/spam CSV; hình và phần nhận xét.'],['4b. ML bổ sung','TF-IDF; chia nhóm; LR/SVM; accuracy, P/R/F1, confusion matrix, baseline.'],['5. Airflow điều phối','DAG batch 10 task, live 4 task, DAG chuẩn bị lô tháng; có run ID và task log.'],['Hồ sơ và dashboard','PDF, source/README, lệnh/log, ảnh demo và đối chiếu generation/cube/index.'],['Nhật ký / đóng góp / secrets','Git và nhật ký mới thật; cá nhân chưa xác nhận; .env không nộp, archive có scan bí mật.']],[137,CW-137])
p('Rubric: kỹ thuật tối đa 7,5 điểm; dashboard tối đa 1,0; minh chứng/tái hiện tối đa 1,5. Báo cáo cung cấp chứng cứ theo nhóm, không tự chấm điểm. Xác nhận đóng góp cá nhân phải được nhóm bổ sung từ thông tin/lịch sử thật.')
chapter('2. Nguồn dữ liệu, định dạng, schema và chất lượng')
h('2.1 Dataset lịch sử')
p('Nguồn: <link href="https://www.kaggle.com/datasets/hienbm/vietnamese-ecommerce-review" color="#16776d">Vietnamese E-commerce Review - Kaggle [T1]</link>. download_dataset.py tải snapshot công khai và chỉ nhận fingerprint đã ghi. CSV UTF-8 có header, quote và review nhiều dòng; record được đếm bằng parser CSV thay vì số dòng vật lý.')
table(['Thuộc tính','Giá trị'],[['Record raw',N(audit['csv_records'])],['Dung lượng',N(audit['source_bytes'])+' byte / '+D(audit['source_bytes']/1048576)+' MiB'],['Số trường','12; cột đầu header rỗng, đặt csv_index khi đọc'],['Ngày nhỏ nhất',audit['date_min']],['Ngày lớn nhất',audit['date_max']],['SHA-256',audit['sha256']],['Quarantine / trùng ID / sạch','74 / 139 / '+N(quality['clean_rows'])]],[138,CW-138])
table(['Trường','Kiểu raw / sau xử lý','Vai trò'],[['csv_index','string','Chỉ số CSV; không dùng làm khóa review'],['reviewid, appid','string','Khóa nguồn và ánh xạ nền tảng'],['content','string','Văn bản gốc và bản chuẩn hóa'],['score','string -> integer','Sao 1-5; sao thấp 1-2'],['at','string -> timestamp','Ngày review; sinh year/month'],['thumbsupcount','string','Lượt hữu ích, không phải doanh thu'],['reviewcreatedversion','string','Phiên bản ứng dụng; có thể thiếu'],['username, userimage','string','Thông tin người viết; không xuất phân tích'],['replycontent, repliedat','string','Phản hồi nhà phát hành; không dùng làm nhãn']],[132,132,CW-264])
h('2.2 Review thật thu thập định kỳ')
p('collect_live_reviews.py dùng google-play-scraper, lấy tối đa 100 review mới nhất/app với lang=vi, country=vn, Sort.NEWEST. Đây là cửa sổ lấy có giới hạn, không bảo đảm toàn bộ review của Google Play. Ban đầu có 400 review; snapshot báo cáo tích lũy 407 review duy nhất. Review ra khỏi cửa sổ lấy không bị xóa khỏi HDFS. [T10]')
table(['Trường event JSON','Ý nghĩa'],[['event_id','SHA-256 appid + review_id + content + score + event_time; ID phiên bản'],['review_id, appid','Khóa review gốc và ứng dụng'],['content, score','Văn bản UTF-8 và số sao integer'],['event_time','Ngày review gốc, yyyy-MM-dd HH:mm:ss'],['ingested_at','Mốc tiếp nhận UTC; chọn phiên bản mới'],['source_mode, source_url','google_play_live và URL Google Play'],['poll_id','ID lượt thu thập để đối chiếu log']],[145,CW-145])
p('Ngày review và thời điểm thu thập khác nhau. Batch dùng session Asia/Ho_Chi_Minh; live dùng UTC trong Spark, hiển thị mốc vận hành theo giờ Việt Nam. Tổng nguồn gộp tại mốc minh chứng: 1.299.873 + 407 - 6 ID trùng = 1.300.274 review. Bản live thay bản lịch sử trùng ID.')
cite(['jobs/collect_live_reviews.py','outputs/live/generations/'+live_gen+'/dashboard_preparation.json','outputs/combined_source_validation.json'])
h('2.3 Đối soát chất lượng')
p('Raw có 71 nội dung trống. Sau chuẩn hóa, một review chỉ chứa ký tự vô hình U+200D cũng rỗng nên có 72 nội dung rỗng; thêm 2 sao=0 tạo 74 quarantine. Loại 139 bản sao ID. Đối soát: 1.300.086 = 74 + 139 + 1.299.873. Quarantine giữ lý do trên HDFS để truy vết.')
p('638.855 dòng lặp nội dung chuẩn hóa trong cùng app ở audit raw không đồng nghĩa review giả. Các ID khác nhau có thể cùng ghi “tốt”/“ok”, nên được giữ. Cờ spam ban đầu có 88 ứng viên, là luật hẹp chưa được gán nhãn người đọc, không phải tổng spam thực tế.')
chapter('3. Kiến trúc và luồng dữ liệu')
architecture()
p('HDFS lưu dữ liệu; Spark xử lý/huấn luyện; Kafka vận chuyển sự kiện mới; Airflow điều phối; dashboard đọc output xuất từ HDFS. WSL chạy Docker Linux với hai Spark worker. Đây là mô hình học tập phân tán theo tiến trình trên một máy, chưa phải cụm nhiều máy có HA.')
table(['Thành phần','Cấu hình','Vai trò'],[['HDFS','3.3.6; 1 NameNode + 1 DataNode; replication=1','Raw, clean, output, models, checkpoint'],['Spark / Java','Spark 3.5.7; Java 11; low-memory: 2 worker × 1 core / 1 GiB','DataFrame, SQL, MLlib, Streaming'],['Kafka','3.9.0; KRaft; 1 broker/controller; 3 partition/topic; replication=1','Topic lịch sử và live riêng'],['Airflow / Postgres','2.10.5; LocalExecutor; PostgreSQL 16.6','Lịch, dependency, retry, metadata, log'],['Dashboard','Python HTTP + JS; cube nhỏ / SQLite','Tìm kiếm toàn tập và đồ thị tự cập nhật'],['Replay runner','Hadoop FileSystem client; run_id riêng','Copy tháng, commit tiến độ, verify cuối']],[103,193,CW-296])
table(['Vùng HDFS','Nội dung'],[['/ecommerce/raw','CSV gốc và source_sha256.txt'],['/ecommerce/quarantine','Record lỗi và lý do'],['/ecommerce/processed/reviews','Parquet partition platform/year'],['/ecommerce/output và /models','Bảng SQL, cube, predictions và models'],['/ecommerce/checkpoints','Checkpoint Kafka replay lịch sử'],['/ecommerce/live','Event, versions, latest reviews, serving, checkpoint riêng'],['/ecommerce/replay/prepared','Parquet theo tháng đã đối soát'],['/ecommerce/replay/runs/<run_id>/loaded','Lô nạp lại độc lập dữ liệu gốc']],[225,CW-225])
p('Không collect toàn bộ dữ liệu lớn về driver/trình duyệt. Bước xuất dashboard chỉ collect bảng nhỏ, giới hạn 10.000 dòng. Chỉ mục tìm kiếm đọc tuần tự JSON gzip xuất từ HDFS; API tra cứu toàn tập, không dùng một mẫu chọn trước.')
cite(['compose.yaml','compose.low-memory.yaml','infra/Dockerfile','jobs/prepare_dashboard.py','scripts/build_dashboard_index.py'])
chapter('4. HDFS: kiến thức, cấu hình và minh chứng')
h('4.1 Giải thích bằng dự án')
p('HDFS là hệ thống file phân tán. NameNode quản lý namespace và ánh xạ file-block; DataNode lưu block, phục vụ đọc/ghi. Client hỏi NameNode vị trí block rồi trao đổi dữ liệu với DataNode. File được chia block; replication tạo bản sao để phục hồi khi node hỏng. [T2]')
p('fs.defaultFS=hdfs://namenode:9000. http://localhost:9870 là giao diện quản trị, không phải địa chỉ dữ liệu Spark. Block size kiểm tra được: 134.217.728 byte (128 MiB). CSV chiếm 5 block: bốn block đủ 128 MiB và block cuối 106.097.069 byte.')
p('Replication=1 vì demo chỉ có một DataNode; không có bản sao để chịu hỏng node. dfs.permissions.enabled=false và bind localhost là cấu hình demo cục bộ, chưa phù hợp triển khai công khai. [T3]')
h('4.2 Lệnh và kết quả kiểm tra')
shell("""docker compose exec -T spark-client hdfs dfs -ls -h /ecommerce/raw
docker compose exec -T spark-client hdfs getconf -confKey dfs.blocksize
docker compose exec -T spark-client hdfs dfsadmin -report
docker compose exec -T spark-client hdfs fsck /ecommerce/raw/reviews.csv -files -blocks -locations
docker compose exec -T spark-client hdfs dfs -cat /ecommerce/raw/reviews.csv | sha256sum""")
p('-ls kiểm tra file/byte; dfsadmin -report xem DataNode/capacity; fsck kiểm tra block/replica; SHA-256 đối chiếu nội dung. hdfs dfs -count đếm thư mục/file/byte, không đếm record CSV. [T4]')
block("""/ecommerce/raw/reviews.csv 642967981 bytes,
replication=1, 5 block(s): OK
Status: HEALTHY
Number of data-nodes: 1
Missing blocks: 0
Corrupt blocks: 0
Default replication factor: 1
SHA-256: 9d333c550cb141aa0f3e9f12af43e8e407809031b073b046b61607f84b39bdf9""")
cite(['outputs/logs/hdfs_blocks_20261015.txt','outputs/logs/hdfs_report_20261015.txt','outputs/logs/hdfs_raw_sha256_20261015.txt','infra/hadoop/hdfs-site.xml'])
h('4.3 Kiểm tra trên browser')
p('Mở http://localhost:9870, chọn Utilities / Browse the file system, duyệt /ecommerce/raw, /ecommerce/processed, /ecommerce/live, /ecommerce/replay; đối chiếu đường dẫn/kích thước với -ls. Ảnh chỉ bổ trợ, không thay code upload/read, checksum, fsck và log Spark. stop giữ volume; không format NameNode hoặc xóa volume khi khởi động lại thông thường.')

chapter('5. PySpark đọc HDFS, làm sạch và biến đổi')
h('5.1 Đọc CSV trực tiếp từ HDFS')
function('src/review_analytics/spark_ops.py','read_raw','Schema tường minh đọc raw dạng string để tránh ép kiểu sai và giữ lỗi cho quarantine. Schema gồm 12 cột dữ liệu và cột kỹ thuật _corrupt_record; header nhận header; multiLine xử lý review có newline; quote/escape xử lý dấu nháy. PERMISSIVE và _corrupt_record nhận diện lỗi parser. path mặc định trong batch_pipeline.py là hdfs://namenode:9000/ecommerce/raw/reviews.csv. [T5]')
p('CSV đơn file với multiLine có thể chỉ có một partition đọc; dự án repartition trước làm sạch để phân phối các bước sau. raw.count() trả đúng 1.300.086 record theo audit CSV. Đây là đọc từ HDFS, không phải CSV ở Downloads.')
h('5.2 Chuẩn hóa và đặc trưng phân tích')
function('src/review_analytics/text.py','normalize_text','Unicode NFKC, chữ thường, loại ký tự vô hình, gộp whitespace; giữ dấu tiếng Việt và phủ định. Nhánh feature ML mới loại URL, token hóa âm tiết, map từ viết tắt. Không mô tả hàm này như bộ tách từ tiếng Việt chuyên dụng.')
function('src/review_analytics/spark_ops.py','enrich','UDF chuẩn hóa; ép score integer và at timestamp; map appid -> platform; tạo review_key bằng SHA-256 rút gọn; year/month và cờ 1-2 sao; cờ spam theo luật. Mảng aspects_mentioned tạo nhãn đề cập đa nhãn, không phải polarity từng khía cạnh.')
h('5.3 Quarantine và khử trùng theo ID')
function('src/review_analytics/spark_ops.py','validation_reasons','Mảng lý do gồm CSV sai, thiếu ID/nội dung, sao/date/app lỗi. Batch kiểm tra khoảng lịch sử; live truyền historical_period=False để nhận review 2026, chỉ thêm kiểm tra ngày tương lai bất hợp lý.')
function('src/review_analytics/spark_ops.py','deduplicate_valid','Window theo appid + reviewid; ưu tiên at mới nhất, hash nội dung/sao làm tie-breaker ổn định. row_number=1 giữ một bản. Không dedup content vì các ID khác nhau có thể cùng viết một câu ngắn.')
h('5.4 Ghi Parquet và đối soát')
excerpt('jobs/batch_pipeline.py',45,58,'MEMORY_AND_DISK tái sử dụng prepared/cleaned, có thể spill ra đĩa. Invalid ghi quarantine; valid dedup và ghi Parquet theo platform/year. Phần cuối hàm đối soát raw = invalid + duplicate + clean và unpersist giải phóng cache; xem toàn bộ hàm tại phụ lục A2.')
p('Parquet là định dạng cột; đọc chọn cột và partition pruning giảm dữ liệu phải đọc. Query Shopee năm 2022 có PartitionFilters; Exchange thể hiện shuffle để GROUP BY. Không khẳng định mọi query đều không shuffle; groupBy và Window có thể trao đổi dữ liệu giữa worker.')
cite(['outputs/raw_inspection.json','outputs/data_quality.json','outputs/persisted_validation.json','outputs/spark_query_plan.txt'])
chapter('6. Spark SQL và kết quả phân tích')
h('6.1 Truy vấn thực tế')
source=content('jobs/batch_pipeline.py');lines=source.splitlines();start=next(i+1 for i,v in enumerate(lines) if '"platform_summary": spark.sql' in v);end=next(i for i in range(start,len(lines)) if '"rating_distribution": spark.sql' in lines[i]);excerpt('jobs/batch_pipeline.py',start,end,'Temp view reviews cho phép SQL trên DataFrame HDFS. COUNT làm mẫu số; SUM CASE WHEN đếm sao thấp; AVG 1.0/0.0 tạo tỷ lệ. Group theo platform hoặc platform/month, tránh so sánh số review thấp tuyệt đối giữa các tập khác kích thước.')
h('6.2 Kết quả lịch sử sau làm sạch')
table(['Nền tảng','Review','Sao thấp','Tỷ lệ 1-2','Điểm TB'],[[k,N(rows[k]['reviews']),N(rows[k]['low_rating_reviews']),PCT(rows[k]['low_rating_rate']),D(rows[k]['mean_rating'],4)] for k in order],[80,97,96,100,CW-373])
figure('outputs/report_charts/01_platform_low_rating.png','Hình 1. Số lượng và tỷ lệ sao thấp từ platform_summary.csv, dataset lịch sử sau làm sạch.',310)
p('Shopee có tỷ lệ 1-2 sao cao nhất snapshot (27,55%), Sendo thấp nhất (14,08%). Đây là khác biệt của tập người viết và giai đoạn thu thập; chưa đủ xếp hạng mức hài lòng toàn bộ khách hàng hoặc kết luận nguyên nhân.')
h('6.3 Khía cạnh trong review sao thấp')
table(['Nền tảng','Ứng dụng','Vận chuyển','Chưa gán'],[[k,PCT(next(r['mention_rate_among_low'] for r in aspects if r['platform']==k and r['aspect']=='app')),PCT(next(r['mention_rate_among_low'] for r in aspects if r['platform']==k and r['aspect']=='delivery')),PCT(next(r['unmatched_rate'] for r in unmatched if r['platform']==k))] for k in order],[100,110,110,CW-320])
figure('outputs/report_charts/03_aspect_platform_heatmap.png','Hình 2. Đề cập khía cạnh trong nhóm 1-2 sao. Đa nhãn nên các tỷ lệ không cộng thành 100%.',330)
p('Ứng dụng và vận chuyển nổi bật ở cả bốn nền tảng. Nên đọc phản hồi về đăng nhập/hiệu năng hoặc giao hàng để rà soát nghiệp vụ. Tỷ lệ chưa gán 48,86%-62,15% cho thấy phải phân biệt phản hồi chung với luật bỏ sót; không ép mọi review vào taxonomy để làm đẹp số liệu.')
p('Bảy nhóm: app, delivery, product, support, payment, promotion, returns. Đóng gói nằm trong product; giá/khuyến mãi nằm trong promotion. Review sao thấp có thể khen hàng hóa và chê giao hàng; đề cập không xác nhận cảm xúc tiêu cực của từng nhóm.')
h('6.4 Thời gian, độ dài và độ nhạy spam')
figure('outputs/report_charts/02_annual_trend_and_volume.png','Hình 3. Xu hướng và khối lượng lịch sử, nguồn monthly_summary.csv; chỉ diễn giải các khoảng có dữ liệu.',320)
p('Tỷ lệ tháng ít review có thể biến động mạnh, cần đọc cùng mẫu số. review_length_summary.csv có độ dài và phân vị; spam_sensitivity.csv so sánh sau bỏ ứng viên spam. Cờ luật 88 ứng viên không chứng minh các review còn lại không chứa spam.')
cite(['outputs/platform_summary.csv','outputs/monthly_summary.csv','outputs/aspect_mentions.csv','outputs/unmatched_low_ratings.csv','outputs/review_length_summary.csv','outputs/spam_sensitivity.csv'])
chapter('7. Machine Learning: đặc trưng, chia tập và metric')
h('7.1 Mục tiêu và đặc trưng')
p('Dự đoán nhóm sao từ văn bản: label=1 khi score<=2, label=0 khi score>=4; bỏ sao 3, ứng viên spam, văn bản không có token. Nhãn star_rating_proxy chưa phải ground truth cảm xúc. model_terms tạo âm tiết unigram/bigram; CountVectorizer (vocabSize=6.000, minDF=3), IDF và L2 Normalizer tạo TF-IDF. [T6]')
excerpt('jobs/train_sentiment.py',42,61,'Sample 5% bằng hash nhóm normalized_content. Chia bucket nhóm 70/10/20; cùng văn bản giữa các nền tảng vào cùng split. Tỷ lệ dòng không bắt buộc 70/10/20 vì nhóm văn bản có số dòng khác nhau.')
table(['Tập','Sao cao (0)','Sao thấp (1)','Tổng dòng'],[[split,N(next(r['count'] for r in ml['split_counts'] if r['split']==split and r['label']==0)),N(next(r['count'] for r in ml['split_counts'] if r['split']==split and r['label']==1)),N(sum(r['count'] for r in ml['split_counts'] if r['split']==split))] for split in ['train','validation','test']],[105,120,120,CW-345])
excerpt('jobs/train_sentiment.py',62,80,'Vocabulary/IDF chỉ fit train, tránh leakage đặc trưng. Trọng số lớp lấy từ train để giảm lệch lớp. LR/SVM thử regParam 0.01 và 0.1, maxIter=40; chọn bằng macro-F1 validation trước khi đánh giá test.')
h('7.2 So sánh model và test cuối')
table(['Mô hình','reg','Accuracy val','Macro-F1 val'],[[c['model'],str(c['regParam']),D(c['validation']['accuracy'],4),D(c['validation']['macro_f1'],4)] for c in ml['validation_candidates']],[171,55,130,CW-356])
table(['Chỉ số test','LR chọn','Majority baseline'],[['Accuracy',PCT(ml['test']['accuracy']),PCT(ml['majority_baseline_test']['accuracy'])],['Precision sao thấp',D(ml['test']['precision_negative'],4),'0'],['Recall sao thấp',D(ml['test']['recall_negative'],4),'0'],['F1 sao thấp',D(ml['test']['f1_negative'],4),'0'],['Macro-F1',D(ml['test']['macro_f1'],4),D(ml['majority_baseline_test']['macro_f1'],4)]],[181,150,CW-331])
table(['Nhãn thật / dự đoán','Sao cao (0)','Sao thấp (1)'],[['Sao cao (0)','8.552','1.015'],['Sao thấp (1)','297','3.129']],[215,140,CW-355])
function('jobs/train_sentiment.py','metrics','Bảng 2x2 là tổng hợp nhỏ được collect. Với target label=1 (sao thấp), precision=TP/(TP+FP), recall=TP/(TP+FN), F1 là trung bình điều hòa; accuracy=(TP+TN)/tổng. Macro-F1 lấy trung bình F1 hai lớp để tránh chỉ nhìn lớp đông hơn.')
p('Recall sao thấp cao hơn precision: tìm được nhiều review 1-2 sao nhưng còn false positive. Chênh macro-F1 validation LR/SVM nhỏ, chưa khẳng định ưu thế tổng quát. Test có 12.993 dòng; giao nhóm train/validation/test đều 0. Chưa kiểm tra near-duplicate hoặc ngoại suy theo thời gian/nền tảng mới.')
h('7.3 Lỗi và model phục vụ')
p('Một review 5 sao nhưng nội dung than phiền phí ship bị model dự đoán sao thấp, nên bị tính sai theo proxy. Đây là ví dụ sao không đồng nhất hoàn toàn với cảm xúc câu. Văn bản vô nghĩa/ngắn cũng gây lỗi. Không sửa nhãn test bằng AI để tăng metric.')
p(f'Chọn 100 mẫu để đối chiếu Spark và serving; {ml["portable_predictions_checked"]} mẫu có đặc trưng được so khớp thành công, 2 mẫu serving trả uncertain. Hai nhánh dùng cùng tokenizer/vocabulary/IDF/hệ số; fingerprint: {ml["model_sha256"]}. Demo không thay model đã đánh giá bằng luật cảm xúc tự chế.')
cite(['jobs/train_sentiment.py','src/review_analytics/sentiment.py','outputs/sentiment_evaluation.json','outputs/sentiment_model.json','outputs/logs/sentiment_train_20261015.log'])
h('7.4 K-Means khám phá bổ sung')
p(f'K={cluster["k"]}, seed=42, cosine; mẫu hash 25% review sao thấp đủ điều kiện, {N(cluster["training_rows"])} vector khác 0. Silhouette của artifact: {D(cluster["silhouette_cosine"],5)}. Cụm phân tách yếu, dùng khám phá và đọc ví dụ; silhouette không phải accuracy khía cạnh. Chưa fine-tune PhoBERT hoặc có nhãn ABSA người đọc.')
excerpt('jobs/batch_pipeline.py',129,154,'RegexTokenizer/StopWordsRemover tạo âm tiết, NGram tạo bigram; TF-IDF/L2 và KMeans cosine. Silhouette dùng tối đa 10.000 điểm. Phần tiếp theo lưu model, feature và sample assignments vào HDFS; human_label=unassigned tránh gọi cụm khám phá là nhãn đã xác nhận. Xem hàm đầy đủ tại phụ lục A2.')

chapter('8. Kafka và Spark Structured Streaming')
h('8.1 Kiến thức Kafka cần trình bày')
p('Kafka giữ luồng event theo topic. Producer ghi event; consumer đọc. Topic chia partition; offset là vị trí trong một partition, không phải mã review. Thứ tự được giữ trong từng partition, không có thứ tự toàn cục giữa ba partition. Broker phục vụ/lưu log; các replica giúp chịu lỗi khi có nhiều broker. [T7]')
table(['Khái niệm','Trong dự án'],[['Producer','collect_live_reviews.py gửi JSON UTF-8; replay_kafka.py chỉ demo lịch sử'],['Topic','ecommerce-live-reviews (thật), ecommerce-reviews (replay lịch sử)'],['Partition / broker','3 partition/topic trên 1 broker KRaft, replication=1'],['Key / ID nghiệp vụ','Key=appid:review_id; event_id là fingerprint phiên bản'],['Offset / checkpoint','Kafka có offset từng partition; Spark lưu tiến độ/state trong HDFS checkpoint'],['Consumer','stream_reviews.py đọc Kafka bằng Spark readStream']],[137,CW-137])
p('acks=all chờ xác nhận từ các replica đồng bộ; với replication=1 ở demo chỉ có một broker xác nhận. retries không tự bảo đảm toàn pipeline exactly-once; còn phụ thuộc producer, checkpoint và cách ghi đích. Không tuyên bố chịu hỏng broker khi chỉ có một bản sao. [T13, T14]')
h('8.2 Producer thật và chống gửi lại phiên bản')
function('jobs/collect_live_reviews.py','build_event','Giữ review ID và thời gian nguồn. event_id thay đổi khi nội dung/sao/thời gian nguồn đổi, không thay chỉ vì poll_id/ingested_at mới. Vì vậy cùng một review không bị biến thành event mới ở mọi lần kiểm tra.')
source=content('jobs/collect_live_reviews.py');lines=source.splitlines();start=next(i+1 for i,v in enumerate(lines) if "previous=connection.execute" in v);end=next(i for i in range(start,len(lines)) if 'except Exception' in lines[i]);excerpt('jobs/collect_live_reviews.py',start,end,'SQLite seen lưu signature đã gửi. Chỉ ghi nhớ sau khi producer.send(...).get() nhận ack Kafka. Nếu crash sau ack trước cập nhật state, có thể gửi lại, nhưng event_id ổn định và consumer dedup là lớp bảo vệ tiếp theo. Nếu mọi nguồn lỗi, task fail, không dùng review giả làm fallback.')
h('8.3 PySpark consumer từ Kafka sang HDFS')
excerpt('jobs/stream_reviews.py',34,42,'readStream đọc topic; startingOffsets=earliest chỉ dùng khi chưa có checkpoint. maxOffsetsPerTrigger=500 giới hạn tải mỗi microbatch. from_json áp schema rồi giữ topic/partition/offset/raw_json để truy vết. dropDuplicates theo phiên bản event ID. [T8]')
excerpt('jobs/stream_reviews.py',44,65,'foreachBatch xử lý một microbatch: lưu raw JSON của event đã qua dedup; chuẩn hóa/kiểm tra; ghi valid Parquet, quarantine và metrics theo batch_id. mode=overwrite ở đường dẫn batch cố định hỗ trợ chạy lại lô, thay vì append lặp. Lý do lỗi không bị bỏ im lặng.')
excerpt('jobs/stream_reviews.py',67,74,'Checkpoint live và lịch sử tách riêng. DAG định kỳ dùng availableNow để xử lý lượng event hiện có rồi kết thúc, phù hợp task Airflow hữu hạn. Cờ --continuous mới dùng processingTime 10 seconds. Giao diện kiểm tra 10 giây không có nghĩa collector thu thập mỗi 10 giây. [T8]')
h('8.4 Cập nhật một review và công bố snapshot')
function('jobs/publish_live_dashboard.py','latest_review_versions','Window theo review_key chọn ingested_at mới nhất; event_id làm tie-breaker. Một review có nhiều phiên bản chỉ góp một bản vào biểu đồ; metric có thể thay đổi mà số review không tăng.')
p('Publisher đọc versions trực tiếp trên HDFS, đối soát số phiên bản với stream metrics, giữ latest key và kiểm tra source_mode. Cube, index và metadata được xây trong generation riêng; chỉ đổi current.json sau kiểm tra độc lập đạt. Dashboard không đọc một nửa tệp cũ và một nửa tệp mới.')
h('8.5 Topic và kết quả đối chiếu')
shell("""docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 --describe --topic ecommerce-live-reviews
# Kết quả đã lưu: PartitionCount: 3; ReplicationFactor: 1
# Mỗi partition: Leader 1; Replicas 1; Isr 1""")
p('Demo replay hữu hạn có tổng 2.000 offsets sau hai lượt producer nhưng chỉ 1.000 review duy nhất trong streaming HDFS, sáu microbatch, ba batch không có event mới. Đây là minh chứng checkpoint/dedup của nguồn lịch sử; không gọi 2.000 offsets là 2.000 review mới thật.')
p(f'Nguồn thật có {N(live_meta["processed_rows"])} review ở generation {live_gen}; ban đầu 400, sau đó nhận thêm review thật. Kafka offset, số event phiên bản và số review latest có thể khác nhau nếu có gửi lại hoặc sửa review. So sánh đúng loại số đếm, không lấy offset làm số khách hàng.')
cite(['outputs/logs/kafka_topic_20261015.txt','outputs/logs/live_kafka_topic_20261015.txt','outputs/logs/kafka_producer_20261015.log','outputs/logs/kafka_consumer_20261015.log','outputs/persisted_validation.json','outputs/live_dashboard_validation.json'])
chapter('9. Airflow: DAG, vận hành và minh chứng')
h('9.1 Vai trò từng thành phần')
p('DAG là đồ thị task có hướng, không chu trình. Dependency định thứ tự; Operator định nghĩa việc thực hiện. DAG run là một lượt workflow; task instance là một task trong lượt đó. Scheduler xét lịch và dependency; executor thực thi; webserver để xem/trigger/debug; metadata database lưu trạng thái. [T9, T11]')
p('Dự án dùng BashOperator gọi Python/spark-submit, LocalExecutor và PostgreSQL. Airflow không lưu thay HDFS, không xử lý luồng thay Kafka và không thay engine Spark. Dữ liệu lớn nằm trên HDFS; database Airflow chỉ giữ metadata vận hành.')
table(['DAG','Lịch / số task','Mục đích'],[['ecommerce_dissatisfaction_pipeline','schedule=None; 10 task','Upload -> đọc -> clean -> SQL -> K-Means -> LR/SVM -> export -> Kafka replay -> verify'],['live_google_play_reviews','*/5 * * * *; 4 task','Thu thập thật -> Kafka/HDFS -> publish -> verify'],['prepare_historical_month_replay','schedule=None; 1 task','Spark chuẩn bị và đối soát các lô tháng cho replay runner']],[170,133,CW-303])
h('9.2 Mã DAG thực tế')
excerpt('dags/ecommerce_pipeline.py',8,37,'Chuỗi >> buộc các bước phụ thuộc nối tiếp. Task 06b là huấn luyện LR/SVM; task 07 tạo cube/index; task cuối đọc lại HDFS và đối chiếu. Batch schedule=None được trigger có chủ đích để không huấn luyện lại toàn tập mỗi 5 phút.')
source=content('dags/live_reviews_pipeline.py');start=next(i+1 for i,v in enumerate(source.splitlines()) if v.startswith('with DAG'));excerpt('dags/live_reviews_pipeline.py',start,len(source.splitlines()),'Lịch 5 phút, catchup=False, max_active_runs=1, retries=1 và retry_delay 30 giây. Nếu lượt chạy lâu, lượt sau phải chờ; không hứa luôn xong đúng 5 phút. Start date và lịch dùng Asia/Ho_Chi_Minh. Lỗi vẫn được giữ trong task log. [T9, T12]')
h('9.3 Run đã đối chiếu')
p('Batch run_id=validation_20261015 có 10/10 task success. Thời gian trong bảng đổi từ UTC log sang giờ Việt Nam; không nhầm execution_date của khoảng lịch với thời điểm task thực thi.')
table(['Task','Bắt đầu (VN)','Kết thúc (VN)','State'],[[t['task_id'],local(t['start_utc']).split()[0],local(t['end_utc']).split()[0],t['state']] for t in evidence['airflow']['tasks']],[215,95,95,CW-405])
p('Live run được chụp cùng snapshot báo cáo: '+escape(live_browser['dag']['run_id'])+'; 4/4 task success. Run scheduled mang mốc logical interval trước thời điểm thực thi: đây là ngữ nghĩa lịch, không phải pipeline ngừng.')
table(['Live task','Bắt đầu (VN)','State'],[[t['task_id'],local(t['start_utc']),t['state']] for t in live_browser['dag']['tasks']],[218,185,CW-403])
h('9.4 Khi lỗi cần xem gì?')
p('Xem DAG run rồi task cụ thể, đúng try_number và stdout/stderr. Task failed khác DAG paused: paused ngăn scheduler tạo lịch mới, failed là lần thực thi đã lỗi. Retry chỉ hữu ích khi thao tác có thể chạy lại; fingerprint raw, batch_id, checkpoint và generation giúp tránh ghi lặp. Clear task để chạy lại phải hiểu dependency và output trước đó; không xóa dữ liệu HDFS gốc để sửa trạng thái Airflow. [T12]')
shell("""docker compose exec -T airflow-scheduler airflow dags list-runs -d live_google_play_reviews --output json
docker compose exec -T airflow-scheduler airflow dags list-import-errors
docker compose logs --tail 80 airflow-scheduler
# UI: http://localhost:8080 -> DAG -> Run -> Task -> Log""")
cite(['dags/ecommerce_pipeline.py','dags/live_reviews_pipeline.py','dags/historical_replay_pipeline.py','outputs/demo_evidence.json','outputs/logs/airflow_tasks','outputs/logs/live_airflow_tasks','outputs/logs/replay_airflow_tasks'])
chapter('10. Dashboard, đồ thị trượt và liên kết với output')
h('10.1 HDFS -> Spark -> cube/index -> API')
p(f'prepare_dashboard.py đọc Parquet HDFS, groupBy platform/month/score/spam, tổng hợp count/unmatched/7 khía cạnh. Cube lịch sử có {N(dash_meta["cube_rows"])} ô; index có {N(dash_meta["processed_rows"])} review. validate_dashboard.py so toàn bộ chín số đếm mỗi ô với SQL trên chỉ mục. generation và tổng count phải khớp trước khi phục vụ.')
excerpt('jobs/prepare_dashboard.py',23,38,'Tổng hợp bằng DataFrame trên HDFS, ghi Parquet rồi chỉ collect bảng nhỏ có giới hạn. Count trong cube phải bằng clean_rows. Browser không tự tính từ dữ liệu giả hoặc chỉ nhìn ảnh minh họa.')
p('API overview và reviews dùng cùng nguồn/generation. Source=all gộp lịch sử với live, loại bản lịch sử có ID đã được live thay; source=historical/live cho so sánh riêng. Clear bỏ tất cả điều kiện và trở về toàn nguồn, toàn khoảng tháng. Từ khóa tự tìm sau 300 ms; bộ lọc khoảng 180 ms; snapshot chung kiểm tra mỗi 10 giây, giữ lựa chọn.')
figure('outputs/screenshots/11-clear-all-data-20261015.png','Hình 4. Nguồn gộp và Clear toàn bộ dữ liệu. Ảnh đọc cùng clear_filters_validation.json và combined_source_validation.json; số liệu là snapshot có generation trong hai file này.',480)
h('10.2 Replay lịch sử theo tháng trên HDFS')
p('Đồ thị nạp dần giữ tối đa 12 tháng, bắt đầu 06/2013, kết thúc 08/2022. Bốn nền tảng bật mặc định, có thể bật/tắt riêng; tháng chưa có review không tạo điểm. Đường chuyển động 700 ms giữa tọa độ thật, trục tỷ lệ cố định 0-100% hoặc điểm trung bình 0-5. Giao diện tuân theo prefers-reduced-motion.')
function('jobs/prepare_replay.py','monthly','Spark tính số review, sao thấp và rating_sum theo tháng/nền tảng. prepare_replay đọc HDFS, ghi lô Parquet theo month rồi đọc lại so toàn bộ nhóm trước khi công bố manifest prepared.json.')
p('replay_months.py dùng Hadoop FileSystem copy lô tháng sang thư mục tạm của run riêng, kiểm số file/byte rồi rename commit. Chỉ sau đó tăng cursor và công bố frame. Cuối 111 tháng, Spark đọc lại đích HDFS, kiểm count, distinct review_key và toàn bộ 377 nhóm. Đây là nạp lại batch thật trên HDFS, có nhãn demo; không phải thu thập review mới.')
p('Nạp lại từ đầu tạo UUID run mới, không xóa dữ liệu gốc hoặc live. Tạm dừng áp dụng sau lô đang chạy; restart đọc checkpoint và tiếp tục. Tốc độ tối thiểu 2/4/8 giây mỗi lô, còn tùy I/O và đối soát; mặc định 4 giây tương đương phần phát lại tối thiểu khoảng 7,4 phút.')
figure('outputs/screenshots/14-four-platform-replay-20261015.png','Hình 5. Lượt replay hoàn tất 111 lô / 1.299.873 review; bốn đường, cửa sổ 12 tháng. Đối chiếu validation_<run_id>.json và Spark verification log.',390)
h('10.3 Đồ thị review thật theo thời điểm thu thập')
p('Nút Xem review mới thật chuyển sang 12 mốc quan sát gần nhất. verify_live_outputs.py chỉ ghi mốc sau khi snapshot HDFS/index đối soát đạt, gồm poll_id, generation và count/low/rating_sum từng nền tảng. Nguồn được lấy mỗi 5 phút, UI đọc tiến độ mỗi giây. Lượt không có review mới/sửa giữ giá trị; không tạo dao động ngẫu nhiên.')
figure('outputs/screenshots/15-live-source-growth-20261015.png','Hình 6. Timeline thu thập thật; snapshot minh chứng có 407 review. Tăng/giảm tỷ lệ khác với tăng tổng review; lượt không thay đổi có đường phẳng.',390)
p('Không nối giai đoạn 2022-2025 không có dữ liệu lịch sử thành dữ liệu quan sát. Biểu đồ theo thời gian review, replay tháng và timeline thời gian thu thập là ba cách nhìn khác nhau; nhãn/trục phải nêu đúng loại thời gian.')
cite(['jobs/prepare_dashboard.py','dashboard/server.py','dashboard/web/replay.js','jobs/prepare_replay.py','jobs/replay_months.py','scripts/verify_live_outputs.py','outputs/replay_browser_validation.json','outputs/replay_restart_validation.json'])

chapter('11. Cài đặt và lệnh chạy từ đầu đến cuối')
p('Các khối dưới chạy trong terminal WSL Ubuntu tại thư mục repository. PowerShell chỉ dùng wsl -d Ubuntu để vào Linux. Không cần cài Hadoop/Java trực tiếp trên Windows; runtime nằm trong Docker. Mật khẩu chỉ được tạo vào .env tại máy, không chép vào PDF hoặc ảnh.')
h('11.1 Chuẩn bị môi trường và chạy batch')
shell("""# PowerShell
wsl -d Ubuntu
# Từ đây là Bash trong Ubuntu
cd /home/VIDO/projects/bigdata_pro/Bigdata_Review
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 docker-buildx git
sudo systemctl start docker
sudo usermod -aG docker "$USER"
# Mở lại terminal WSL để nhận group docker rồi quay về repo
python3 scripts/download_dataset.py
python3 scripts/init_local_env.py
bash scripts/run_pipeline.sh""")
p('run_pipeline.sh audit CSV, build runtime, dựng HDFS/Spark, chuẩn bị quyền output, upload raw, chạy batch + ML + dashboard, demo Kafka lịch sử và đối soát. Dùng low-memory khi RAM hạn chế; chạy job tuần tự. Trần bộ nhớ container không phải lượng RAM luôn dùng thực tế.')
h('11.2 Bật Airflow, nguồn thật và replay tháng')
shell("""bash scripts/start_live.sh
# Khởi động core/Kafka/Postgres/Airflow/dashboard và bật lịch live 5 phút
bash scripts/start_replay.sh
# Trigger DAG chuẩn bị tháng; runner tự nạp khi manifest đã kiểm tra""")
p('DAG batch đầy đủ có thể chạy trong Airflow theo lệnh sau; không cần chạy đồng thời với run batch đang hoạt động. Sau khi success, dùng đúng run ID để capture minh chứng. Chạy lại có thể tạo generation mới nên phải lấy lại bảng/ảnh tương ứng.')
shell("""docker compose exec -T airflow-scheduler airflow dags unpause ecommerce_dissatisfaction_pipeline
docker compose exec -T airflow-scheduler airflow dags trigger ecommerce_dissatisfaction_pipeline --run-id demo_batch_$(date +%Y%m%d_%H%M%S)
docker compose exec -T airflow-scheduler airflow dags list-runs -d ecommerce_dissatisfaction_pipeline --output json
# Thay RUN_ID_DA_SUCCESS bằng run ID thực, không dùng nguyên chuỗi mẫu
docker compose exec -T airflow-scheduler python scripts/capture_evidence.py --run-id RUN_ID_DA_SUCCESS
docker compose cp airflow-scheduler:/opt/airflow/logs/dag_id=ecommerce_dissatisfaction_pipeline outputs/logs/airflow_tasks""")
h('11.3 Chạy từng bước PySpark để giải thích')
shell("""# Dùng cấu hình low-memory cho các lệnh tương tác
 dc() { docker compose -f compose.yaml -f compose.low-memory.yaml --profile orchestration --profile streaming --profile dashboard "$@"; }
 dc exec -T spark-client python scripts/bootstrap_hdfs.py
 dc exec -T spark-client spark-submit --master spark://spark-master:7077 --driver-memory 1g --executor-memory 1g jobs/batch_pipeline.py --stage inspect
 dc exec -T spark-client spark-submit --master spark://spark-master:7077 --driver-memory 1g --executor-memory 1g jobs/batch_pipeline.py --stage clean
 dc exec -T spark-client spark-submit --master spark://spark-master:7077 --driver-memory 1g --executor-memory 1g jobs/batch_pipeline.py --stage analyze
 dc exec -T spark-client spark-submit --master spark://spark-master:7077 --driver-memory 1g --executor-memory 1g jobs/train_sentiment.py
 dc exec -T spark-client spark-submit --master spark://spark-master:7077 --driver-memory 1g --executor-memory 1g jobs/validate_persisted.py
 dc exec -T spark-client python scripts/validate_dashboard.py --outputs /exports""")
p('inspect in schema/count; clean ghi quarantine/Parquet; analyze ghi bảng SQL; train_sentiment huấn luyện/đánh giá; validate_persisted đọc lại HDFS. Nếu chạy riêng clean/analyze/train sau khi thay nguồn, cần chạy lại export và prepare_dashboard/index trước khi trình bày giao diện. Lệnh đầy đủ nằm trong run_pipeline.sh và DAG.')
h('11.4 Producer và consumer thật chạy thủ công')
shell("""# Chỉ dùng để demo riêng khi DAG live không chạy chồng tác vụ này
 dc exec -T spark-client python jobs/collect_live_reviews.py
 dc exec -T spark-client spark-submit --master spark://spark-master:7077 --driver-memory 1g --executor-memory 1g --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7 jobs/stream_reviews.py --live --topic ecommerce-live-reviews --root hdfs://namenode:9000/ecommerce/live --exports /exports/live
 dc exec -T spark-client spark-submit --master spark://spark-master:7077 --driver-memory 1g --executor-memory 1g jobs/publish_live_dashboard.py
 dc exec -T spark-client python scripts/verify_live_outputs.py
 dc exec -T spark-client hdfs dfs -ls /ecommerce/live/streaming/reviews
 dc exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 --describe --topic ecommerce-live-reviews""")
p('Các lần chạy cùng checkpoint không được thực hiện đồng thời. Để vận hành thường xuyên dùng DAG live thay vì mở nhiều consumer thủ công. Khi kiểm tra lỗi, xem log/task trước khi quyết định chạy lại; không reset checkpoint nguồn thật chỉ để tạo số lượng tăng.')
h('11.5 URL và dừng/mở lại')
table(['Giao diện','Địa chỉ / kiểm tra'],[['Dashboard tổng','http://localhost:8090/?source=all'],['Đồ thị trượt','http://localhost:8090/?source=all#replay'],['Demo model','http://localhost:8090/demo.html'],['HDFS / Spark / Airflow','http://localhost:9870 / 8081 / 8080'],['Kiểm tra dịch vụ','docker compose --profile orchestration --profile dashboard ps'],['Kiểm tra hồ sơ','python3 scripts/check_submission.py']],[145,CW-145])
block("""# Dừng, giữ data/volumes/checkpoint
 dc stop
# Mở lại môi trường đã dựng
 dc up -d namenode datanode spark-master spark-worker-1 spark-worker-2 spark-client kafka postgres airflow-webserver airflow-scheduler dashboard replay-runner""")
p('Mở lại tiếp tục trạng thái đã lưu; không tự nạp lại 400 review thành 400 mới. Nạp lại từ đầu trên tab replay chỉ tạo run lịch sử riêng. Không dùng down -v hoặc format HDFS trong quy trình giữ dữ liệu này.')
chapter('12. Ma trận mã - lệnh - log - kết quả')
p('Ảnh không đứng riêng làm bằng chứng. Mỗi chức năng dưới đây có source, cách chạy và artifact đối chiếu. Các đường dẫn tương đối tính từ thư mục repository; package chứa log/metadata tương ứng, không chứa .env hay CSV gốc.')
proof=[['Raw HDFS','bootstrap_hdfs.py; hdfs -ls/fsck/-cat | sha256sum','hdfs_upload/blocks/raw_sha256_20261015; dataset_profile','642.967.981 byte; 5 block HEALTHY; hash nguồn khớp'],['Spark clean/SQL','batch_pipeline.py; spark-submit --stage clean/analyze','raw_inspection/data_quality/persisted_validation; batch log','1.300.086 = 74 + 139 + 1.299.873; SQL tổng bằng clean'],['ML','train_sentiment.py; spark-submit','sentiment_train log; sentiment_evaluation/model JSON','12.993 test; LR reg=.1; hash model và 98 serving checks'],['Kafka lịch sử','replay_kafka.py + stream_reviews.py','kafka_topic/producer/consumer log; stream_batch JSON','2.000 offsets; 1.000 review unique; 3 batch lặp rỗng'],['Live thật','collector -> stream --live -> publisher','live topic/task log; immutable generation metadata/cube/index checks','407 review tại generation '+live_gen],['DAG batch/live','dags/*.py; trigger/list-runs','demo_evidence; live_dashboard_validation; logs/*airflow_tasks','Batch 10/10; live snapshot 4/4 success'],['Dashboard','prepare_dashboard/index/server; API','dashboard_validation/demo; clear/combined validation; screenshots','1.910 ô lịch sử; nguồn gộp 1.972 ô × 9 số đếm khớp'],['Replay tháng','prepare_replay.py; replay_months.py','prepared, batch JSON, validation run, Spark verification log','111 tháng; 1.299.873 dòng = unique key; 377 nhóm khớp'],['UI chuyển động/restart','replay.js; validate_replay_browser; verify_replay_restart','replay_browser/restart JSON và log; ảnh 12-15','Mặc định 4; tối đa 12 mốc; dịch trái; resume không lặp tháng']]
table(['Chức năng','Mã / lệnh','Log / output','Kết quả'],proof,[83,126,160,CW-369])
h('12.1 Mốc snapshot và fingerprint')
table(['Đối tượng','Giá trị'],[['Raw SHA-256',audit['sha256']],['Model SHA-256',ml['model_sha256']],['Generation lịch sử',dash_meta['generation']],['Generation live trong ảnh/bảng',live_gen],['Generation gộp',combined['generation']],['Run replay đã đọc lại HDFS',replay['run_id']],['Mã nguồn tại thời điểm dựng',commit]],[167,CW-167])
p('Mỗi snapshot live là thư mục bất biến. Khi pipeline tạo phiên mới, ảnh đã chụp vẫn được đối chiếu với generation của chính ảnh, không ép mọi ảnh cũ bằng current.json mới. report_manifest.json lưu hash của source và artifact mà PDF dùng; MANIFEST_SHA256 trong ZIP kiểm hash các file đóng gói.')
h('12.2 Kiểm thử và tiêu chí chấp nhận')
p('Bộ runtime lưu 16 test đạt (live_runtime_tests_20261015.log). Bộ replay/backend lưu 10 test đạt (replay_unit_20261015.log); đây là hai lượt kiểm tra khác nhau, có phạm vi giao nhau, không cộng thành số test duy nhất. Browser kiểm tra bộ lọc, Clear, debounce, response cũ, retry startup, pause/reset/toggle/slide và live timeline; không có browser error trong artifact đạt.')
p('Kiểm tra dữ liệu toàn tập gồm checksum raw, phương trình đối soát, distinct key, tổng bảng, mọi ô cube với index và đọc lại HDFS replay. Chưa có benchmark nhiều máy, chaos test mọi tình huống hỏng broker/DataNode hoặc bộ nhãn khía cạnh người đọc. Không suy rộng các kiểm tra hiện có thành các bảo đảm chưa thử.')
chapter('13. Nhật ký, lỗi và đóng góp')
h('13.1 Nhật ký có minh chứng')
table(['Mốc / công việc','Lỗi hoặc quyết định','Cách xử lý / bằng chứng'],[['Khôi phục môi trường và dữ liệu','Thiếu runtime/CSV/Git; HEAD Kaggle 404','Docker/WSL; GET archive; SHA nguồn/audit/upload; runtime_build và dataset log'],['Batch toàn tập','Giới hạn RAM; CSV nhiều dòng','Low-memory 2 worker 1 core/1 GiB; schema/multiLine, repartition; count đối soát'],['Mô hình','Lỗi cú pháp thử đầu, output khác UID','Sửa lỗi có log, shared group/setgid/atomic write; train lại đạt'],['Airflow','Task trước thất bại, cần đúng attempt/run','Giữ log lỗi và recovery; run validation_20261015 10/10 success'],['Live và dashboard','Dữ liệu 2026 bị giới hạn ngày lịch sử nếu dùng chung rule','historical_period=False cho live; topic/checkpoint/root riêng'],['Filter/Clear','Ô tháng trống giữ kết quả cũ; Clear chỉ 400 live','Reset toàn nguồn/điều kiện; combined loại 6 ID trùng; browser proof'],['Replay đồ thị','Dồn 2013-2026 gây rối; per-call JVM chậm','Lô tháng riêng; cửa sổ 12 mốc; Hadoop client lâu sống; verify HDFS'],['Hồ sơ PDF hiện tại','Trước đây người dùng chỉ muốn source/kiểm chứng','Yêu cầu mới cho phép PDF; bìa chưa cung cấp thông tin, không bịa cá nhân']],[124,166,CW-290])
p('Nguồn nhật ký: docs/IMPLEMENTATION_JOURNAL.md. Các mốc mới thuộc phiên hoàn thiện 15/10/2026 giờ Việt Nam; log thường dùng UTC. Không biến nhật ký tự động này thành nhật ký hồi tố của sinh viên.')
h('13.2 Git history thực tế')
table(['Commit / ngày giờ','Tác giả','Nội dung'],[[r.split('|',3)[0]+'\n'+r.split('|',3)[1],r.split('|',3)[2],r.split('|',3)[3]] for r in reversed(git_rows)],[134,116,CW-250])
p('Thư mục ban đầu không có lịch sử Git cá nhân. Các commit được tạo trong phiên có tác giả Codex-Automation, phản ánh công việc tự động hóa thực sự. Không thay tác giả hoặc tạo commit giả để phân bổ cho ba thành viên. Source ZIP có GIT_HISTORY và source_history.bundle để kiểm tra.')
h('13.3 Đối chiếu phân công gốc và xác nhận cá nhân')
table(['Ký hiệu phân công','Nhóm việc dự kiến','Sản phẩm có thể kiểm tra','Đóng góp cá nhân'],[['TV1','Nghiên cứu, taxonomy, guideline, gán nhãn, insight, báo cáo','Taxonomy/guideline/insight có; chưa có nhãn người đọc độc lập','Chưa xác nhận; tên/MSSV chưa cung cấp'],['TV2','Nguồn, HDFS, EDA, chia tập, pipeline, dashboard','Audit/HDFS/SQL/split/dashboard và log có thật','Chưa xác nhận; tên/MSSV chưa cung cấp'],['TV3','Tiền xử lý, ML, so sánh, demo, hỗ trợ hồ sơ','Feature/LR/SVM/demo có; chưa fine-tune PhoBERT','Chưa xác nhận; tên/MSSV chưa cung cấp']],[73,140,165,CW-378])
p('File phân công là kế hoạch, không chứng minh ai đã làm. Nhóm cần bổ sung tên/MSSV, thời điểm, file/commit, cách chạy và xác nhận của từng người. Mẫu annotation_sample.csv có 1.000 review với nhãn độc lập còn trống; không báo cáo F1 khía cạnh từ chính luật đã sinh nhãn. Hướng phân tích 4a vẫn có kết quả, nhưng không tuyên bố nghiên cứu ABSA đã được xác thực.')
cite(['docs/PHAN_CONG_GOC.txt','docs/MEMBER_TASK_AUDIT.md','docs/ANNOTATION_GUIDE.md','docs/IMPLEMENTATION_JOURNAL.md'])

chapter('14. Kiến thức và câu hỏi bảo vệ trước giảng viên')
p('Các câu trả lời dưới gắn với chính mã/cấu hình đã chạy. Khi bảo vệ, trình bày khái niệm ngắn, chỉ vào file/lệnh minh chứng, rồi nêu giới hạn. Không đọc thuộc một khẳng định mà cấu hình một máy không chứng minh được.')
h('14.1 HDFS')
qa=[('HDFS khác lưu CSV trong ổ C/D như thế nào?','HDFS quản lý file thành block trong namespace của NameNode và lưu qua DataNode; code dùng URI hdfs://namenode:9000. File trong container /input chỉ là nguồn upload. Em chứng minh bằng -ls, fsck, checksum và spark.read trên URI HDFS, không chỉ bằng ảnh.'),('NameNode có chứa toàn bộ nội dung review không?','Trong vai trò kiến trúc, NameNode giữ metadata/ánh xạ, DataNode giữ block. File CSV dự án có 5 block ở DataNode. Truy vấn NameNode lấy vị trí, đọc dữ liệu qua DataNode. Chỉ có một máy demo nên không chứng minh scale-out nhiều máy. [T2]'),('Vì sao replication=1, có an toàn khi hỏng máy không?','Một DataNode không tạo được ba replica độc lập. Em đặt replication=1 để demo phù hợp tài nguyên; nếu DataNode/volume mất thì không có replica khác để khôi phục. Muốn kiểm thử chịu lỗi phải thêm DataNode, replication và cơ chế HA/backup thích hợp, chưa làm trong bản này.'),('Block size 128 MiB có nghĩa mỗi review 128 MiB không?','Không. Block chia file vật lý, một block chứa nhiều record. CSV 642.967.981 byte có 4 block 134.217.728 byte và block cuối 106.097.069 byte. Record CSV có thể qua newline và không được đếm bằng số block hay số dòng vật lý.'),('Tại sao Parquet và partition theo platform/year?','Sau clean, Spark ghi Parquet cột và partition platform/year; query lọc Shopee năm 2022 có thể bỏ các partition khác và chỉ đọc cột cần. groupBy vẫn có shuffle. Em mở spark_query_plan.txt chỉ PartitionFilters/Exchange, không nói mọi query đều đọc toàn bộ hay đều không shuffle.'),('Dừng container rồi mở lại có mất dữ liệu không?','stop giữ Docker volumes và checkpoint. Em đã test restart replay giữ cursor và không lặp tháng. Đây không phải bằng chứng chịu mất ổ đĩa; format NameNode hoặc xóa volume là thao tác khác và không nằm trong quy trình restart thường.')]
for question,answer in qa:h(question);p(answer)
h('14.2 Kafka và nguồn dữ liệu thật')
qa=[('Tại sao streaming cần Kafka, batch có cần không?','CSV lịch sử đã cố định nên có thể upload HDFS trực tiếp. Nguồn thật phát sinh qua nhiều lượt; Kafka tách collector khỏi Spark consumer, giữ event log và cho xử lý lại. Topic live dùng riêng với dữ liệu lịch sử để không nhầm replay thành review mới.'),('Topic, partition, offset và review_id khác nhau thế nào?','Topic là luồng có tên, partition là nhánh log; offset xác định vị trí trong nhánh. review_id là khóa nghiệp vụ từ Google Play, event_id là phiên bản nội dung. 2.000 offsets có thể chỉ cho 1.000 review unique nếu gửi lại. [T7, T14]'),('Consumer group có vai trò gì?','Trong mô hình Kafka consumer group, các consumer của cùng group chia nhau partition; mỗi partition được giao cho một consumer trong group tại một thời điểm. Với Spark dự án, tiến độ khôi phục cần kiểm tra checkpoint Structured Streaming, không chỉ offset commit của một consumer console khác. [T15]'),('acks=all có nghĩa không bao giờ mất dữ liệu không?','Không. Nó yêu cầu xác nhận từ replica đồng bộ; demo replication=1 không có chịu lỗi nhiều broker. Hệ thống còn dựa vào ack rồi mới nhớ signature, dedup event ID, checkpoint và ghi batch cố định. Chưa chaos-test toàn bộ lỗi nên không tuyên bố end-to-end exactly-once mọi tình huống. [T13]'),('Tại sao 5 phút trôi qua số review vẫn 400?','Mỗi lượt lấy tối đa 100/app, so ID và signature. Không có bản mới/sửa thì gửi 0 event và count giữ nguyên; không nạp lại 400 thành 800. Minh chứng đã có lúc tăng lên 407, từ snapshot thật. “Mới” là mới với collector/phiên bản, không khẳng định mọi review đều vừa được viết trong ngày.'),('Review sửa đổi được xử lý ra sao?','Signature đổi tạo event phiên bản mới. HDFS giữ phiên bản; publisher Window theo review_key và ingested_at chọn latest. Count có thể không đổi nhưng điểm/tỷ lệ đổi. Khi ghép hai nguồn, 6 ID trùng ở snapshot báo cáo dùng bản live thay bản lịch sử.'),('Nếu tắt consumer hoặc nguồn thu thập lỗi?','Consumer tiếp tục theo checkpoint khi mở lại, trong phạm vi Kafka còn giữ dữ liệu. Nếu nguồn thu thập không trả review, collector ghi errors; tất cả app thất bại thì task fail, không tạo fallback giả. Cửa sổ lấy 100/app có giới hạn nên không hứa bù đủ mọi review nếu ngừng lâu.')]
for question,answer in qa:h(question);p(answer)
h('14.3 Airflow')
qa=[('Vì sao cần Airflow khi có thể tự chạy Python?','Chạy tay dùng để kiểm tra từng bước; DAG nêu dependency, lịch, retry và log cho pipeline tái hiện. Batch 10 bước được nối >>; live 4 bước chạy 5 phút/lần. Thành công được đối chiếu bằng run ID và task log, không chỉ ảnh nút xanh.'),('DAG run khác task instance thế nào?','Một DAG run là cả lượt pipeline; task instance là bước cụ thể trong lượt đó. Khi xem lỗi em chọn đúng DAG, run và attempt. Một task success cũ không chứng minh run mới success. [T9]'),('Scheduler, executor, webserver, Postgres làm gì?','Scheduler quyết định khi nào được chạy, LocalExecutor thực thi lệnh; webserver hiển thị/cho điều khiển; Postgres giữ metadata trạng thái. Dữ liệu review vẫn ở HDFS. Em chỉ vào environment và services compose.yaml để chứng minh cấu hình của nhóm. [T11]'),('catchup=False, retries=1 và max_active_runs=1 nghĩa gì?','Dự án không tự chạy bù toàn lịch quá khứ; task lỗi có một lần retry sau delay; DAG tối đa một lượt hoạt động. Nếu lần xử lý vượt 5 phút, lịch sau phải chờ. Mỗi tác vụ phải có cách chạy lại không làm số liệu lặp. [T9, T12]'),('Vì sao dùng availableNow thay một stream chạy mãi?','Airflow task nên kết thúc để bước publish/verify chạy sau. Spark đọc lượng event hiện có rồi dừng, lần lịch sau khôi phục cùng checkpoint. Đây là thu thập liên tục theo lịch với các lượt xử lý hữu hạn, không phải cam kết độ trễ tức thời từng mili giây.'),('Làm sao chứng minh DAG thực sự chạy Spark?','Mở source BashOperator có spark-submit; mở task log có Spark stages/job và đường HDFS; kiểm kết quả Parquet bằng validate_persisted hoặc Spark read. Metadata success chỉ là một phần; output/count/generation mới đối chiếu chức năng.'),('Nếu task xanh nhưng output sai?','Task chỉ xanh vì process exit 0 nếu không tự kiểm tra. Pipeline này có count, unique, checksum và cube/index checks; publisher không đổi pointer trước khi kiểm đạt. Nếu thiếu kiểm tra nội dung thì ảnh Airflow xanh không đủ kết luận đúng.')]
for question,answer in qa:h(question);p(answer)
h('14.4 Spark, phân tích và ML')
qa=[('Lazy evaluation, transformation và action là gì?','select/filter/withColumn tạo kế hoạch; count/write/collect kích hoạt tính toán. persist hữu ích khi nhiều action dùng lại dữ liệu, unpersist giải phóng tài nguyên. Trong clean có nhiều count và write nên dùng MEMORY_AND_DISK; không collect 1,3 triệu review về driver.'),('Tại sao label=0 lại là positive?','Trong code nhóm sao cao gán 0, sao thấp gán 1. Khi tính precision/recall, lớp mục tiêu là 1 = sao thấp. Em chỉ confusion matrix với hàng thật/cột dự đoán, không suy từ chữ positive trong tên biến sang ý nghĩa nghiệp vụ mà không đọc mapping.'),('Accuracy gần 90% có chứng minh phát hiện nguyên nhân không hài lòng không?','Không. Metric đo dự đoán nhóm sao theo nhãn proxy trên split đã định. Khía cạnh là luật đề cập; chưa có ground truth cảm xúc hoặc nguyên nhân nhân quả. Em báo thêm baseline, F1 lớp thấp và lỗi sao cao nhưng văn bản than phiền.'),('Chia 70/10/20 sao số dòng không đúng tỷ lệ đó?','Em hash theo nhóm normalized_content để tránh cùng nội dung lọt nhiều split. Các nhóm có số dòng không đều, nên số dòng train/val/test thực là 54.818/3.105/12.993. Tỷ lệ là bucket nhóm, không phải randomSplit từng dòng.'),('Tại sao dashboard dùng SQLite, có còn Big Data không?','Spark xử lý toàn tập trên HDFS rồi xuất cube/index cho phục vụ. Click bộ lọc dùng kết quả đã tính và chỉ mục, không chạy lại 1,3 triệu dòng mỗi lần. Generation/count và mọi ô tổng hợp được đối chiếu từ HDFS -> output -> index/API.'),('Đồ thị chạy có phải dữ liệu giả không?','Replay copy các lô tháng thật sang HDFS run riêng và chỉ xuất frame sau commit; cuối lượt Spark đọc lại đủ 1.299.873 dòng. Nó được ghi rõ demo lịch sử. Đồ thị thứ hai dùng mốc thu thập thật; không có review mới thì đường có thể phẳng.')]
for question,answer in qa:h(question);p(answer)
h('14.5 Kịch bản thuyết minh khoảng hai phút')
p('“Nhóm phân tích review ứng dụng TMĐT Việt Nam. Dataset raw có 1.300.086 record, khoảng 613 MiB, lưu HDFS với checksum. Spark chuẩn hóa, quarantine 74 và loại 139 ID trùng, còn 1.299.873 review. Spark SQL tạo bảng theo nền tảng/thời gian và luật đề cập khía cạnh; mô hình bổ sung dự đoán nhóm sao bằng TF-IDF + LR/SVM, có split nhóm nội dung và test riêng. Airflow điều phối batch và nhánh Google Play thật mỗi 5 phút. Event mới/sửa qua Kafka vào HDFS, Spark chọn phiên mới và công bố snapshot đã đối soát. Dashboard đọc cube/index, có nguồn tổng và đồ thị trượt 12 tháng. Replay lịch sử được tách khỏi thu thập thật. Nhóm chứng minh bằng source, lệnh, log, output và generation; chưa tuyên bố có nhãn ABSA người đọc hoặc cụm HA nhiều máy.”')
chapter('15. Bảo mật, giới hạn và kết luận')
h('15.1 Loại bí mật khỏi bài nộp')
p('.env chứa giá trị cục bộ và không được đưa vào Git/ZIP/PDF; .env.example chỉ là mẫu trống; Compose tham chiếu biến môi trường. init_local_env.py sinh mật khẩu tại máy. Không in biến mật khẩu/API key/token hoặc chụp màn hình .env. Thông tin username/avatar không được đưa vào output phục vụ; văn bản review vẫn có thể chứa nội dung người dùng tự đăng nên không chép tùy tiện ví dụ cá nhân vào báo cáo.')
p('package_submission.py dùng allowlist, bỏ CSV gốc/SQLite/.env/volumes và kiểm các giá trị bí mật cục bộ không xuất hiện trong byte file đóng gói, kể cả Git bundle. PDF được kiểm cả text trích xuất vì nén PDF có thể che việc tìm secret bằng tìm byte đơn thuần. Freeze nội dung file trước đóng ZIP để các log đang cập nhật không làm sai manifest.')
h('15.2 Giới hạn thực nghiệm')
p('Dữ liệu 642 MB chưa phải quy mô cực lớn; giá trị học tập nằm ở luồng HDFS/Spark/Kafka/Airflow và tái hiện, không ở tuyên bố benchmark terabyte. Một DataNode/broker với replication=1 không có khả năng chịu mất máy bằng replica. Hai worker trên một máy không chứng minh hiệu năng nhiều máy.')
p('Mẫu Google Play bị giới hạn 100/app/lượt; không xác nhận người mua hàng. Luật khía cạnh chưa có precision/recall/F1 do người đọc độc lập; sample nhãn còn trống. TF-IDF theo âm tiết chưa phải tách từ chuyên dụng; split không đánh giá ngoại suy theo thời gian/near-duplicate. K-Means silhouette thấp; chưa triển khai PhoBERT. Các hạn chế này không được che bằng ảnh demo đẹp.')
h('15.3 Kết luận theo yêu cầu')
p('Đã có pipeline batch và thu thập thật, HDFS lưu raw/processed/output/checkpoint, Spark DataFrame/SQL/ML, Kafka producer/consumer, DAG và log Airflow, dashboard có nguồn pipeline và replay kiểm chứng. Hướng phân tích có bảng/biểu đồ/insight; baseline ML có đặc trưng/split/metric và giới hạn. Báo cáo này bổ sung phần PDF đã được yêu cầu mới. Nhóm vẫn cần điền trường/lớp/giảng viên/tên-MSSV và xác nhận đóng góp cá nhân từ bằng chứng thật trước khi ký nộp.')

chapter('Tài liệu tham khảo và chỉ dẫn nguồn')
refs=[('T1','Vietnamese E-commerce Review - Kaggle','https://www.kaggle.com/datasets/hienbm/vietnamese-ecommerce-review'),('T2','Apache Hadoop 3.3.6 - HDFS Architecture','https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html'),('T3','Apache Hadoop 3.3.6 - HDFS User Guide','https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html'),('T4','Hadoop 3.3.6 - FileSystem Shell','https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-common/FileSystemShell.html'),('T5','Spark 3.5.7 - CSV Files','https://spark.apache.org/docs/3.5.7/sql-data-sources-csv.html'),('T6','Spark 3.5.7 - Extracting / Transforming Features','https://spark.apache.org/docs/3.5.7/ml-features.html'),('T7','Apache Kafka - Introduction','https://kafka.apache.org/intro/'),('T8','Spark 3.5.7 - Structured Streaming Guide','https://spark.apache.org/docs/3.5.7/structured-streaming-programming-guide.html'),('T9','Airflow 2.10.5 - DAGs','https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html'),('T10','google-play-scraper - source project','https://github.com/JoMingyu/google-play-scraper'),('T11','Airflow 2.10.5 - Architecture Overview','https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/overview.html'),('T12','Airflow 2.10.5 - Tasks','https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/tasks.html'),('T13','Kafka 3.9 - Producer Configs','https://kafka.apache.org/39/configuration/producer-configs/'),('T14','Kafka 3.9 - Design','https://kafka.apache.org/39/design/design/'),('T15','Kafka 3.9 - Consumer Configs','https://kafka.apache.org/39/configuration/consumer-configs/')]
p('Tài liệu chính thức được đối chiếu ngày 15/10/2026. Các kết quả định lượng của dự án lấy từ file/log nội bộ đã nêu, không lấy từ tài liệu framework. Kiến thức được diễn giải theo cấu hình demo, không sao chép toàn văn tài liệu. Phiên bản Kafka trong runtime là 3.9.0; tài liệu cấu hình theo nhánh 3.9.')
for key,title,url in refs:p(f'<b>[{key}] {escape(title)}</b><br/><link href="{url}" color="#16776d">{escape(url)}</link>','small')
h('Nguồn nội bộ và tính toàn vẹn')
p('Các đường dẫn Đối chiếu trong báo cáo là file thật của dự án. report_manifest.json chứa SHA-256 của mã nguồn và artifact được dùng; package có MANIFEST_SHA256.json. Mục lục/bookmark giúp đến phần kiến thức hoặc mã. Thông tin tên/lớp chưa cung cấp không được suy ra từ tài khoản Windows hay tên thư mục.')
appendices=[('src/review_analytics/spark_ops.py','Schema raw, đọc HDFS, chuẩn hóa/enrich, quarantine, Window dedup và cột phân tích. Dùng chung cho batch và streaming; nhánh live nới phạm vi ngày theo tham số.'),('jobs/batch_pipeline.py','Job batch đầy đủ: inspect, clean, Spark SQL, K-Means và export. Input mặc định là HDFS raw CSV; output là Parquet/JSON/model HDFS. Đọc cùng phần giải thích tại mục 5-7.'),('jobs/train_sentiment.py','Job TF-IDF + LR/SVM đầy đủ, chia nhóm nội dung, trọng số lớp, chọn bằng validation, test cuối, leakage checks, lưu model và đối chiếu phục vụ.'),('jobs/stream_reviews.py','Consumer Spark Structured Streaming cho topic lịch sử/live; parse schema, dedup, foreachBatch, quarantine, checkpoint và availableNow/continuous.'),('jobs/prepare_dashboard.py','Từ HDFS processed tạo cube và serving JSON gzip; có giới hạn collect và kiểm tổng clean_rows.'),('jobs/publish_live_dashboard.py','Chọn phiên bản review mới nhất từ HDFS, tạo generation live, xây index và đối soát trước đổi pointer.'),('jobs/prepare_replay.py','Chuẩn bị lô tháng thật từ HDFS; đọc lại đối soát; --verify-run kiểm đích replay có đủ dòng, unique key và từng nhóm tháng/nền tảng.')]
for i,(path,note) in enumerate(appendices,1):
 chapter(f'Phụ lục A{i}. {path}',new_page=(i==1))
 p(note);raw=content(path);p('SHA-256: '+SOURCES[path],'small')
 p('Số bên trái là dòng gốc. Dấu | ở dòng tiếp là bọc dòng bản in, không thuộc mã thực thi. File nguyên bản trong source ZIP/repository là chuẩn.','small')
 block(raw,numbered=True)
chapter('Phụ lục B. Từ vựng và bản đồ đọc mã')
table(['Thuật ngữ','Giải thích ngắn theo dự án'],[['Batch / stream','Dataset hữu hạn xử lý theo lô / sự kiện đến qua nhiều lượt'],['Schema / DataFrame','Cấu trúc cột-kiểu / bảng dữ liệu phân tán có kế hoạch xử lý'],['Transformation / action','Tạo kế hoạch / kích hoạt tính toán, như count và write'],['Shuffle / partition pruning','Trao đổi theo khóa giữa partition / bỏ vùng dữ liệu không phù hợp filter'],['Quarantine / dedup','Giữ record lỗi cùng lý do / loại bản sao theo khóa định nghĩa'],['Checkpoint / idempotence','Lưu tiến độ/state / chạy lại không làm lặp kết quả logic khi thiết kế đúng'],['Event-time / ingestion-time','Ngày review nguồn / mốc hệ thống tiếp nhận'],['Generation / snapshot','ID phiên output đồng bộ / bộ dữ liệu tại một mốc'],['Precision / recall / F1','Độ đúng dự đoán lớp đích / độ tìm đủ lớp đích / trung bình điều hòa'],['Ground truth / proxy','Nhãn xác thực độc lập / nhãn thay thế như số sao']],[160,CW-160])
table(['Muốn giải thích','Đọc mã'],[['Upload HDFS / fingerprint','scripts/bootstrap_hdfs.py'],['Producer / phiên bản review','jobs/collect_live_reviews.py'],['Consumer / checkpoint','jobs/stream_reviews.py'],['Query / làm sạch / ML','jobs/batch_pipeline.py; src/review_analytics/spark_ops.py; jobs/train_sentiment.py'],['Điều phối / lịch','dags/ecommerce_pipeline.py; dags/live_reviews_pipeline.py'],['Dữ liệu dashboard','jobs/prepare_dashboard.py; scripts/build_dashboard_index.py; dashboard/server.py'],['Đường trượt / reset riêng','jobs/prepare_replay.py; jobs/replay_months.py; dashboard/web/replay.js']],[156,CW-156])
p('Kết thúc báo cáo. Hồ sơ này mô tả đúng sản phẩm và các kiểm chứng đã có; phần thông tin hành chính/đóng góp cá nhân chờ nhóm xác nhận, không làm giả để hoàn chỉnh hình thức.','small')
DEST.parent.mkdir(parents=True,exist_ok=True)
doc=Report(str(DEST),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=48,title='ReviewLens - Bao cao do an Big Data',author='ReviewLens - ho so ky thuat',subject='HDFS, PySpark, Kafka, Airflow, analytics and verified dashboard')
doc.addPageTemplates(PageTemplate(id='report',frames=[Frame(48,48,CW,H-96,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=page))
doc.multiBuild(story)
manifest={'generated_local':NOW.isoformat(),'pdf':str(DEST.relative_to(ROOT)),'pdf_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'source_commit':commit,'historical_generation':dash_meta['generation'],'live_generation':live_gen,'live_reviews':live_meta['processed_rows'],'combined_generation':combined['generation'],'combined_reviews':combined['total_reviews'],'source_hashes':SOURCES,'artifact_hashes':ARTIFACTS,'snippets':snippets,'cover_identity':'Chua cung cap','individual_contributions':'Unverified; no fabricated attribution','references':[{'key':k,'title':t,'url':u} for k,t,u in refs]}
(DEST.parent/'report_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({'pdf':str(DEST),'bytes':DEST.stat().st_size,'source_files':len(SOURCES),'artifacts':len(ARTIFACTS),'snippets':len(snippets)},ensure_ascii=False))
