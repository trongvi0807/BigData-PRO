# Đối chiếu yêu cầu môn Big Data

Theo lựa chọn mới của người dùng, phiên này chỉ hoàn thiện mã nguồn và kiểm chứng; chưa tạo báo cáo PDF cuối hoặc xác nhận đóng góp cá nhân. Không kết luận hồ sơ nộp đã đầy đủ.

Kết luận kỹ thuật cần đọc kèm outputs/submission_validation.json sau kiểm tra cuối: dự án dùng hướng phân tích dữ liệu để đáp ứng yêu cầu số 4, đồng thời bổ sung baseline ML nhãn sao thay thế. Không tự chấm điểm hoặc cam kết 10/10 vì rubric là mức tối đa và còn phụ thuộc đánh giá của thầy.

| Yêu cầu | Mã nguồn/lệnh | Log và kết quả |
|---|---|---|
| 1 Bài toán, nguồn, schema, record, dung lượng | README, audit_dataset.py, download_dataset.py | dataset_profile.json: 12 trường, 1.300.086 record, 642.967.981 byte, SHA-256 nguồn |
| 2 Dữ liệu thực trong HDFS; Kafka khi streaming | bootstrap_hdfs.py, compose/Hadoop XML, replay_kafka.py, stream_reviews.py | hdfs_upload/report/blocks/ls_20261015, Kafka producer/consumer log, stream_batch_*.json; replay ghi rõ nguồn lịch sử |
| 3 Spark đọc trực tiếp HDFS, làm sạch/DataFrame/SQL | jobs/batch_pipeline.py, spark_ops.py, hdfs://namenode:9000/ecommerce/raw/reviews.csv | raw_inspection, data_quality, SQL plan, batch log và Parquet HDFS đối soát persisted_validation |
| 4a Phân tích, chỉ số/bảng/biểu đồ/insight | analyze()/Spark SQL, render_report_charts.py | platform/month/rating/aspect/length/spam CSV, PNG/SVG, báo cáo diễn giải giới hạn |
| 4b ML bổ sung | jobs/train_sentiment.py, shared feature/inference | LR/SVM train/validation/test theo nhóm, Accuracy/P/R/F1/confusion/baseline, HDFS model và sentiment_evaluation.json; nhãn sao proxy |
| 5 Airflow điều phối | dags/ecommerce_pipeline.py, 10 task nối dependency, retry | demo_evidence.json đúng run ID 20261015; logs/airflow_tasks đầy đủ attempt, gồm lỗi và phục hồi |
| Báo cáo PDF, source, README | báo cáo PDF cuối chưa tạo theo lựa chọn của người dùng, Git history, package_submission.py | ZIP source/minh chứng và MANIFEST_SHA256 đối chiếu bytes/hash |
| Dashboard có ảnh và dùng output pipeline | prepare_dashboard.py → build_dashboard_index.py → dashboard/server.py | generation/cube 1.910 ô/index 1.299.873 review, dashboard_validation, dashboard_demo_validation, screenshots mới |
| Nhật ký, lỗi, commit, đóng góp | IMPLEMENTATION_JOURNAL.md, MEMBER_TASK_AUDIT.md, git log | Có nhật ký và commit mới thật; chưa có bằng chứng cá nhân lịch sử, không dựng lại hoặc gán tác giả giả |
| Loại mật khẩu/API key/token | init_local_env.py, .env.example trống, Compose ${...}, .gitignore, allowlist ZIP | .env không tracked và không nằm trong archive; package scanner kiểm tra byte bí mật thực không xuất hiện |

Các PDF/DOCX tiến độ và STATUS cũ chỉ mô tả phiên trước, không phải báo cáo cuối. Điểm chưa thể tự hoàn tất: nhãn người đọc độc lập và xác nhận đóng góp cá nhân. Nhãn AI/nhãn sao không thay thế được hai loại bằng chứng đó. Snapshot này không có ngành hàng và không chứng minh nguyên nhân khách quan của sự không hài lòng.

## Nhánh thu thập mới theo yêu cầu bổ sung

Google Play được lấy trực tiếp, không dùng replay thay nguồn thật. Bốn app đều lấy được 100 review trong lần đầu, raw JSON Kafka được lưu HDFS, processed hiện có 400 unique. DAG live_google_play_reviews chạy định kỳ 5 phút, 4 task; dashboard tự đọc snapshot mới 10 giây và giữ bộ lọc. Nguồn/thời gian/schema/số lượng/dung lượng được đối chiếu qua collection_status/collection_runs, Kafka topic, HDFS logs và metadata generation. Các run thành công tiếp theo giữ 400 unique khi không có review mới/sửa. File hướng dẫn LIVE_RUNBOOK.md và minh chứng live_dashboard_validation.json liên kết với log thực tế. PDF cuối vẫn chưa tạo theo lựa chọn của người dùng.
