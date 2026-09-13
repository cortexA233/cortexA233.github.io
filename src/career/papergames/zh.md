---
project:
  title: 闪耀暖暖
  company: 叠纸游戏 · Papergames
  role: 游戏客户端工程师
  period: 2020.12 – 2023.06
  contributions:
    - 设计八叉树与 BVH 混合空间索引，优化射线查询与碰撞检测。
    - 开发拍照模式 UI，实现特效与 3D 角色变换的同步。
title: 游戏客户端工程师 — 叠纸游戏（Infold Games）
summary: 《闪耀暖暖》· 2020.12 – 2023.06
---

在**叠纸游戏（Infold Games / Paper Games）**，使用 C#、Lua 和 Unity 开发《**闪耀暖暖**》的客户端系统。

**任职时间：** 2020 年 12 月 – 2023 年 6 月<br>
**技术栈：** C#、Lua、Unity

## 空间查询与碰撞检测

- 优化 **AABB** 射线检测，并实现支持空间变换的 **OBB**。
- 设计结合**八叉树与 BVH 的混合空间索引**，使全局射线查询速度达到 **Unity `RaycastAll` 的 2–5 倍**。

## 拍照界面与 3D 同步

- 实现支持自定义文字、特效和变换编辑的拍照模式 UI。
- 设计**双锚点算法**，让 UGUI 特效与 3D 角色的位移、旋转和缩放保持同步。
