# Báo cáo eval 2 — workshop-bootstrap (with skill)

## Tool
raw-viewer (research)

## Tier
Platform — 3 ngôn ngữ (Python, Shell, Swift), có `Sources/`, `Package.swift`, dấu vết thiết kế/plan.

## Phase
Phase 2 — detect, prove, plan (artifact 3/5, 2 manual chờ xác nhận)

## Thiếu (artifact)
- Mỗi unknown rủi ro phải có spike với go/no-go. (skill: create-technical-spike)
- Mỗi lựa chọn khó đảo ngược phải có ADR. (skill: domain-modeling)

## Chờ xác nhận (manual)
- Thiết kế đã viết và được duyệt (file present)
- Fresh reviewer đã đọc plan và các phát hiện đã sửa

## Tiếp theo
1. Viết spike cho rủi ro chưa chứng minh (Swift gọi Rust core), ghi go/no-go vào `docs/spikes/`. (create-technical-spike)
2. Viết ADR cho lựa chọn khó đảo ngược (một core Rust, hai front end). (domain-modeling)

Skill chạy `phase_status.py raw-viewer` và trích xuất output. Không sửa file nào.