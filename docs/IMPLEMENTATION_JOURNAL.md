# Nhật ký kiểm tra và hoàn thiện

Mốc bên dưới thuộc phiên kiểm tra ngày 15/10/2026 theo Asia/Ho_Chi_Minh. Log chạy ghi UTC, ví dụ 2026-10-14T17 giờ UTC tương ứng 00 giờ ngày 15/10 tại Việt Nam. Đây là nhật ký bổ sung tự động, không phải nhật ký hồi tố của ba sinh viên.

| Mốc | Thực hiện và bằng chứng | Lỗi và xử lý |
|---|---|---|
| Kiểm tra ban đầu | Đọc file phân công gốc và toàn bộ mã, tài liệu, output đã lưu | Bản hiện tại chưa có CSV gốc, Docker/Java, Git; README còn nói về máy cũ |
| Khôi phục môi trường | Cài Docker trong WSL Ubuntu; build Hadoop 3.3.6, Spark 3.5.7, Airflow 2.10.5; log runtime_build/airflow_build_20261015 | Sandbox Windows không khởi động, phải dùng lệnh được người dùng duyệt ngoài sandbox |
| Khôi phục dữ liệu | Tải đúng snapshot Kaggle, SHA-256 khớp; audit 1.300.086 record; upload HDFS, fsck/report/ls | HEAD endpoint tải Kaggle trả 404; GET tải archive thành công |
| Xử lý toàn tập | Batch đọc HDFS, clean/quarantine/dedup/SQL/K-Means, lưu Parquet và xuất bảng | Chạy với hai worker mỗi worker 1 core/1 GiB, driver 1 GiB để phù hợp RAM WSL 7,6 GiB |
| Mô hình bổ sung | TF-IDF + LR/SVM, chọn bằng validation, test riêng theo nhóm nội dung; đối chiếu 100 dự đoán phục vụ với Spark | Một dấu ngoặc thiếu ở script mới: lưu log lỗi rồi sửa; log root tạo không ghi đè được: sửa owner outputs, chạy lại |
| Streaming | Topic 3 partition; producer replay 1.000 review; Structured Streaming → HDFS | Checkpoint và dedup giữ ID qua chạy lại; không giả gọi dữ liệu replay là thu thập trực tiếp |
| Điều phối và demo | DAG mở rộng 10 task; dashboard cube và chỉ mục toàn tập; demo dùng hệ số model xuất từ HDFS/Spark | Công cụ UI bị cùng lỗi sandbox; dùng Chromium headless và HTTP để ghi minh chứng giao diện |
| Hồ sơ nộp | Người dùng chọn chỉ hoàn thiện mã nguồn/kiểm chứng; chưa tạo PDF cuối, bảng đối chiếu yêu cầu/phân công, lịch sử Git mới, ZIP/manifest không có secrets | Không có lịch sử cá nhân cũ để phục dựng; không gán commit tự động cho thành viên |

Kết quả chốt từng bước phải đọc ở outputs/demo_evidence.json, outputs/submission_validation.json và log tương ứng, không lấy dòng kế hoạch làm bằng chứng đã chạy. Các artifact ngày 12/10 được giữ ở outputs/history/20261012; kết quả nộp mới dùng lần chạy 15/10.

## Bổ sung theo yêu cầu review mới thật ngày 15/10/2026

Bỏ nút Áp dụng/Tìm phản hồi/refresh, tự cập nhật bộ lọc/từ khóa/snapshot. Kiểm thử browser trên số đếm thật, giữ lựa chọn và kiểm tra response đến sai thứ tự. Đã kiểm tra nguồn Google Play thật của cả bốn app, mẫu có ngày nguồn trong tháng 10/2026. Bổ sung collector, version fingerprint, topic live riêng, raw/processed HDFS, publisher nguyên tử và DAG định kỳ 5 phút. Dataset lịch sử không bị thay bằng dữ liệu giả; không tạo PDF mới theo lựa chọn trước của người dùng. Kết quả kiểm chứng cuối nằm ở auto_filters_validation.json, live_dashboard_validation.json và log DAG.

- 15/10/2026: Sửa lỗi xóa trống tháng làm giao diện giữ kết quả cũ. Tháng bắt đầu/kết thúc trống được khôi phục theo biên dữ liệu nguồn và tự truy vấn lại; kiểm chứng browser đối chiếu số đếm API thật.

- 15/10/2026: Clear tháng trước đây chỉ giới hạn nguồn live (400 review). Thêm nguồn tổng mặc định, Clear toàn bộ điều kiện, truy vấn hai chỉ mục và thay thế review lịch sử trùng ID bằng bản live. Đối soát thấy 6 khóa trùng: 1.299.873 lịch sử + 400 live − 6 = 1.300.267 review. Kiểm thử 8 tình huống backend và trình duyệt với dữ liệu thật; không tạo review mới giả.

- 15/10/2026: Theo phương án đã chốt, thêm pipeline tháng riêng trên HDFS và đồ thị trượt 12 tháng. Điều chỉnh mặc định bốn nền tảng theo yêu cầu bổ sung. DAG chuẩn bị chạy thành công; lượt nạp đầu đủ 111 tháng / 1.299.873 review, Spark đối soát distinct key và 377 nhóm tháng/nền tảng đạt. Bổ sung timeline quan sát live sau bước kiểm chứng; không đổi nguồn thật thành replay.

- Kiểm chứng cuối: 10 unit tests đạt; browser xác nhận mặc định bốn nền tảng, xóa/reset tạo run riêng, các điểm dịch trái theo lô thực, tạm dừng, đổi chỉ số và chuyển sang timeline thật đều đạt. Restart container giữ checkpoint; sau resume số tháng không trùng và tổng loaded khớp tổng frame. Bộ lọc tự động/Clear toàn bộ dữ liệu tiếp tục đạt.

- Quan sát nguồn thật lúc 08:06 15/10/2026 (giờ Việt Nam): tăng từ 400 lên 407 review, snapshot `5bf111f038694040a540af00fc0d109f`. Toàn bộ dữ liệu tại mốc đối soát: 1,300,274 review sau khử trùng giữa hai nguồn. Minh chứng mỗi browser snapshot được đối chiếu với generation bất biến của chính nó; pipeline thật tiếp tục chạy khi đóng gói.

## 15/10/2026 - Báo cáo cuối và kiến thức bảo vệ

Người dùng yêu cầu mới tạo PDF đầy đủ, mã PySpark kèm giải thích và kiến thức HDFS/Kafka/Airflow; yêu cầu này thay lựa chọn trước chỉ hoàn thiện mã nguồn. scripts/build_final_report.py dựng nội dung từ source, artifact và snapshot có generation; giữ rõ lịch sử/review thật/replay. Thêm câu hỏi bảo vệ, lệnh chạy và phụ lục source. scripts/validate_final_report.py kiểm hash, text, geometry, số liệu và secret; render riêng để rà soát bố cục. Không thay đổi pipeline hay tạo log chạy giả. Thông tin hành chính được người dùng xác nhận chưa cung cấp; đóng góp cá nhân vẫn chưa kiểm chứng.

## 15/10/2026 - Dọn và đóng gói dưới 20 MB

Sau lần dọn 455 ảnh render/cache (85,98 MiB), người dùng yêu cầu xóa phần thừa và tạo ZIP nhỏ hơn 20 MB. Xóa thêm 6 file (6.040.615 byte, 5,76 MiB): Word, ghi chú/phân công CSV cũ và snapshot kiểm tra dọn tạm. Giữ PDF mẫu tại docs/templates/01_Bao_cao_tien_do.pdf và kế hoạch JSON tại docs/PHAN_CONG_5_TUAN.json. Giữ dữ liệu CSV, SQLite, .env, báo cáo mới, ảnh/log và Docker volumes để demo. Trình đóng gói bổ sung PDF tiến độ, đọc kiểm tra bí mật trong mọi PDF, cố định pointer live đã chọn, kiểm ZIP/hash và chặn file từ 20.000.000 byte trở lên. Kết quả ở outputs/package_validation.json.
