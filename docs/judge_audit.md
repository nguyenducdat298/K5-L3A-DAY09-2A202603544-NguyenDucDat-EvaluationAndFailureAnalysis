# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (`κ=0.757≥0.6`, `P=0.857≥0.8`, `R=0.800≥0.7`) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không (`κ=0.375<0.6`, `R=0.300<0.7`) | loại |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`) | PASS | FAIL | Người đúng | `"Em đã hoàn tiền cho anh rồi nha..."` — xưng `"em"` + `"nha"` quá suồng sã; sửa rubric cấm đại từ thân mật và từ `"nha/nhé"`. |
| 2 | `H-029` (`tone_ok`) | PASS | FAIL | Người đúng | `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` — giọng ra lệnh dù có `"Dạ, vui lòng"`; sửa rubric bổ sung ví dụ câu mệnh lệnh bị đánh FAIL. |
| 3 | `H-042` (`tone_ok`) | FAIL | PASS | Người đúng | `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` — câu ngắn đủ ý vẫn đạt; sửa rubric nêu rõ không phạt câu ngắn khi không từ chối/không sai sót. |
| 4 | `H-051` (`tone_ok`) | FAIL | PASS | Người đúng | `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` — dùng `"refund"` được phép trong CSKH LogiX; sửa rubric whitelist các thuật ngữ CSKH chuẩn (`refund`, `voucher`). |
| 5 | `H-063` (`tone_ok`) | FAIL? -> Judge nói PASS | FAIL | Người đúng | `"Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ."` — tự ý hứa `"sẽ hoàn thêm"` ngoài kết quả hệ thống; sửa rubric đánh FAIL mọi cam kết tiền ngoài ledger. |
| 6 | `HL-016` (`helpful`) | PASS | FAIL | Người đúng | `"LogiX thành thật xin lỗi... đã hoàn 55.000đ"` nhưng ledger ghi `35.000đ` (`sai tiền`); judge bị đánh lừa bởi văn phong dài dòng lịch sự và không đọc được sổ cái. |

## Kết luận
- **Tiêu chí bị loại:** `helpful` (`n=100`, `TP=9, FP=0, FN=21, TN=70`). Judge bỏ sót 21/30 ca lỗi thực tế (`Recall = 0.300`, `κ = 0.375`), làm tỉ lệ lỗi quan sát giảm ảo từ `0.300` xuống `0.090` (Rogan-Gladen hiệu chỉnh về đúng `0.300`). Nguyên nhân chính: phần lớn lỗi là `sai tiền` so với sổ cái (`HL-015`, `HL-016`, `HL-020`, `HL-028`, `HL-035`, `HL-041`), cộng với thiên kiến chuộng câu dài xin lỗi nhiều (*verbosity bias*), nên LLM judge không thể dùng thay cho code grader đọc ledger.
- **Tiêu chí được giữ lại:** `tone_ok` (`n=100`, `TP=24, FP=4, FN=6, TN=66`, `κ=0.757`, `P=0.857`, `R=0.800`, observed fail `0.280` → Rogan-Gladen corrected `0.300`) đạt cả 3 ngưỡng FLOORS, dùng được cho đánh giá giọng văn sau khi bổ sung rubric 5 điểm trên.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.
