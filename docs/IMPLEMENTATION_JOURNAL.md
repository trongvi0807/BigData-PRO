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
