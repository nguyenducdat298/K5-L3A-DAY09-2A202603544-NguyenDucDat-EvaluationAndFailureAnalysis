# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, `E-seeded_regression-20261117-a9ca` (`reports/eval_seeded_regression.json`) |
| Triệu chứng | `pass_rate` (`TrialPass`) và `refund_amount_correct` fail; `reply` (event `6`) nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` và ledger ghi `refund_vnd=20000, refund_count=1`, trong khi nhãn chuẩn là `status=denied, refund_vnd=0`. |
| Bước sai đầu tiên | Event `3` `model_override`: `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event `1` `handoff` đúng (`claim_id: "C-002"`, `principal_scope: "owner_order_only"`). Event `2` `investigator` đọc đúng DB (`order_id: "O-202"`, `status: "delivered"`, `delay_days: 2`, không đủ ngưỡng trễ ≥ 3 ngày). Đến event `3`, agent tự ý dùng số `5 ngày` trong ticket ghi đè lên `delay_days=2` của DB, dẫn tới event `4` `quote` tính nhầm `20.000đ` và chi tiền sai. |
| Failure mode | `FM-03` (`ticket_trust` — tin ticket hơn DB) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên shape `fixed C-002@11`: event `1` (`handoff`) và `2` (`investigator`, `delay_days: 2`) giống hệt, **không có** event `model_override`; event `3` `quote` tính đúng `amount_vnd: 0, reason: "no_entitlement"`, event `4` `reply` từ chối lịch sự (`ledger=0, status=denied`). |
| Regression test | `test_c002_seed11_override_caught_on_regression_and_clean_on_fixed` trong `src/tests/test_lab9_regression.py` (dùng `DbFactKept` và `RefundAmountCorrect`): fail trên `seeded_regression C-002@11` và pass trên `fixed C-002@11`. |
| Chưa chắc chắn | MockLLM bỏ qua diễn đạt tự nhiên thực tế của LLM khi trích xuất `delay_days` từ câu phức tạp hơn (cần kiểm thêm với prompt thật ở môi trường staging). |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
