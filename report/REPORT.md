# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Thế Hùng | 2A202602381 | 100% (cài đặt harness, chạy thực nghiệm, curator, phân tích báo cáo) |

- Mô hình (`LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash`, `0.0`, `60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows 11, chạy trực tiếp trong PowerShell
- Số lần chạy tác vụ đã dùng / ngân sách: 18 / 18 lần chạy tác vụ (3 điều kiện x 6 tác vụ)
- Commit của tag `freeze`: Được cập nhật tại mục 7 sau khi đóng băng skill

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Điều kiện `subagents` không cải thiện điểm trên tác vụ đánh giá (dự kiến đạt ~0.60 tương đương baseline) vì các tác tử con dù cộng tác phân rã nhiệm vụ vẫn không thể tự suy đoán ra các quy ước tổ chức ẩn (`rule_*`) nếu không có tri thức ngoài; tuy nhiên số token tiêu thụ sẽ tăng gấp 4-5 lần do chi phí hội thoại và giao việc.
- H2 (skills-auto so với baseline): Điều kiện `skills-auto` sẽ đạt điểm cao nhất trên tác vụ đánh giá (dự kiến tăng vọt từ ~0.60 lên ~0.90) nhờ đọc và áp dụng các skill quy ước do curator đúc kết từ phản hồi của bot kiểm duyệt ở tác vụ học, giúp giải quyết triệt để nhóm lỗi E.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm tác vụ học ở điều kiện `skills-auto` sẽ đạt tuyệt đối (1.00), cao hơn tác vụ đánh giá (~0.90) do tác vụ đánh giá xuất hiện thêm các quy ước tổ chức mới chưa từng có ở tập học (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`), phản ánh giới hạn khái quát hóa tự nhiên của self-evolving agent.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: công cụ tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), công cụ shell (`execute`) và công cụ tác tử con (`task`). Công cụ cho phép chạy lệnh hệ thống là `execute`.
2. Mô tả của công cụ `task` nêu rõ `general-purpose` là subagent phục vụ nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp/nội dung và thực thi tác vụ nhiều bước (có toàn bộ công cụ như tác tử chính). Về ngữ cảnh: subagent hoạt động theo cơ chế phi trạng thái (stateless by default), chỉ nhìn thấy nội dung prompt được giao từ tác tử chính chứ không thừa kế toàn bộ lịch sử hội thoại trước đó.
3. Hướng dẫn hành vi trích từ mô tả:
   - Từ công cụ `task`: *"Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return."*
   - Từ công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | rule_type_hints | E | "RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value." |
| code-learn | rule_regression_tests | E | "RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass." |
| code-learn | rule_changelog | E | "RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets)." |
| data-learn | rule_money_in_cents | E | "RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)." |
| data-learn | rule_meta_block | E | "RULE: answer.json has an object `meta` = {\"source\": <input file name>, \"rows_in\": <number of data rows in the input file, duplicates included>, \"rows_used\": <number of distinct orders with a known amount>}." |
| data-learn | rule_clean_csv | E | "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer cents." |
| logs-learn | rule_service_names | E | "RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service)." |
| logs-learn | rule_sorted_errors | E | "RULE: `errors` is sorted by service, then by timestamp_utc, ascending." |
| logs-learn | rule_schema_header | E | "RULE: the top-level object has \"schema_version\": 2 and \"generated_by\": \"log-triage\"." |

Nhận xét:
- Nhóm lỗi **E (Vi phạm quy ước tổ chức)** chiếm 100% số lỗi thất bại (9/9 checks thất bại trên 3 tác vụ học). Nguyên nhân: Các quy tắc nội bộ của Acme không hề xuất hiện trong tệp đề bài `instruction.md`, do đó tác tử không thể suy đoán nếu không được nạp tri thức từ trước hoặc nhận phản hồi từ bot kiểm duyệt.
- **Bằng chứng phủ định cho các nhóm lỗi A, B, C, D**: Toàn bộ 18/18 check kỹ thuật trên cả 3 tác vụ học đều đạt 100% (`code-learn`: 7/7, `data-learn`: 5/5, `logs-learn`: 6/6). Tác tử đọc kỹ mã nguồn, chạy kiểm thử xác minh và giải quyết nguyên nhân gốc rễ một cách chính xác.
- Một skill được đúc kết từ phản hồi của bot kiểm duyệt hoàn toàn có thể phòng ngừa 100% nhóm lỗi E bằng cách hướng dẫn tác tử tuân thủ quy ước trước khi kết thúc tác vụ.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  1. `explorer`: Phân tích cấu trúc thư mục, đọc kiểm thử lỗi, giải thích nguyên nhân thất bại và dữ liệu đầu vào.
  2. `implementer`: Trực tiếp áp dụng các thay đổi trong mã nguồn hoặc chuyển đổi tệp dữ liệu, chỉ tập trung vào sửa logic theo chỉ định.
  3. `reviewer`: Chạy kiểm thử xác minh độc lập, rà soát lại các ca biên và bảo đảm không làm gãy các thành phần cũ.
- `subagent_calls` ở từng tác vụ: Mỗi tác vụ ghi nhận từ 2 đến 3 lượt gọi subagent (`explorer` -> `implementer` -> `reviewer`).
- Nhận xét về thông tin giao việc: Tác tử chính truyền ngữ cảnh đầy đủ vào trường `prompt` theo đúng cơ chế stateless của subagent, nhận báo cáo dạng text và tổng hợp lại.
- Ảnh hưởng đến token và thời gian: Số lượng token tăng vọt từ ~6,845 token/run (ở baseline) lên ~33,966 token/run (gấp khoảng 5 lần) do mỗi subagent sở hữu một ngữ cảnh riêng và phản hồi chi tiết. Thời gian chạy cũng tăng từ ~16s lên ~45s. Tuy nhiên, điểm số không tăng vì các subagent cũng không thể đoán được các quy ước ẩn của tổ chức (`rule_*`).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 1 lần chạy curator xử lý phản hồi từ 3 tác vụ học của điều kiện `baseline`. Số skill bị xóa do vi phạm quy tắc: 0 (tất cả 3 skill đều tuân thủ định dạng kebab-case, có YAML frontmatter hợp lệ và không chứa từ khóa rò rỉ tập đánh giá).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `acme-python-conventions` | Tổng quát cho mọi gói Python trong tổ chức Acme | Đúng hoàn toàn, đúc kết 3 quy tắc: type hints cho mọi hàm public, bổ sung `tests/test_regressions.py` có >=3 test, và ghi bullet `CHANGELOG.md`. | 8 dòng; `Use when modifying or fixing Python packages to follow Acme engineering standards.`; `skills_read = 1` |
| `acme-data-conventions` | Tổng quát cho các tác vụ xử lý dữ liệu bảng Acme | Đúng hoàn toàn, đúc kết 3 quy tắc: lưu tiền theo cent nguyên, thêm khối `meta` thống kê dòng, và xuất `clean.csv`. | 8 dòng; `Use when processing tabular sales or transaction data to comply with Acme data standards.`; `skills_read = 1` |
| `acme-log-conventions` | Tổng quát cho chuẩn hóa và phân tích nhật ký Acme | Đúng hoàn toàn, đúc kết 3 quy tắc: tên dịch vụ chuyển snake_case, danh sách lỗi sắp xếp theo service rồi timestamp_utc, và thêm header `schema_version: 2`. | 8 dòng; `Use when parsing server logs and performing error triage to follow Acme logging standards.`; `skills_read = 1` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Sẽ được cập nhật sau khi hoàn tất freeze và chạy `compare.py` / `check_breakdown.py`.
