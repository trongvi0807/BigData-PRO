# Cơ sở nghiên cứu và lựa chọn phương pháp

Bài toán là khám phá các khía cạnh được nhắc đến trong phản hồi sao thấp của ứng dụng TMĐT tại Việt Nam và dự đoán nhãn sao thấp/cao từ văn bản. Review ứng dụng không đồng nhất với đánh giá sản phẩm hay giao dịch; không có ngành hàng, giá trị đơn, nhân khẩu học hoặc định danh khách hàng ổn định.

SemEval-2014 Task 4 phân biệt nhận diện khía cạnh với cảm xúc theo từng khía cạnh. Vì vậy câu “hàng tốt nhưng giao lâu” cần hai khía cạnh với polarity khác nhau. Baseline của dự án chỉ nhận diện đề cập; cảm xúc ML ở mức toàn review không được dùng làm polarity của tất cả khía cạnh. Nguồn: Pontiki et al. (2014), https://aclanthology.org/S14-2004/.

PhoBERT là mô hình tiền huấn luyện cho tiếng Việt, có kết quả trên nhiều tác vụ NLP trong nghiên cứu gốc. Kết quả đó không phải metric sentiment của dataset này. Dự án chưa fine-tune PhoBERT vì môi trường WSL hiện khoảng 7,6 GiB RAM, không có bộ nhãn cảm xúc/khía cạnh độc lập do người đọc chốt. Nguồn: Nguyen và Nguyen (2020), https://aclanthology.org/2020.findings-emnlp.92/.

TF-IDF + Logistic Regression và Linear SVM được chọn làm baseline có thể chạy bằng Spark ML, so sánh trên cùng feature và split, lưu mô hình HDFS và export hệ số để demo. Từ vựng/IDF chỉ fit trên train; split theo hash nội dung chuẩn hóa giúp cùng văn bản không rơi vào các tập khác nhau. Feature là âm tiết unigram/bigram, không tuyên bố đã tách từ tiếng Việt như VnCoreNLP. Nguồn thuật toán/API: https://spark.apache.org/docs/3.5.7/ml-classification-regression.html và https://spark.apache.org/docs/3.5.7/ml-features.html.

Văn bản gốc được giữ để kiểm tra bằng mắt. Mô hình chuẩn hóa NFKC, chữ thường, ký tự vô hình, URL, teen code có danh sách hữu hạn; dùng ký tự chữ/số để tokenization. Emoji bị bỏ ở nhánh mô hình, có thể mất tín hiệu cảm xúc; số sao và username không được đưa vào features. Từ phủ định “không” được giữ. Các trường hợp phủ định, trộn cảm xúc, châm biếm, viết không dấu và ngoại lệ teen code cần rà riêng.

Không có nhãn người đọc thì không báo cáo precision/recall/F1 khía cạnh. Metric ML dùng sao 1/2 làm negative, 4/5 làm positive, bỏ sao 3: chỉ đo dự đoán nhãn sao thay thế, không chứng minh hiểu đúng cảm xúc tự nhiên. Giá và khuyến mãi là một nhóm; đóng gói thuộc sản phẩm. Bộ taxonomy 7 nhóm được mô tả trong ANNOTATION_GUIDE.md.
