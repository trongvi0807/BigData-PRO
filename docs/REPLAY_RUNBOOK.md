# Đồ thị trượt và nạp dần dữ liệu lịch sử

## Mục đích và nguồn dữ liệu

Màn hình `Đồ thị nạp dần` (`http://localhost:8090/?source=all#replay`) có hai đồ thị. Đồ thị lịch sử là demo replay từ 06/2013 đến 08/2022: 1.299.873 review sau làm sạch của dataset Kaggle. Đồ thị thứ hai dùng các mốc quan sát review Google Play thật. Bốn nền tảng Shopee/Lazada/Sendo/Tiki được bật mặc định; có thể bật/tắt riêng, luôn giữ ít nhất một nền tảng.

Mỗi đồ thị chỉ hiện tối đa 12 mốc. Lịch sử dùng tháng viết review; nguồn thật dùng thời điểm hoàn tất thu thập và kiểm chứng. Đường chuyển động 700 ms giữa tọa độ của các mốc thực; khi có mốc mới, điểm cũ dịch trái. Tỷ lệ 1–2 sao = low/reviews có trục cố định 0–100%; điểm trung bình = rating_sum/reviews có trục 0–5. Tháng không có review của nền tảng không tạo điểm và không nối qua khoảng trống. Các tháng đầu có thể chỉ có Lazada vì các ứng dụng khác chưa có review trong nguồn tại thời điểm đó. Thiết lập giảm chuyển động của trình duyệt được tôn trọng.

## Pipeline thật phía sau demo

1. DAG `prepare_historical_month_replay` chạy `jobs/prepare_replay.py`. Spark đọc trực tiếp `hdfs://namenode:9000/ecommerce/processed/reviews`, phân lô Parquet theo tháng ở `/ecommerce/replay/prepared/<generation>`, tính count/low/rating_sum theo tháng và nền tảng. Spark đọc lại các lô để đối soát toàn bộ chỉ số trước khi công bố `outputs/replay/prepared.json`.
2. Dịch vụ `replay-runner` chạy `jobs/replay_months.py`. Hadoop FileSystem client copy từng thư mục tháng vào thư mục tạm của một run riêng; kiểm tra số file/dung lượng rồi rename sang `loaded/month=YYYY-MM`. Chỉ sau khi lô HDFS hoàn thành mới tăng cursor, cộng số review và công bố frame vào `status.json` cùng log `batch_<month>.json`.
3. Sau 111 lô, Spark đọc lại toàn bộ `/ecommerce/replay/runs/<run_id>/loaded`, kiểm tra số dòng, distinct review_key và toàn bộ 377 nhóm tháng/nền tảng. Kết quả lưu `validation_<run_id>.json` và `runs/<run_id>/spark_verification.log`. Trạng thái chỉ thành `completed` sau khi kiểm chứng đạt.
4. Dashboard polling API `/api/replay` mỗi giây khi mở tab; render tối đa 12 tháng. Các file Parquet không được tải lên trình duyệt.

Dữ liệu batch gốc, toàn bộ chỉ mục dashboard và checkpoint Kafka/HDFS live không bị reset. Chuẩn bị và nạp lại lịch sử không được gọi là review mới thật. Kafka tiếp tục dùng ở DAG thu thập thật; replay theo tháng là pipeline batch trên HDFS.

## Chạy và thao tác

Trên hệ thống đã khởi động core/live theo `docs/LIVE_RUNBOOK.md`:

```bash
bash scripts/start_replay.sh
```

DAG chuẩn bị sẽ tái sử dụng manifest đã kiểm chứng nếu generation lịch sử không đổi. Runner tự chạy lượt đầu. `Tạm dừng` áp dụng sau lô đang nạp; `Tiếp tục` chạy từ cursor đã lưu. `Nạp lại từ đầu` tạo run mới bắt đầu 06/2013, không xóa run trước. Dừng/mở lại container tiếp tục từ trạng thái lưu; nếu lô đã copy xong trước khi checkpoint công bố, runner kiểm tra lại thư mục đích và chỉ cộng lô một lần. Run cũ được giữ làm minh chứng; có thể chiếm thêm dung lượng HDFS khi nạp lại nhiều lượt.

Chọn tốc độ tối thiểu 2, 4 hoặc 8 giây/lô. Thời gian thực tế còn phụ thuộc copy HDFS và đối soát Spark cuối lượt; không cam kết mỗi lô luôn xong đúng thời gian tối thiểu. Với 111 lô, mức 4 giây có phần phát lại tối thiểu khoảng 7,4 phút. Progress là toàn bộ bốn nền tảng, độc lập với các đường đang bật.

Nút `Xem review mới thật` chuyển sang 12 mốc quan sát gần nhất, được `scripts/verify_live_outputs.py` ghi sau khi live pipeline đối soát thành công. Mỗi mốc chứa poll ID, generation, số review mới/sửa và count/low/rating_sum của snapshot HDFS thực tế. Khi không có review mới/sửa, giá trị giữ nguyên; không tạo dao động giả. Live vẫn kiểm tra nguồn mỗi 5 phút; UI đọc mốc mỗi giây.

## Minh chứng và tái hiện

```bash
docker compose exec -T spark-client hdfs dfs -ls /ecommerce/replay
docker compose exec -T spark-client hdfs dfs -du -h /ecommerce/replay
docker compose logs replay-runner
docker compose exec -T airflow-scheduler airflow dags list-runs -d prepare_historical_month_replay --output json
```

Mã kiểm thử: `tests/test_replay.py`, `scripts/validate_replay_browser.py`.
Minh chứng browser: `outputs/replay_browser_validation.json`, `outputs/logs/replay_browser_20261015.log`, ảnh 12/13 trong `outputs/screenshots`.
Minh chứng HDFS: `outputs/replay/prepared.json`, `status.json`, `validation_*.json`, từng batch log và Spark verification log.
Live observation: `outputs/live/observation_timeline.json`.

Lượt HDFS đầu đã đối soát đạt: `054f7512feb1480c9d389ae11f4071e1`, 111 tháng, 1.299.873 dòng = 1.299.873 khóa duy nhất, 377 nhóm tháng/nền tảng. Đây là đóng góp tự động hóa trong phiên hiện tại; không gán thành đóng góp lịch sử của thành viên.
