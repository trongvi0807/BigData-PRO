# Trạng thái phiên hoàn thiện ngày 15/10/2026

Đây là phiên cài lại trong WSL Ubuntu hiện tại; xem README và REQUIREMENTS_AUDIT để tái hiện. Các bằng chứng ngày 12/10 giữ trong outputs/history/20261012, không dùng để giả nhận cluster hiện tại đã chạy.

Đã cài Docker và build Hadoop/HDFS 3.3.6, Java 11, Spark 3.5.7, Kafka 3.9.0, Airflow 2.10.5. Hai Spark worker, mỗi worker 1 core/1 GiB theo compose.low-memory.yaml. Dataset Kaggle đã tải và checksum khớp, upload HDFS; 13 tests container đều đạt. Batch có 1.299.873 processed, 74 quarantine, 139 duplicates.

Đã bổ sung supervised baseline LR/SVM, split nội dung 70/10/20, feature chỉ fit train, test riêng, kiểm tra portable inference khớp Spark. Nhãn là sao thay thế, không nhãn người đọc. Dashboard/index được tái tạo toàn tập; Kafka đã lưu 1.000 review unique từ replay lịch sử. DAG mới 10 task gồm mô hình và đối soát dashboard; kết quả cuối xem outputs/demo_evidence.json và outputs/submission_validation.json.

Báo cáo cuối: đã bổ sung output/pdf/Bao_cao_Big_Data_ReviewLens.pdf theo yêu cầu mới, có mã PySpark giải thích và kiến thức HDFS/Kafka/Airflow để bảo vệ. Không dùng PDF tiến độ ngày 14/10 làm báo cáo cuối. Nhật ký và kiểm tra phân công ở IMPLEMENTATION_JOURNAL.md và MEMBER_TASK_AUDIT.md. Chưa có lịch sử Git/nhật ký cá nhân cũ để xác nhận đóng góp từng thành viên. Không tạo tác giả/commit hồi tố.

## Giao diện và nguồn tự động mới

Đã bỏ nút Áp dụng/Tìm phản hồi/refresh. Thay bộ lọc/từ khóa tự tải kết quả, đọc snapshot mỗi 10 giây, giữ lựa chọn và bỏ response cũ. Nhánh live_google_play_reviews chạy thật theo lịch 5 phút: lấy Google Play → Kafka ecommerce-live-reviews → HDFS /ecommerce/live → snapshot đã đối soát. Lần đầu có 400 review, 100 mỗi app, ngày nguồn 2025-05 đến 2026-10; 62 ô cube × 9 số đếm khớp index. Nhánh live có 4/4 task success; các lần thu thập lặp không tăng unique. Runtime 16 tests đạt, gồm review mới vượt giới hạn lịch sử và review chỉnh sửa thay score giữ nguyên số unique. Kiểm chứng browser ở auto_filters_validation.json và live_dashboard_validation.json.

- 15/10/2026: Nguồn mặc định toàn bộ dữ liệu, Clear tháng/nút Clear phục hồi mọi điều kiện; phạm vi 06/2013–10/2026. Tổng 1.300.267 review = 1.299.873 lịch sử + 400 live − 6 khóa trùng được bản live thay thế. Đối soát độc lập toàn bộ 1.972 ô tổng hợp × 9 chỉ số khớp SQL của hai chỉ mục.

- Đã thêm màn hình **Đồ thị nạp dần**: bốn nền tảng mặc định, cửa sổ trượt 12 tháng, chuyển động theo lô HDFS thực tế, tạm dừng/tiếp tục/nạp lại riêng demo và chuyển sang đồ thị mốc thu thập thật. Hướng dẫn: [REPLAY_RUNBOOK](REPLAY_RUNBOOK.md). Truy cập `http://localhost:8090/?source=all#replay`.

- Quan sát nguồn thật lúc 08:06 15/10/2026 (giờ Việt Nam): tăng từ 400 lên 407 review, snapshot `5bf111f038694040a540af00fc0d109f`. Toàn bộ dữ liệu tại mốc đối soát: 1,300,274 review sau khử trùng giữa hai nguồn. Minh chứng mỗi browser snapshot được đối chiếu với generation bất biến của chính nó; pipeline thật tiếp tục chạy khi đóng gói.

## Bổ sung báo cáo theo yêu cầu mới - 15/10/2026

Báo cáo dùng source/evidence hash và generation bất biến ghi tại output/pdf/report_manifest.json. validate_final_report.py kiểm tra PDF/text/hash, số liệu và bí mật; kiểm tra trực quan phải được thực hiện riêng trên PDF đã render. Tên trường/lớp/giảng viên/thành viên/MSSV: chưa cung cấp. Không gán commit tự động thành đóng góp cá nhân.
