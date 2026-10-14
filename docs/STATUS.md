# Trạng thái phiên hoàn thiện ngày 15/10/2026

Đây là phiên cài lại trong WSL Ubuntu hiện tại; xem README và REQUIREMENTS_AUDIT để tái hiện. Các bằng chứng ngày 12/10 giữ trong outputs/history/20261012, không dùng để giả nhận cluster hiện tại đã chạy.

Đã cài Docker và build Hadoop/HDFS 3.3.6, Java 11, Spark 3.5.7, Kafka 3.9.0, Airflow 2.10.5. Hai Spark worker, mỗi worker 1 core/1 GiB theo compose.low-memory.yaml. Dataset Kaggle đã tải và checksum khớp, upload HDFS; 13 tests container đều đạt. Batch có 1.299.873 processed, 74 quarantine, 139 duplicates.

Đã bổ sung supervised baseline LR/SVM, split nội dung 70/10/20, feature chỉ fit train, test riêng, kiểm tra portable inference khớp Spark. Nhãn là sao thay thế, không nhãn người đọc. Dashboard/index được tái tạo toàn tập; Kafka đã lưu 1.000 review unique từ replay lịch sử. DAG mới 10 task gồm mô hình và đối soát dashboard; kết quả cuối xem outputs/demo_evidence.json và outputs/submission_validation.json.

Báo cáo cuối: báo cáo PDF cuối chưa tạo theo lựa chọn của người dùng. Không dùng PDF tiến độ ngày 14/10 làm báo cáo cuối. Nhật ký và kiểm tra phân công ở IMPLEMENTATION_JOURNAL.md và MEMBER_TASK_AUDIT.md. Chưa có lịch sử Git/nhật ký cá nhân cũ để xác nhận đóng góp từng thành viên. Không tạo tác giả/commit hồi tố.

## Giao diện và nguồn tự động mới

Đã bỏ nút Áp dụng/Tìm phản hồi/refresh. Thay bộ lọc/từ khóa tự tải kết quả, đọc snapshot mỗi 10 giây, giữ lựa chọn và bỏ response cũ. Nhánh live_google_play_reviews chạy thật theo lịch 5 phút: lấy Google Play → Kafka ecommerce-live-reviews → HDFS /ecommerce/live → snapshot đã đối soát. Lần đầu có 400 review, 100 mỗi app, ngày nguồn 2025-05 đến 2026-10; 62 ô cube × 9 số đếm khớp index. Nhánh live có 4/4 task success; các lần thu thập lặp không tăng unique. Runtime 16 tests đạt, gồm review mới vượt giới hạn lịch sử và review chỉnh sửa thay score giữ nguyên số unique. Kiểm chứng browser ở auto_filters_validation.json và live_dashboard_validation.json.

- 15/10/2026: Nguồn mặc định toàn bộ dữ liệu, Clear tháng/nút Clear phục hồi mọi điều kiện; phạm vi 06/2013–10/2026. Tổng 1.300.267 review = 1.299.873 lịch sử + 400 live − 6 khóa trùng được bản live thay thế. Đối soát độc lập toàn bộ 1.972 ô tổng hợp × 9 chỉ số khớp SQL của hai chỉ mục.
