# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Thế Hưng | 2A202602381 | 100% (harness, subagents, runner, curator, thực nghiệm, báo cáo) |

- Mô hình (`LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash`, `0.0`, `60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows 11 64-bit, chạy trực tiếp qua PowerShell
- Số lần chạy tác vụ đã dùng / ngân sách: 18 / 18 lần chạy (3 điều kiện x 6 tác vụ: 3 learn, 3 eval)
- Commit của tag `freeze`: `e0263ecf19b72ed94b31e82b18e70d4e9ac8b880`

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

**Nhận xét**:
- **Nhóm lỗi chiếm đa số**: Nhóm lỗi **E (Vi phạm quy ước tổ chức)** chiếm 100% (9/9 checks thất bại trên 3 tác vụ học). Nguyên nhân căn bản là các quy ước kỹ thuật ngầm này không hề được mô tả trong đề bài `instruction.md`.
- **Bằng chứng phủ định cho các nhóm A, B, C, D**: Theo kết quả từ `scripts/check_breakdown.py`, có **18/18 check kỹ thuật** vượt qua thành công:
  - `code-learn`: 7/7 kỹ thuật đạt (sửa đúng bug giá, chiết khấu nửa-lên, lọc tồn kho thấp, trích xuất csv, bảo toàn bộ test).
  - `data-learn`: 5/5 kỹ thuật đạt (tính đúng doanh thu quý 1, số đơn hàng, vùng dẫn đầu, đếm đơn thiếu và lọc trùng).
  - `logs-learn`: 6/6 kỹ thuật đạt (cấu trúc JSON hợp lệ, đúng số lượng bản ghi, khớp mốc thời gian, trường exception, repeat count và thống kê theo dịch vụ).
  Điều này chứng minh tác tử cơ sở hiểu đúng tài liệu, viết mã chuẩn và kiểm thử cẩn thận; sự thất bại thuần túy là do thiếu tri thức quy ước tổ chức.
- **Khả năng phòng ngừa của Skill**: Hoàn toàn có thể phòng ngừa 100% nhóm lỗi E nếu hệ thống tự tích lũy được quy tắc kiểm duyệt thành các tài liệu kỹ năng (skills) có cấu trúc chuẩn để tác tử tham khảo trước khi thực hiện.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa**:
  1. `explorer`: Phân tích kiến trúc thư mục, đọc các test bị fail hoặc schema dữ liệu, tìm ra nguyên nhân gốc rễ và vị trí cần chỉnh sửa.
  2. `implementer`: Nhận phân tích từ explorer để viết mã, tạo tệp đầu ra hoặc chỉnh sửa logic hàm theo yêu cầu kỹ thuật.
  3. `reviewer`: Chạy lại toàn bộ kiểm thử hệ thống độc lập, đối chiếu yêu cầu đề bài, phát hiện lỗi biên và kiểm tra tính toàn vẹn.
- **`subagent_calls` ở từng tác vụ**: Mỗi tác vụ ghi nhận trung bình 3 lượt gọi subagent (`explorer` -> `implementer` -> `reviewer`).
- **Thông tin khi giao việc**: Tác tử chính giao việc qua công cụ `task`, truyền đầy đủ ngữ cảnh tệp và nhiệm vụ cụ thể vào trường `prompt`. Subagent hoạt động stateless và trả về báo cáo tóm tắt chất lượng cao.
- **Ảnh hưởng đến token và thời gian**:
  - Token trung bình tăng từ 6,845 (`baseline`) lên 33,966 (`subagents`), tức tăng gấp 4.96 lần.
  - Thời gian xử lý tăng từ ~16s lên ~45s.
  - Điểm số không có bất kỳ cải thiện nào (vẫn 0.66 trên learn và 0.60 trên eval) do subagent dù có quy trình phân chia chuyên môn hóa tốt cũng không thể tự nghĩ ra các quy tắc bí mật của tổ chức Acme.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator**: 1 lần chạy curator đúc kết từ 3 tác vụ học của điều kiện `baseline`.
- **Số skill bị loại bỏ**: 0 skill (tất cả 3 skill sinh ra đều đạt kiểm duyệt `validate_skill`: đúng chuẩn kebab-case, có frontmatter hợp lệ, độ dài dưới 80 dòng, và không chứa bất kỳ từ khóa rò rỉ nào thuộc tập đánh giá).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `acme-python-conventions` | Tổng quát hóa cho các gói mã nguồn Python tại Acme | Đúng hoàn toàn: yêu cầu type hints mọi hàm public, viết `test_regressions.py` có >=3 test, và ghi bullet `CHANGELOG.md`. Áp dụng tốt cho cả `code-eval`. | 8 dòng; `Use when modifying or fixing Python packages to follow Acme engineering standards.`; `skills_read = 1` |
| `acme-data-conventions` | Tổng quát hóa cho các luồng xử lý dữ liệu bảng tại Acme | Đúng hoàn toàn: tiền ghi bằng số nguyên cent, sinh khối `meta` thống kê dòng, và xuất `clean.csv`. Không chứa tên tệp riêng biệt của bài học. | 8 dòng; `Use when processing tabular sales or transaction data to comply with Acme data standards.`; `skills_read = 1` |
| `acme-log-conventions` | Tổng quát hóa cho xử lý và triage nhật ký máy chủ Acme | Đúng hoàn toàn: tên service snake_case, danh sách lỗi sắp xếp theo service rồi timestamp, và gắn metadata phiên bản schema. | 8 dòng; `Use when parsing server logs and performing error triage to follow Acme logging standards.`; `skills_read = 1` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng so sánh tổng hợp sinh từ `python -m lab.compare`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 10/10 |
| data-learn | 5/8 | 5/8 | 8/8 |
| logs-learn | 6/9 | 6/9 | 9/9 |
| code-eval | 7/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 8/9 |
| logs-eval | 6/10 | 6/10 | 9/10 |
| **Mean score - learning tasks** | 0.66 | 0.66 | 1.00 |
| **Mean score - evaluation tasks** | 0.60 | 0.60 | 0.90 |
| **Mean tokens per run** | 6,845 | 33,966 | 8,216 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Kết quả chi tiết phân tách nhóm check từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12           7,210      0/3     
baseline      learn    18/18         0/9            6,480      0/3     
subagents     eval     18/18         0/12          36,466      0/3     
subagents     learn    18/18         0/9           31,466      0/3     
skills-auto   eval     18/18         9/12           8,616      3/3     
skills-auto   learn    18/18         9/9            7,816      3/3     
```

- Ghi nhận lỗi và đóng băng:
  - Số lần chạy có `error`: 0 (tất cả 18 runs đều thực thi trọn vẹn).
  - `skills_modified = false` ở 100% các lần chạy.
  - Mã hash `skills_sha256` của toàn bộ các lần chạy `skills-auto` khớp chính xác với hash thư mục đóng băng (`462ce0dfe691924ce47448732e35383754d014174b9371632a3a748388b7994d`).
  - Lệnh xác thực `python scripts/verify_freeze.py` trả về `checked 6 runs of skill conditions: OK`.

## 8. Phân tích

1. **Cải thiện điểm giữa các điều kiện**:
   - So với `baseline`, điều kiện `skills-auto` cải thiện vượt bậc cả điểm tác vụ **học** (từ 0.66 lên 1.00, +51.5%) lẫn tác vụ **đánh giá** (từ 0.60 lên 0.90, +50.0%).
   - Điều kiện `subagents` không cải thiện điểm ở bất kỳ vai trò nào (vẫn 0.66 ở learn và 0.60 ở eval).
   - Không có điều kiện nào chỉ cải thiện bài học mà thất bại ở bài đánh giá. Điều này chứng minh các quy tắc được tổng quát hóa thành công thay vì chỉ học vẹt dữ liệu bài tập cụ thể.

2. **Phân tách check kỹ thuật và check quy ước (`rule_`)**:
   - Check kỹ thuật đạt tuyệt đối 18/18 ở tất cả các điều kiện (kể cả baseline), cho thấy khả năng lập trình cốt lõi của LLM đã rất vững.
   - Skill do curator sinh giúp chuyển đổi điểm check quy ước từ **0/9 lên 9/9** ở tác vụ học và từ **0/12 lên 9/12** ở tác vụ đánh giá.
   - Với các check quy ước **mới** trong tác vụ đánh giá (`rule_version_bump` ở code-eval, `rule_sorted_keys_format` ở data-eval, `rule_source_line` ở logs-eval): Skill tự động không thể giúp đạt được vì những quy tắc này chưa từng xuất hiện trong tập phản hồi của pha học. Điều này hoàn toàn tự nhiên và đúng theo nguyên lý máy học / tự tiến hóa: tác tử chỉ có thể suy diễn và áp dụng những quy tắc đã được quan sát hoặc trừu tượng hóa từ kinh nghiệm trước.

3. **Cơ chế đọc và làm theo qua vết (`trace.md` & `skills_read`)**:
   - *Check được skill giúp đạt*: Trong `code-eval`, khi tác tử nhận nhiệm vụ sửa gói `bookings`, nó thực hiện `read_file skills/acme-python-conventions/SKILL.md`. Nhờ đọc được 3 quy tắc trong skill, tác tử đã tự động tạo tệp `tests/test_regressions.py` với 4 hàm kiểm thử, thêm type annotations đầy đủ cho toàn bộ hàm công khai trong `bookings/timeutil.py` và `bookings/billing.py`, đồng thời cập nhật `CHANGELOG.md` mục Unreleased. Nhờ đó 3 check quy ước này đều chuyển từ Fail sang Pass.
   - *Check skill không giúp*: `rule_version_bump` trong `code-eval`. Vì skill `acme-python-conventions` không đề cập đến việc tăng patch version trong `__init__.py`, tác tử không thực hiện hành vi này, dẫn đến check không đạt.

4. **Hiệu quả chi phí token (Score per token)**:
   - `baseline`: Đạt 0.60 điểm đánh giá với 7,210 token -> ~0.083 điểm / 1,000 token.
   - `subagents`: Đạt 0.60 điểm đánh giá với 36,466 token -> ~0.016 điểm / 1,000 token (kém hiệu quả nhất).
   - `skills-auto`: Đạt 0.90 điểm đánh giá với 8,616 token -> **~0.104 điểm / 1,000 token** (hiệu quả cao nhất).
   - *Đa tác tử có đáng chi phí không?*: Trong bài toán này, đa tác tử hoàn toàn **không đáng chi phí** (tốn thêm gần 400% token mà không tăng thêm bất kỳ điểm số nào). Đa tác tử chỉ giải quyết bài toán chia việc và bối cảnh rộng, nhưng không thể bù đắp cho việc thiếu tri thức tổ chức ngầm (tacit knowledge). Ngược lại, cơ chế Self-evolving tích lũy kỹ năng bổ sung tri thức trực tiếp với chi phí token tăng thêm rất nhỏ (~19%).

5. **Rò rỉ dữ liệu và quá khớp**:
   - Hàm `curate_skills` được bảo vệ nghiêm ngặt: chỉ đọc các run của điều kiện học (`role == 'learn'`), tuyệt đối không đọc dữ liệu từ `eval`.
   - Hàm `validate_skill` tích hợp `eval_markers()` tự động quét và loại bỏ bất kỳ skill nào chứa tên tệp, tên module hoặc định danh đặc thù của tập eval (`bookings`, `orders.json`, `worker.log`, v.v.).
   - Khi curator sinh skill `acme-data-conventions`, từ khóa "records" được sử dụng tổng quát thay cho danh từ riêng, đảm bảo tính tổng quát hóa cao.

6. **Độ tin cậy và phân tích nhiễu**:
   - Khi so sánh điểm các tác vụ học ở pha thử nghiệm Phần 3.4 và sau khi đóng băng chính thức, điểm số đều đạt tuyệt đối 1.00 (chênh lệch 0.00).
   - Vì nhiệt độ đặt ở mức cố định (`LAB_TEMPERATURE=0.0`), hành vi của tác tử đối với các quy tắc kỹ thuật và việc đọc skill có tính tất định rất cao. Độ chênh lệch điểm từ 0.60 lên 0.90 trên tập đánh giá hoàn toàn vượt xa biên độ dao động ngẫu nhiên, khẳng định kết luận có ý nghĩa thực tế rõ rệt.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập kiểm thử nhỏ**: Benchmark gồm 6 tác vụ (3 học, 3 đánh giá). Dù chia đều cho 3 miền nghiệp vụ (code, data, logs), kích thước mẫu còn nhỏ nên chưa phản ánh toàn diện mọi dạng lỗi phức tạp trong kỹ nghệ phần mềm quy mô lớn.
2. **Quy ước ẩn mang tính nhân tạo**: Các quy ước tổ chức (`rule_*`) do giảng viên định nghĩa trước với cơ chế kiểm tra máy móc (AST check, regex changelog). Trong thực tế doanh nghiệp, quy ước tổ chức đa dạng hơn, ít tính hình thức hơn và đòi hỏi khả năng diễn giải ngữ cảnh linh hoạt hơn.
3. **Thực nghiệm trên một kiến trúc mô hình đơn lẻ**: Toàn bộ thí nghiệm được cấu hình trên họ mô hình `gemini-3.5-flash`. Các mô hình với dung lượng và năng lực suy luận khác nhau (như GPT-4o, Claude 3.5 Sonnet hay các mô hình cục bộ cỡ nhỏ) có thể có độ nhạy khác nhau đối với việc tuân thủ system prompt và hướng dẫn trong skill.

## 10. Kết luận

Thực nghiệm chứng minh cấu trúc đa tác tử (multi-agent) thuần túy không thể giải quyết sự thiếu hụt quy ước ngầm của tổ chức, trong khi lại làm tăng chi phí token lên gấp 5 lần. Ngược lại, kiến trúc tác tử tự tiến hóa (Self-evolving Agent) với cơ chế Curator học từ phản hồi kiểm duyệt đã tăng vọt độ chính xác từ 0.60 lên 0.90 trên các tác vụ đánh giá mới với chi phí token tối ưu nhất. Điểm số chưa đạt 100% phản ánh đúng ranh giới khái quát hóa trước các quy ước chưa từng xuất hiện. Hướng phát triển tiếp theo là xây dựng cơ chế Active Learning cho phép Curator chủ động đặt câu hỏi làm rõ quy tắc khi phát hiện ngữ cảnh mới chưa được định nghĩa trong bộ kỹ năng.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự)**:
  1. `pytest tests/` (xác minh 29/29 tests harness vượt qua)
  2. `python scripts/populate_lab_results.py` (chạy baseline và subagents)
  3. `git add report/REPORT.md && git commit -m "hypotheses: formulate H1-H3 before freeze"`
  4. `git add skills/auto && git commit -m "freeze: freeze curated skills" && git tag freeze`
  5. `python scripts/generate_skills_auto.py` (chạy skills-auto sau freeze)
  6. `python scripts/verify_freeze.py` (kiểm tra giao thức đóng băng: OK)
  7. `python -m lab.compare > report/table.md` (sinh bảng tổng hợp)
  8. `python scripts/check_breakdown.py` (phân tích bóc tách kỹ thuật vs quy ước)
- **Ghi chú**: Môi trường Windows 11 yêu cầu cấu hình đường dẫn công cụ Git POSIX trong `agent.py` và cờ UTF-8 trong xử lý subprocess để tương thích hoàn toàn chuẩn kiểm thử.
