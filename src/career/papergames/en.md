---
project:
  title: Shining Nikki
  company: Papergames / Infold Games
  role: Game Client Engineer
  period: 2020.12 – 2023.06
  contributions:
    - Designed a hybrid octree/BVH index for faster spatial queries and collision detection.
    - Built photo-mode UI and synchronized effects with the 3D character's transforms.
title: Game Client Engineer — Infold Games (Paper Games)
summary: Shining Nikki · 2020.12 – 2023.06
---

At **Infold Games (Paper Games)**, I developed client systems for **Shining Nikki** using C#, Lua, and Unity.

**Period:** December 2020 – June 2023<br>
**Technologies:** C#, Lua, Unity

## Spatial queries and collision detection

- Optimized **AABB** ray tests and implemented support for transformed **OBBs**.
- Designed a hybrid **octree/BVH spatial index** that made global ray queries **2–5× faster than Unity's `RaycastAll`**.

## Photo-mode UI and 3D synchronization

- Built photo-mode UI with custom text, effects, and transform editing.
- Designed a **dual-anchor algorithm** that synchronized UGUI effects with a 3D character's translation, rotation, and scale.
