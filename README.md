# ReviewLens Đồ án Big Data phân tích review TMĐT Việt Nam

Bài toán: tìm các khía cạnh được nhắc trong phản hồi sao thấp của ứng dụng Shopee, Lazada, Sendo, Tiki và dự đoán sao thấp/cao từ văn bản. Nguồn là snapshot Google Play 2013-08/2022, **không phải review sản phẩm, giao dịch hay dữ liệu mới thu thập trực tiếp**.

Phiên hoàn thiện ngày 15/10/2026 dùng WSL Ubuntu và Docker Linux: Hadoop/HDFS 3.3.6, Spark 3.5.7 với hai worker, Kafka 3.9.0, Airflow 2.10.5, dashboard và demo nhập review. Lần chạy mới có log riêng với hậu tố 20261015; artifact lịch sử được giữ ở outputs/history/20261012. Xem [đối chiếu yêu cầu](docs/REQUIREMENTS_AUDIT.md), [kiểm tra phân công](docs/MEMBER_TASK_AUDIT.md), [nhật ký](docs/IMPLEMENTATION_JOURNAL.md).

## Cài đặt trong WSL Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 docker-buildx git
sudo systemctl start docker
sudo usermod -aG docker "$USER"
# Mở lại terminal WSL sau khi thêm group docker.
cd /home/VIDO/projects/bigdata_pro/Bigdata_Review
python3 scripts/download_dataset.py
python3 scripts/init_local_env.py
bash scripts/run_pipeline.sh
```

Dataset công khai tải từ [Kaggle](https://www.kaggle.com/datasets/hienbm/vietnamese-ecommerce-review), không cần ghi API key vào code. Script kiểm tra SHA-256 `9d333c550cb141aa0f3e9f12af43e8e407809031b073b046b61607f84b39bdf9`, 642.967.981 byte; raw có 1.300.086 record/12 trường. Nếu fingerprint thay đổi, script từ chối để nhóm audit snapshot mới. Chạy lại không tải đè CSV đã có. CSV gốc, dữ liệu review, chỉ mục SQLite, .env và volumes không nộp vào Git/ZIP.

`compose.low-memory.yaml` dành cho WSL khoảng 7,6 GiB RAM: hai worker × 1 core/1 GiB, driver 1 GiB. Chạy job tuần tự. Compose gốc dành cho máy nhiều RAM hơn. Hadoop/Spark nằm trong container, không cần Java trên Windows. HDFS giữ raw CSV, quarantine, processed Parquet, bảng SQL, models và checkpoint bằng Docker volumes.

## Mở sản phẩm và kiểm tra HDFS

- Dashboard: http://localhost:8090
- Demo khía cạnh + cảm xúc: http://localhost:8090/demo.html
- HDFS NameNode: http://localhost:9870
- Spark master: http://localhost:8081
- Airflow: http://localhost:8080

```bash
docker compose exec -T spark-client hdfs dfs -ls -h /ecommerce/raw
docker compose exec -T spark-client hdfs dfsadmin -report
docker compose exec -T spark-client hdfs fsck /ecommerce/raw/reviews.csv -files -blocks -locations
docker compose exec -T spark-client hdfs dfs -ls /ecommerce/processed/reviews
python3 scripts/demo_review.py 'Giao hàng quá chậm, ứng dụng bị lỗi.'
```

Pipeline chính đọc **hdfs://namenode:9000/ecommerce/raw/reviews.csv**. Sau làm sạch: 74 quarantine, 139 bản sao ID bị loại, 1.299.873 review hợp lệ; đối soát `raw = quarantine + duplicates + clean`. Khử trùng theo app/reviewid, giữ các ID khác nhau dù cùng văn bản. Spark SQL tổng hợp theo sàn, tháng, sao, khía cạnh, độ dài và độ nhạy spam. Dashboard lấy cube Spark và chỉ mục xuất từ Parquet HDFS, dùng generation để phát hiện cập nhật chưa đồng bộ.

## Kafka và Airflow

Kafka replay snapshot lịch sử qua topic `ecommerce-reviews`, 3 partition, replication=1; không gọi đây là nguồn streaming thực. Structured Streaming đọc Kafka, dedup ID và lưu Parquet/checkpoint HDFS. Chạy producer/consumer hai lần để kiểm tra offset tăng nhưng unique review giữ nguyên. Batch lịch sử không bắt buộc Kafka vì CSV đã là snapshot cố định; Kafka là nhánh mô phỏng thu thập liên tục có bằng chứng riêng.

```bash
# Sau khi batch/ML/streaming ở run_pipeline.sh thành công:
cp outputs/data_quality.json outputs/quality_before_airflow.json
docker compose --profile orchestration build airflow-init
docker compose --profile orchestration up -d postgres kafka
docker compose --profile orchestration run --rm airflow-init
docker compose -f compose.yaml -f compose.low-memory.yaml --profile orchestration up -d airflow-webserver airflow-scheduler
docker compose exec -T airflow-scheduler airflow dags list-import-errors
docker compose exec -T airflow-scheduler airflow dags unpause ecommerce_dissatisfaction_pipeline
docker compose exec -T airflow-scheduler airflow dags trigger ecommerce_dissatisfaction_pipeline --run-id validation_$(date +%Y%m%d_%H%M%S)
```

DAG có 10 task, bao gồm huấn luyện LR/SVM, tạo dashboard và kiểm tra persisted Parquet + mọi ô cube. DAG `schedule=None`, tối đa một run/task hoạt động, retry một lần. Đăng nhập Airflow bằng username `airflow`, mật khẩu `AIRFLOW_ADMIN_PASSWORD` trong `.env` tại máy. Không đưa .env vào bài nộp hoặc ảnh. Thư mục output dùng group 0/setgid theo `scripts/prepare_shared_outputs.py` để Spark và Airflow khác UID có thể ghi kết quả.

Sau run success, lấy đúng run ID để ghi minh chứng:

```bash
docker compose exec -T airflow-scheduler python /workspace/scripts/capture_evidence.py --run-id YOUR_SUCCESSFUL_RUN_ID
docker compose cp airflow-scheduler:/opt/airflow/logs/dag_id=ecommerce_dissatisfaction_pipeline outputs/logs/airflow_tasks
python3 scripts/check_submission.py
```

## Mô hình và giới hạn

TF-IDF âm tiết unigram/bigram + Logistic Regression/Linear SVM; vocabulary/IDF chỉ fit trên train. Chia 70/10/20 theo nhóm nội dung chuẩn hóa, cùng nội dung giữa các sàn không lọt sang tập khác; vẫn chưa giải quyết near-duplicate hay kiểm chứng ngoài thời gian. Chọn hyperparameter bằng validation, báo cáo test cuối và majority baseline. **Nhãn sao 1/2 negative, 4/5 positive chỉ là proxy; bỏ sao 3**. Không có nhãn cảm xúc/khía cạnh do người đọc xác thực; không báo cáo F1 khía cạnh hoặc giả gọi sao là ground truth cảm xúc.

Khía cạnh là luật đề cập đa nhãn; cảm xúc demo ở mức toàn review. K-Means khám phá trên mẫu 25% review sao thấp, silhouette thấp; không diễn giải thành độ chính xác phân loại. [Nghiên cứu liên quan](docs/LITERATURE_REVIEW.md), [guideline nhãn](docs/ANNOTATION_GUIDE.md), [rà soát lỗi](docs/MODEL_ERROR_REVIEW.md).

## Hồ sơ nộp và kiểm chứng

Báo cáo mới: reports/Bao_cao_Bigdata_hoan_thien.pdf. Bộ source/minh chứng: submission/Source_va_minh_chung_Bigdata.zip, tạo bằng scripts/package_submission.py. Kiểm tra outputs/submission_validation.json và MANIFEST_SHA256.json. File phân công gốc được giữ trong docs/PHAN_CONG_GOC.txt; kế hoạch không được dùng làm bằng chứng đóng góp cá nhân. Git history mới ghi công việc tự động thực sự từ phiên này, không tạo commit giả/hồi tố cho sinh viên.

```bash
docker compose exec -T spark-client python -m unittest discover -s tests -v
# Dừng và giữ volumes/dataset/checkpoint:
docker compose -f compose.yaml -f compose.low-memory.yaml --profile orchestration --profile streaming --profile dashboard stop
```
