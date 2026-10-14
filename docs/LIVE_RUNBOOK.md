# Thu thập review thật và giao diện tự động

Giao diện bỏ nút Áp dụng/Tìm phản hồi/refresh thủ công. Chọn sàn, tháng, spam hoặc bộ lọc review sẽ tự tải kết quả; từ khóa tìm sau 300 ms ngừng gõ. Đọc snapshot mới mỗi 10 giây, giữ bộ lọc/từ khóa; bỏ response cũ khi người dùng thay lựa chọn nhanh.

Nguồn mới là Google Play công khai, lấy trực tiếp bằng google-play-scraper 1.2.7, lang=vi, country=vn, Sort.NEWEST, tối đa 100 review/app/lần. Không dùng CSV replay khi nguồn không truy cập được. APP_MAP giữ bốn package của đề tài. Ngày review giữ theo nguồn (collector/Spark UTC), ingested_at là thời điểm tiếp nhận; không đổi ngày review thành ngày thu thập. Đây là mẫu review mới nhất có thể lấy, không phải toàn bộ review Google Play hoặc cam kết review mới phát sinh mỗi 5 phút.

DAG live_google_play_reviews tự chạy mỗi 5 phút, max_active_runs=1, bốn task: collect → Kafka/HDFS → tổng hợp/công bố → verify. Các task hữu hạn, không huấn luyện lại mô hình hay đọc lại toàn bộ 1,3 triệu review lịch sử. Một lần lấy không có review mới/đã sửa thì số lượng giữ nguyên, trạng thái lần thu thập vẫn được cập nhật đúng.

Topic ecommerce-live-reviews có 3 partition. Collector giữ ID + fingerprint sau Kafka ack; thay nội dung/sao/ngày nguồn tạo event version mới, nhưng canonical review ID giữ nguyên. Spark checkpoint google-play-live-v1 khử trùng version, ghi Kafka raw (topic/partition/offset/payload) và dữ liệu làm sạch vào HDFS /ecommerce/live. Publisher chọn phiên bản mới nhất cho mỗi review; review chỉnh sửa không làm tăng số unique.

Snapshot live có cube + index + metadata + kiểm tra độc lập mọi ô số đếm. Mỗi generation là thư mục bất biến; current.json chỉ đổi nguyên tử sau khi mọi kiểm tra đạt. Snapshot lịch sử được giữ riêng. Dashboard mặc định dùng dữ liệu mới khi đã có kết quả; bộ lọc Nguồn cho phép chọn Dataset lịch sử để so sánh. Query ?source=historical luôn mở đúng tập gốc.

Khởi động hệ thống trong terminal Ubuntu WSL:

```bash
cd /home/VIDO/projects/bigdata_pro/Bigdata_Review
bash scripts/start_live.sh
```

Khi Docker và scheduler đang chạy, không cần bấm Trigger hoặc chạy producer/Spark thủ công. Container có restart unless-stopped; nếu chủ động stop thì cần start lại. Không tạo Windows Scheduled Task hoặc tự bật máy tính.

Kiểm tra:

```bash
docker compose exec -T airflow-scheduler airflow dags list-runs --dag-id live_google_play_reviews --output json
docker compose exec -T spark-client hdfs dfs -ls /ecommerce/live/raw/kafka
docker compose exec -T spark-client hdfs dfs -ls /ecommerce/live/processed/reviews
docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 --describe --topic ecommerce-live-reviews
curl -fsS 'http://localhost:8090/api/bootstrap?source=live'
```

Browser HDFS: http://localhost:9870/explorer.html#/ecommerce/live . Dashboard: http://localhost:8090 . Airflow: http://localhost:8080 . collection_status.json ghi fetched/new/updated/unchanged và lỗi theo app; lỗi nguồn không được biến thành review giả. live/current.json và generation dashboard_validation.json liên kết với log DAG, Kafka raw và Parquet thật. Nhánh phân tích dùng số sao làm tín hiệu; chưa có nhãn ABSA do người đọc xác thực.

### Toàn bộ dữ liệu và Clear bộ lọc

Nguồn mặc định `Toàn bộ dữ liệu` (`?source=all`) ghép hai đầu ra HDFS đã kiểm chứng: dataset lịch sử và review thật mới thu thập. Phạm vi hiện tại 06/2013–10/2026. Khi review trùng khóa xuất hiện ở hai nguồn, phiên bản live thay thế bản lịch sử trong cả biểu đồ, tìm kiếm và xuất CSV. Không tạo dữ liệu cho các tháng không có review.

Bấm `Clear bộ lọc` hoặc xóa trống một ô tháng sẽ trở về toàn bộ dữ liệu, chọn mọi sàn, toàn khoảng tháng, bỏ loại spam, từ khóa, số sao và khía cạnh. Bộ lọc vẫn tự chạy khi thay đổi. Khi snapshot mới có tháng mới, mốc đầu/cuối tự mở rộng nếu đang chọn toàn khoảng; phạm vi tùy chọn được giữ lại.

Minh chứng: `outputs/clear_filters_validation.json`, `outputs/combined_source_validation.json`, `outputs/logs/clear_filters_browser_20261015.log` và `outputs/screenshots/11-clear-all-data-20261015.png`. Kiểm chứng độc lập: `python3 scripts/verify_combined_source.py`.
