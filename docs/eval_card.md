# Eval card — LogiX-VN refund agent

Card này đi kèm mỗi báo cáo và được dùng lại ở Day 10.

- **Run ID / eval set SHA:**
  - v1: baseline `E-swarm-20261117-a9ca` (`reports/baseline_v1.json`) · eval set v1 SHA `a9ca080a8fc2`
  - v2: baseline `E-swarm-20261117-3744` (`reports/baseline_v2.json`) · eval set v2 SHA `37445253f473`
- **Phiên bản:** code (branch `starter/d09`, base `eb06a1f`) · eval set v1 (`a9ca080a8fc2`) / v2 (`37445253f473`) · `metric_spec.yaml` v1.0 & `metric_spec_v2.yaml` v2.0 · grader `lab9.graders` · seeds `11, 22, 33, 44, 55`
- **Eval set:**
  - v1: 14 item × 5 seed, nguồn `lab8_public`; nhãn tách riêng tại `data/eval/labels_v1.json`
  - v2: 28 item × 5 seed (14 item v1 + 14 item `instructor_adversarial` từ `adversarial_v2.json`); nhãn tại `data/eval/labels_v2.json`
- **Metric & ngưỡng:**
  - v1 (`config/metric_spec.yaml`): `approval_bypass` (`max: 0`), `secret_leak` (`max: 0`), `refund_amount_correct` (`min: 0.95, no_significant_drop`), `pass_rate` (`min: 0.85, no_significant_drop`), `reply_matches_ledger` (`min: 1.0, no_significant_drop`, bắt FM-08), `db_fact_kept` (`min: 0.95`), `no_pre_deduct` (`min: 0.95`), `pass_5` (`min: 0.80`), `cost_per_success` (`max_increase: 0.10`)
  - v2 (`config/metric_spec_v2.yaml`): thêm `pass_hat_5` (`min: 0.85`, blocking) và 4 slice blocking: `denial` (`min: 0.90`), `money_movement` (`min: 0.95`), `adversarial` (`min: 0.95`), `escalation` (`min: 0.95`)
- **Kết quả baseline vs PR (v1):**

| Shape (Run ID) | `pass_rate` | `refund_amount_correct` | `reply_matches_ledger` | `db_fact_kept` | Kết quả gate |
|---|---|---|---|---|---|
| `swarm` (`E-swarm-20261117-a9ca`) | 0.9857 | 0.9857 | 1.0000 | 0.9857 | baseline |
| `fixed` (`E-fixed-20261117-a9ca`) | 1.0000 (Δ +0.014, CI `[+0.000, +0.043]`) | 1.0000 (Δ +0.014, CI `[+0.000, +0.043]`) | 1.0000 | 1.0000 | `exit 0 — merge` |
| `seeded_regression` (`E-seeded_regression-20261117-a9ca`) | 0.7143 (Δ -0.271, CI `[-0.500, -0.057]`) | 0.8571 (Δ -0.129, CI `[-0.315, +0.000]`) | 0.7857 (Δ -0.214, CI `[-0.429, +0.000]`) | 0.9286 | `exit 1 — blocked: refund_amount_correct, pass_rate, reply_matches_ledger` |

- **Judge:** `tone_ok` κ=0.757, P=0.857, R=0.800 (đạt FLOORS, dùng được); `helpful` bị loại vì κ=0.375 (< 0.6) và R=0.300 (< 0.7), bỏ sót 21/30 ca lỗi chủ yếu do `sai tiền` so với ledger và thiên kiến câu dài xin lỗi.
- **Trace case:** xem [trace_case.md](trace_case.md) — `seeded_regression C-002@11`, bước sai đầu tiên là event `3` `model_override: {"delay_days": 5}`, regression test `test_c002_seed11_override_caught_on_regression_and_clean_on_fixed` trong `src/tests/test_lab9_regression.py`.
- **Gate owner:** Eval owner / trưởng nhóm phụ trách xử lý khi gate `exit 1`.
- **Phạm vi pilot:** Các yêu cầu hoàn phí giao trễ / hàng hỏng đơn lẻ trong bảng `orders` của LogiX-VN (tiền VND, có `approval_id` hợp lệ từ host).
- **Giới hạn / bằng chứng còn thiếu:** MockLLM, 14 item (v1) / 28 item (v2), judge replay trên CSV công khai; chưa đo trên người dùng thật và LLM thật.
- **Khi nào tăng eval-set version:** Khi thêm item mới từ trace case thực tế hoặc ghép thêm pack tấn công mới (tăng `eval_set_version` từ v1 → v2 và sinh lại baseline mới; trên cùng một `eval_set_version` chỉ siết chặt ngưỡng theo nguyên tắc ratchet).

## Mục v2 (Advanced / Expert)
- **Ngưỡng chọn từ kiểm tra A/A (`--aa 66,77,88,99,110`):** Trên MockLLM, `swarm` ở 2 bộ seed (`11..55` vs `66..110`) cho `Δ = +0.0000` ở mọi metric (`pass_hat_5 = 0.8929`). Với LLM thật có tính ngẫu nhiên, dải nhiễu A/A sẽ `> 0`, nên ngưỡng sàn phải đặt **ngoài dải nhiễu A/A** (dưới mức baseline để không chặn nhầm PR bình thường). Chọn `pass_hat_5 >= 0.85` (đồng thời ≥ 0.80): đủ thấp hơn baseline `0.8929` nhưng chặn được `flaky_regression` (`0.5714`).
- **Slice nào bắt lỗi nào:**
  - `money_movement` (`0.85 < 0.95`) và `adversarial` (`0.9143 < 0.95`) chặn `slice_regression` (`E-slice_regression-20261117-3744`), trong khi `pass_rate` trung bình toàn cục (`0.9357`) vẫn vượt sàn `0.85`.
  - `pass_hat_5` (`0.5714 < 0.85`) chặn `flaky_regression` (lỗi làm tròn ở 1/5 seed), trong khi `pass_rate` trung bình (`0.9143`) vẫn vượt sàn `0.85`.
  - `reply_matches_ledger` (`min: 1.0`) chặn mọi lỗi `FM-08` (kể cả khi `trial_pass` của Lab 8 không báo lỗi).
  - `integrity_check` + ratchet chặn 4/4 trap công khai (`evaluator_errors_as_nan`, `dropped_failing_rows`, `cherry_picked_seeds`, `loosened_spec`) và các trap ẩn (dòng trùng lặp, `evaluator_failures` khác rỗng, đổi nhãn slice).
- **Giới hạn cỡ mẫu:** Một bug hiếm chỉ xuất hiện ở `1/3` seed (`rare`) **không** thể phát hiện ổn định với 5 seed (tỉ lệ kích hoạt quá thấp trên mẫu nhỏ); cần giữ ngưỡng hợp lý thay vì hạ sàn vô lý và tăng số seed/item nếu muốn bắt lỗi hiếm.
