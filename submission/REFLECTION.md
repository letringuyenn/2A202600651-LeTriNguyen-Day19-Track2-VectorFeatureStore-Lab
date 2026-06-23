# Reflection — Lab 19

**Tên:** _Le Tri Nguyen_
**Cohort:** _A20_
**Path đã chạy:** _lite_

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên golden set 50 queries, **BM25 thắng rõ ở `exact`** vì query chứa đúng technical terms trong corpus nên lexical match rất mạnh. **Hybrid thắng ở `mixed`** vì nó giữ được exact signal từ BM25 nhưng vẫn cộng thêm semantic signal từ vector khi query có phần diễn đạt lại. Ở path lite này, **`paraphrase` lại nghiêng nhẹ về BM25/hybrid hơn semantic** vì embedding `BAAI/bge-small-en-v1.5` không tối ưu cho tiếng Việt nên semantic retrieval bị hụt trên các câu diễn đạt thuần Việt.

Mình **không dùng hybrid** khi bài toán chỉ cần exact match, ranking dễ giải thích, hoặc có budget latency/compute rất chặt vì hybrid phải chạy hai retriever rồi fuse kết quả. Khi corpus và query chủ yếu là paraphrase đa ngôn ngữ với embedding tốt hơn (ví dụ `bge-m3`), pure vector có thể là lựa chọn gọn hơn.

---

## Điều ngạc nhiên nhất khi làm lab này

Điều bất ngờ nhất là hybrid không tự động thắng mọi loại query; chất lượng embedding model ảnh hưởng rất mạnh đến kết quả paraphrase tiếng Việt.

---

## Bonus challenge

- [ ] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
