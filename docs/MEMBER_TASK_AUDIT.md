# Đối chiếu công việc với file phân công gốc

Nguồn ưu tiên là docs/PHAN_CONG_GOC.txt, bản sao nguyên văn file người dùng gửi. Phan_cong_5_tuan.json có kế hoạch chia việc khác; giữ làm tài liệu lịch sử, không thay thế phân công gốc khi nghiệm thu. TV1/TV2/TV3 bên dưới là ký hiệu trong file gốc, chưa có xác nhận ánh xạ ký hiệu với tên người. Danh sách nhóm trong hồ sơ: Huỳnh Quang Sang, Phan Đức Thể, Đỗ Trọng Vĩ.

| Tuần | TV | Công việc và bằng chứng đối chiếu | Kết luận về sản phẩm |
|---|---|---|---|
| 1 | 1 | Nghiên cứu khía cạnh/ABSA/PhoBERT: docs/LITERATURE_REVIEW.md, config/aspects.json | Đã có tổng hợp và taxonomy, không tuyên bố fine-tune PhoBERT |
| 1 | 2 | Nguồn/schema/record/dung lượng: scripts/download_dataset.py, artifacts/audit/dataset_profile.json | Dataset thật được khôi phục; chỉ có review ứng dụng, không có ngành hàng |
| 1 | 3 | Phương pháp xử lý/feature/ML: src/review_analytics/sentiment.py, docs/LITERATURE_REVIEW.md | Có chuẩn hóa và feature baseline; tokenization âm tiết |
| 2 | 1 | Kiến trúc HDFS/blocks/replication: docs/ARCHITECTURE.md, outputs/logs/hdfs_blocks_20261015.txt | Có code/config và kết quả HDFS, replication=1 trong demo một DataNode |
| 2 | 2 | Cài Hadoop/upload/check: compose.yaml, scripts/bootstrap_hdfs.py, log hdfs_upload/report/ls_20261015 | Đã cài và upload snapshot thật, checksum khớp |
| 2 | 3 | Cài Java/Spark, đọc HDFS: infra/Dockerfile, jobs/batch_pipeline.py, outputs/raw_inspection.json | Có runtime, hai worker và Spark đọc 1.300.086 record từ HDFS |
| 3 | 1 | Taxonomy/guideline/multi-aspect: docs/ANNOTATION_GUIDE.md, config/aspects.json | Có guideline; bảy nhóm, đóng gói thuộc product, giá thuộc promotion |
| 3 | 2 | EDA missing/duplicates/stars/platform/time/length: audit, SQL, outputs/*summary.csv | Đã có kết quả và ghi HDFS, có đối soát tổng |
| 3 | 3 | Unicode/lowercase/URL/emoji/teen code/tokenization: text.py và sentiment.py | Giữ raw, nhánh feature xử lý hữu hạn; chưa dùng tách từ tiếng Việt chuyên dụng |
| 4 | 1 | Rà lỗi/nhãn/multi-aspect: docs/MODEL_ERROR_REVIEW.md và annotation_sample.csv | Có rà lỗi AI minh bạch; **chưa có nhãn người đọc độc lập**; không giả ghi thành viên đã gán nhãn |
| 4 | 2 | Train/validation/test, feature/input/output HDFS: jobs/train_sentiment.py, sentiment_evaluation.json | Có split nhóm nội dung, kiểm tra leakage và fit feature trên train |
| 4 | 3 | So sánh LR/SVM, Accuracy/P/R/F1/confusion: sentiment_evaluation.json, sentiment_train log | Đã chạy thực tế; metrics theo nhãn sao thay thế; PhoBERT để hướng phát triển do tài nguyên/nhãn |
| 5 | 1 | Phân tích khía cạnh/sàn/thời gian: bảng CSV, report_charts, báo cáo PDF | Có kết quả, insight và giới hạn diễn giải |
| 5 | 2 | Pipeline toàn dataset, dashboard: DAG, persisted_validation, dashboard_validation, screenshots | Có đối chiếu HDFS → Spark → cube/index → API; trạng thái cuối đọc demo_evidence.json |
| 5 | 3 | Demo review/source/model/report: /demo.html, API /api/predict, demo_review.py, báo cáo PDF | Demo dùng mô hình xuất từ Spark; khía cạnh đề cập và sentiment mức review, chưa phải ABSA được xác thực |

Không thể xác nhận ai làm trước phiên này vì thư mục ban đầu không có .git và không có nhật ký cá nhân. Các sửa mới có commit tác giả Codex automation. Không coi tỷ trọng kế hoạch 1/3 là tỷ trọng đóng góp thực tế. Nhóm cần xác nhận bảng đóng góp theo lịch sử/nhật ký thực tế nếu thầy yêu cầu xác minh cá nhân; trợ lý không thể làm thay việc xác nhận đó.

Yêu cầu chung của thầy cho phép chọn **phân tích dữ liệu**. Vì vậy thiếu nhãn người đọc không ngăn nghiệm thu hướng phân tích, nhưng ngăn tuyên bố đã hoàn thành nghiên cứu ABSA có ground truth như kỳ vọng cao hơn trong kế hoạch. Bản nộp dùng phạm vi phân tích khía cạnh và baseline dự đoán sao, ghi rõ giới hạn này.
