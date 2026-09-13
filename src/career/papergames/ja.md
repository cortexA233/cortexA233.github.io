---
project:
  title: シャイニングニキ
  company: Papergames / Infold Games
  role: ゲームクライアントエンジニア
  period: 2020.12 – 2023.06
  contributions:
    - 八分木と BVH を組み合わせた空間インデックスを設計し、レイ検索と衝突判定を最適化。
    - 撮影モードの UI を開発し、エフェクトを 3D キャラクターの移動・回転・拡縮と同期。
title: ゲームクライアントエンジニア — Infold Games (Paper Games)
summary: Shining Nikki · 2020.12 – 2023.06
---

**Infold Games（Paper Games）**で、C#、Lua、Unity を使用し、**Shining Nikki** のクライアントシステムを開発しました。

**在籍期間：** 2020 年 12 月 – 2023 年 6 月<br>
**使用技術：** C#、Lua、Unity

## 空間検索と衝突判定

- **AABB** のレイ判定を最適化し、空間変換に対応した **OBB** を実装。
- **八分木と BVH を組み合わせた空間インデックス**を設計し、シーン全体のレイ検索を **Unity の `RaycastAll` と比べて 2～5 倍高速化**しました。

## 撮影モードの UI と 3D 同期

- カスタムテキスト、エフェクト、変換編集に対応する撮影モードの UI を構築。
- **二点アンカーのアルゴリズム**を設計し、UGUI エフェクトを 3D キャラクターの移動・回転・拡縮と同期させました。
