# Simulation Walkthrough — Short Version

One compact table per step. Same data as the detailed walkthrough, but scannable in seconds.

**Legend**
- **Faults** — `ID@location` `lv`demand · `?`hidden / `⚡`progress / `✓`repaired
- **RC** — `ID@pos` `v`speed `r`resources · action
- **MPS** — `ID@pos` kW-limit `e`nergy-kWh · state
- **Sections** — LIVE / PARTIAL[dark nodes] / DARK[all nodes]

> V-tie nodes can carry load. V2 has `L_V2` (120 kW, weight 8). V1, V3, V4 are tie-only.


---

## Case1
_3 hidden faults · 2 RC · 1 MPS · 1 Scout_

#### Initial (t=0h)

| | |
|---|---|
| Loads     | 4/11 on · reward 2990 |
| Faults    | DP1@N3-N10 lv4 ? hidden · DP2@N11 lv5 ⚡ 0/5 · DP3@N8-N9 lv4 ? hidden |
| RC        | RC1@N2 v4 r15 →S6(2km) · RC2@N11 v5 r15 REPAIR DP2 |
| Scout     | Scout1@N2 v10 →S3 |
| MPS       | MPS1@N4 600kW e5000 →N10 |
| Switches  | closed: S1,S2,S5  ·  open: S3,S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 1 (t=1h)
> RC1 arrived at S6 (t=1, total=2.0km); Scout Scout1 arrived at S3

| | |
|---|---|
| Loads     | 4/11 on · reward 2990 |
| Faults    | DP1@N3-N10 lv4 ? hidden · DP2@N11 lv5 ⚡ 3/5 · DP3@N8-N9 lv4 ? hidden |
| RC        | RC1@S6 v4 r15 →V1(6km) · RC2@N11 v5 r12 REPAIR DP2 |
| Scout     | Scout1@S3 v10 →S8 |
| MPS       | MPS1@N4 600kW e5000 →N10 |
| Switches  | closed: S1,S2,S5  ·  open: S3,S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 2 (t=2h)
> RC2 repaired DP2 at t=2; Scout Scout1 arrived at S8; MPS1 arrived at N10; MPS1 standing by at N10 — awaiting section clearance; MPS1 standing by at N10 — awaiting section clearance

| | |
|---|---|
| Loads     | 4/11 on · reward 2990 |
| Faults    | DP1@N3-N10 lv4 ? hidden · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ? hidden |
| RC        | RC1@S6 v4 r15 →V1(2km) · RC2@N11 v5 r10 →N10(4km) |
| Scout     | Scout1@S8 v10 →N9 |
| MPS       | MPS1@N10 600kW e5000 idle |
| Switches  | closed: S1,S2,S5  ·  open: S3,S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 3 (t=3h)
> RC1 arrived at V1 (t=3, total=8.0km); RC2 arrived at N10 (t=3, total=4.0km); *** RC RC2 DISCOVERED DP1 at N10 (t=3h) ***; Scout Scout1 arrived at N9; *** Scout Scout1 DISCOVERED DP3 at N9 (t=3h) ***; MPS1 standing by at N10 — awaiting section clearance; RC1 moving to discovered fault DP1; RC2 traversing fault edge to N3

| | |
|---|---|
| Loads     | 4/11 on · reward 2990 |
| Faults    | DP1@N3-N10 lv4 ⚡ 0/4 · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 0/4 |
| RC        | RC1@V1 v4 r15 →N3(12km) · RC2@N10 v5 r10 →N3(2km) |
| Scout     | Scout1@N9 v10 →N8 |
| MPS       | MPS1@N10 600kW e5000 idle |
| Switches  | closed: S1,S2,S5  ·  open: S3,S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 4 (t=4h)
> RC2 arrived at N3 (t=4, total=6.0km); Scout Scout1 arrived at N8; MPS1 standing by at N10 — awaiting section clearance; RC1 redirected to fault DP3; RC2 auto-started repair of DP1

| | |
|---|---|
| Loads     | 4/11 on · reward 2990 |
| Faults    | DP1@N3-N10 lv4 ⚡ 0/4 · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 0/4 |
| RC        | RC1@V1 v4 r15 →N8(14km) · RC2@N3 v5 r10 REPAIR DP1 |
| Scout     | Scout1@N8 v10 →S4 |
| MPS       | MPS1@N10 600kW e5000 idle |
| Switches  | closed: S1,S2,S5  ·  open: S3,S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 5 (t=5h)
> Scout Scout1 arrived at S4; MPS1 standing by at N10 — awaiting section clearance

| | |
|---|---|
| Loads     | 4/11 on · reward 2990 |
| Faults    | DP1@N3-N10 lv4 ⚡ 3/4 · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 0/4 |
| RC        | RC1@V1 v4 r15 →N8(10km) · RC2@N3 v5 r7 REPAIR DP1 |
| Scout     | Scout1@S4 v10 →N12 |
| MPS       | MPS1@N10 600kW e5000 idle |
| Switches  | closed: S1,S2,S5  ·  open: S3,S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 6 (t=6h)
> RC2 repaired DP1 at t=6; Scout Scout1 arrived at N12; MPS1 moving to N8 (restores 1 loads)

| | |
|---|---|
| Loads     | 10/11 on · reward 9800 |
| Faults    | DP1@N3-N10 lv4 ✓ repaired · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 0/4 |
| RC        | RC1@V1 v4 r15 →N8(6km) · RC2@N3 v5 r6 →V4(12km) |
| Scout     | Scout1@N12 v10 →S7 |
| MPS       | MPS1@N10 600kW e5000 →N8 |
| Switches  | closed: S1,S2,S3,S5  ·  open: S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=LIVE · Area5=LIVE |

#### Step 7 (t=7h)
> MPS1 arrived at N8; MPS1 standing by at N8 — awaiting section clearance; MPS1 standing by at N8 — awaiting section clearance

| | |
|---|---|
| Loads     | 10/11 on · reward 9800 |
| Faults    | DP1@N3-N10 lv4 ✓ repaired · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 0/4 |
| RC        | RC1@V1 v4 r15 →N8(2km) · RC2@N3 v5 r6 →V4(7km) |
| Scout     | Scout1@N12 v10 →S7 |
| MPS       | MPS1@N8 600kW e5000 idle |
| Switches  | closed: S1,S2,S3,S5  ·  open: S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=LIVE · Area5=LIVE |

#### Step 8 (t=8h)
> RC1 arrived at N8 (t=8, total=26.0km); Scout Scout1 arrived at S7; MPS1 standing by at N8 — awaiting section clearance; RC2 redirected to fault DP3; RC1 traversing fault edge to N9

| | |
|---|---|
| Loads     | 10/11 on · reward 9800 |
| Faults    | DP1@N3-N10 lv4 ✓ repaired · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 0/4 |
| RC        | RC1@N8 v4 r15 →N9(4km) · RC2@N3 v5 r6 →N8(2km) |
| Scout     | Scout1@S7 v10 idle |
| MPS       | MPS1@N8 600kW e5000 idle |
| Switches  | closed: S1,S2,S3,S5  ·  open: S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=LIVE · Area5=LIVE |

#### Step 9 (t=9h)
> RC1 arrived at N9 (t=9, total=30.0km); RC2 arrived at N8 (t=9, total=18.0km); MPS1 standing by at N8 — awaiting section clearance; RC1 auto-started repair of DP3; RC2 traversing fault edge to N9

| | |
|---|---|
| Loads     | 10/11 on · reward 9800 |
| Faults    | DP1@N3-N10 lv4 ✓ repaired · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 0/4 |
| RC        | RC1@N9 v4 r15 REPAIR DP3 · RC2@N8 v5 r6 →N9(4km) |
| Scout     | Scout1@S7 v10 idle |
| MPS       | MPS1@N8 600kW e5000 idle |
| Switches  | closed: S1,S2,S3,S5  ·  open: S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=LIVE · Area5=LIVE |

#### Step 10 (t=10h)
> RC2 arrived at N9 (t=10, total=22.0km); MPS1 standing by at N8 — awaiting section clearance

| | |
|---|---|
| Loads     | 10/11 on · reward 9800 |
| Faults    | DP1@N3-N10 lv4 ✓ repaired · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ⚡ 3/4 |
| RC        | RC1@N9 v4 r12 REPAIR DP3 · RC2@N9 v5 r6 →V4(6km) |
| Scout     | Scout1@S7 v10 idle |
| MPS       | MPS1@N8 600kW e5000 idle |
| Switches  | closed: S1,S2,S3,S5  ·  open: S4,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=DARK[N8,N9] · Area4=LIVE · Area5=LIVE |

#### Step 11 (t=11h)
> RC1 repaired DP3 at t=11

| | |
|---|---|
| Loads     | 11/11 on · reward 11800 |
| Faults    | DP1@N3-N10 lv4 ✓ repaired · DP2@N11 lv5 ✓ repaired · DP3@N8-N9 lv4 ✓ repaired |
| RC        | RC1@N9 v4 r11 idle · RC2@N9 v5 r6 →V4(1km) |
| Scout     | Scout1@S7 v10 idle |
| MPS       | MPS1@N8 600kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4,S5  ·  open: S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

**✓ All faults repaired at t=11h.**


---

## Case2
_3 hidden faults · 2 RC · 1 MPS · 1 Scout_

#### Initial (t=0h)

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N10-N12 lv5 ? hidden · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ? hidden |
| RC        | RC1@N2 v4 r15 →S3(0km) · RC2@N9 v5 r15 →N8(4km) |
| Scout     | Scout1@N2 v10 →S2 |
| MPS       | MPS1@N11 600kW e4000 idle |
| Switches  | closed: S2,S4  ·  open: S1,S3,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 1 (t=1h)
> RC1 arrived at S3 (t=1, total=0.0km); RC2 arrived at N8 (t=1, total=4.0km); Scout Scout1 arrived at S2; MPS1 standing by at N11 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N10-N12 lv5 ? hidden · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ? hidden |
| RC        | RC1@S3 v4 r15 →S6(2km) · RC2@N8 v5 r15 →S4(2km) |
| Scout     | Scout1@S2 v10 →S1 |
| MPS       | MPS1@N11 600kW e4000 idle |
| Switches  | closed: S2,S4  ·  open: S1,S3,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 2 (t=2h)
> RC1 arrived at S6 (t=2, total=2.0km); RC2 arrived at S4 (t=2, total=6.0km); Scout Scout1 arrived at S1; MPS1 standing by at N11 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N10-N12 lv5 ? hidden · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ? hidden |
| RC        | RC1@S6 v4 r15 →V1(6km) · RC2@S4 v5 r15 →N3(0km) |
| Scout     | Scout1@S1 v10 →N6 |
| MPS       | MPS1@N11 600kW e4000 idle |
| Switches  | closed: S2,S4  ·  open: S1,S3,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 3 (t=3h)
> RC2 arrived at N3 (t=3, total=6.0km); Scout Scout1 arrived at N6; *** Scout Scout1 DISCOVERED DP3 at N6 (t=3h) ***; MPS1 standing by at N11 — awaiting section clearance; RC1 redirected to fault DP3

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N10-N12 lv5 ? hidden · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ⚡ 0/3 |
| RC        | RC1@S6 v4 r15 →N6(6km) · RC2@N3 v5 r15 →N10(2km) |
| Scout     | Scout1@N6 v10 →N7 |
| MPS       | MPS1@N11 600kW e4000 idle |
| Switches  | closed: S2,S4  ·  open: S1,S3,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 4 (t=4h)
> RC2 arrived at N10 (t=4, total=8.0km); *** RC RC2 DISCOVERED DP1 at N10 (t=4h) ***; Scout Scout1 arrived at N7; MPS1 standing by at N11 — awaiting section clearance; RC2 traversing fault edge to N12

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N10-N12 lv5 ⚡ 0/5 · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ⚡ 0/3 |
| RC        | RC1@S6 v4 r15 →N6(2km) · RC2@N10 v5 r15 →N12(2km) |
| Scout     | Scout1@N7 v10 →V1 |
| MPS       | MPS1@N11 600kW e4000 idle |
| Switches  | closed: S2,S4  ·  open: S1,S3,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 5 (t=5h)
> RC1 arrived at N6 (t=5, total=12.0km); RC2 arrived at N12 (t=5, total=10.0km); Scout Scout1 arrived at V1; MPS1 standing by at N11 — awaiting section clearance; RC1 traversing fault edge to N7; RC2 auto-started repair of DP1

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N10-N12 lv5 ⚡ 0/5 · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ⚡ 0/3 |
| RC        | RC1@N6 v4 r15 →N7(2km) · RC2@N12 v5 r15 REPAIR DP1 |
| Scout     | Scout1@V1 v10 →V2 |
| MPS       | MPS1@N11 600kW e4000 idle |
| Switches  | closed: S2,S4  ·  open: S1,S3,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 6 (t=6h)
> RC1 arrived at N7 (t=6, total=14.0km); Scout Scout1 arrived at V2; MPS1 standing by at N11 — awaiting section clearance; RC1 auto-started repair of DP3

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N10-N12 lv5 ⚡ 3/5 · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ⚡ 0/3 |
| RC        | RC1@N7 v4 r15 REPAIR DP3 · RC2@N12 v5 r12 REPAIR DP1 |
| Scout     | Scout1@V2 v10 →V3 |
| MPS       | MPS1@N11 600kW e4000 idle |
| Switches  | closed: S2,S4  ·  open: S1,S3,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 7 (t=7h)
> RC1 repaired DP3 at t=7; RC2 repaired DP1 at t=7; Scout Scout1 arrived at V3; MPS1 moving to N13 (restores 1 loads)

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ? hidden · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N7 v4 r12 →S8(12km) · RC2@N12 v5 r10 →S5(12km) |
| Scout     | Scout1@V3 v10 →N13 |
| MPS       | MPS1@N11 600kW e4000 →N13 |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 8 (t=8h)
> Scout Scout1 arrived at N13; *** Scout Scout1 DISCOVERED DP2 at N13 (t=8h) ***; RC1 redirected to fault DP2

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N7 v4 r12 →N13(18km) · RC2@N12 v5 r10 →S5(7km) |
| Scout     | Scout1@N13 v10 →S7 |
| MPS       | MPS1@N11 600kW e4000 →N13 |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 9 (t=9h)
> Scout Scout1 arrived at S7; MPS1 arrived at N13; MPS1 standing by at N13 — awaiting section clearance; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N7 v4 r12 →N13(14km) · RC2@N12 v5 r10 →S5(2km) |
| Scout     | Scout1@S7 v10 →V4 |
| MPS       | MPS1@N13 600kW e4000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 10 (t=10h)
> RC2 arrived at S5 (t=10, total=22.0km); Scout Scout1 arrived at V4; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N7 v4 r12 →N13(10km) · RC2@S5 v5 r10 idle |
| Scout     | Scout1@V4 v10 →S8 |
| MPS       | MPS1@N13 600kW e4000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 11 (t=11h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N7 v4 r12 →N13(6km) · RC2@S5 v5 r10 idle |
| Scout     | Scout1@V4 v10 →S8 |
| MPS       | MPS1@N13 600kW e4000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 12 (t=12h)
> Scout Scout1 arrived at S8; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N7 v4 r12 →N13(2km) · RC2@S5 v5 r10 idle |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N13 600kW e4000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 13 (t=13h)
> RC1 arrived at N13 (t=13, total=36.0km); MPS1 standing by at N13 — awaiting section clearance; RC1 auto-started repair of DP2

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N13 v4 r12 REPAIR DP2 · RC2@S5 v5 r10 idle |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N13 600kW e4000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 14 (t=14h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ⚡ 3/6 · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N13 v4 r9 REPAIR DP2 · RC2@S5 v5 r10 idle |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N13 600kW e4000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 15 (t=15h)
> RC1 repaired DP2 at t=15

| | |
|---|---|
| Loads     | 11/11 on · reward 11800 |
| Faults    | DP1@N10-N12 lv5 ✓ repaired · DP2@N13 lv6 ✓ repaired · DP3@N6-N7 lv3 ✓ repaired |
| RC        | RC1@N13 v4 r6 idle · RC2@S5 v5 r10 idle |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N13 600kW e4000 idle |
| Switches  | closed: S1,S2,S3,S4,S5  ·  open: S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

**✓ All faults repaired at t=15h.**


---

## Case3
_3 hidden faults · 2 RC · 1 MPS · 1 Scout_

#### Initial (t=0h)

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ? hidden · DP3@N2-N6 lv4 ? hidden |
| RC        | RC1@N1 v5 r12 →S6(0km) · RC2@V2 v4 r12 →N12(2km) |
| Scout     | Scout1@N1 v10 →S1 |
| MPS       | MPS1@N2 400kW e3000 idle |
| Switches  | closed: S3,S4,S5  ·  open: S1,S2,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 1 (t=1h)
> RC1 arrived at S6 (t=1, total=0.0km); RC2 arrived at N12 (t=1, total=2.0km); Scout Scout1 arrived at S1; MPS1 standing by at N2 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ? hidden · DP3@N2-N6 lv4 ? hidden |
| RC        | RC1@S6 v5 r12 →S2(2km) · RC2@N12 v4 r12 →N10(2km) |
| Scout     | Scout1@S1 v10 →N2 |
| MPS       | MPS1@N2 400kW e3000 idle |
| Switches  | closed: S3,S4,S5  ·  open: S1,S2,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 2 (t=2h)
> RC1 arrived at S2 (t=2, total=2.0km); RC2 arrived at N10 (t=2, total=4.0km); Scout Scout1 arrived at N2; *** Scout Scout1 DISCOVERED DP3 at N2 (t=2h) ***; MPS1 standing by at N2 — awaiting section clearance; RC1 moving to discovered fault DP3

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ? hidden · DP3@N2-N6 lv4 ⚡ 0/4 |
| RC        | RC1@S2 v5 r12 →N2(0km) · RC2@N10 v4 r12 →N3(2km) |
| Scout     | Scout1@N2 v10 →S3 |
| MPS       | MPS1@N2 400kW e3000 idle |
| Switches  | closed: S3,S4,S5  ·  open: S1,S2,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 3 (t=3h)
> RC1 arrived at N2 (t=3, total=2.0km); RC2 arrived at N3 (t=3, total=6.0km); Scout Scout1 arrived at S3; MPS1 standing by at N2 — awaiting section clearance; RC1 traversing fault edge to N6

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ? hidden · DP3@N2-N6 lv4 ⚡ 0/4 |
| RC        | RC1@N2 v5 r12 →N6(4km) · RC2@N3 v4 r12 →S4(0km) |
| Scout     | Scout1@S3 v10 →N6 |
| MPS       | MPS1@N2 400kW e3000 idle |
| Switches  | closed: S3,S4,S5  ·  open: S1,S2,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 4 (t=4h)
> RC1 arrived at N6 (t=4, total=6.0km); *** RC RC1 DISCOVERED DP2 at N6 (t=4h) ***; RC2 arrived at S4 (t=4, total=6.0km); Scout Scout1 arrived at N6; MPS1 standing by at N2 — awaiting section clearance; RC1 auto-started repair of DP3; RC2 moving to discovered fault DP2

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ⚡ 0/4 · DP3@N2-N6 lv4 ⚡ 0/4 |
| RC        | RC1@N6 v5 r12 REPAIR DP3 · RC2@S4 v4 r12 →N6(12km) |
| Scout     | Scout1@N6 v10 →N7 |
| MPS       | MPS1@N2 400kW e3000 idle |
| Switches  | closed: S3,S4,S5  ·  open: S1,S2,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 5 (t=5h)
> RC1 repaired DP3 at t=5; Scout Scout1 arrived at N7; MPS1 standing by at N2 — awaiting section clearance; RC1 traversing fault edge to N7

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ⚡ 0/4 · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N6 v5 r8 →N7(2km) · RC2@S4 v4 r12 →N6(8km) |
| Scout     | Scout1@N7 v10 →V1 |
| MPS       | MPS1@N2 400kW e3000 idle |
| Switches  | closed: S3,S4,S5  ·  open: S1,S2,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 6 (t=6h)
> RC1 arrived at N7 (t=6, total=8.0km); Scout Scout1 arrived at V1; MPS1 standing by at N2 — awaiting section clearance; RC1 auto-started repair of DP2

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ⚡ 0/4 · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N7 v5 r8 REPAIR DP2 · RC2@S4 v4 r12 →N6(4km) |
| Scout     | Scout1@V1 v10 →V3 |
| MPS       | MPS1@N2 400kW e3000 idle |
| Switches  | closed: S3,S4,S5  ·  open: S1,S2,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 7 (t=7h)
> RC1 repaired DP2 at t=7; Scout Scout1 arrived at V3; MPS1 moving to N5 (restores 1 loads)

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N7 v5 r4 →N4(10km) · RC2@S4 v4 r12 →N6(0km) |
| Scout     | Scout1@V3 v10 →S7 |
| MPS       | MPS1@N2 400kW e3000 →N5 |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 8 (t=8h)
> RC2 arrived at N6 (t=8, total=18.0km); Scout Scout1 arrived at S7; MPS1 arrived at N5; MPS1 standing by at N5 — awaiting section clearance; MPS1 standing by at N5 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N7 v5 r4 →N4(5km) · RC2@N6 v4 r12 →N5(10km) |
| Scout     | Scout1@S7 v10 →V4 |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 9 (t=9h)
> Scout Scout1 arrived at V4; MPS1 standing by at N5 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ? hidden · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N7 v5 r4 →N4(0km) · RC2@N6 v4 r12 →N5(6km) |
| Scout     | Scout1@V4 v10 →S8 |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 10 (t=10h)
> RC1 arrived at N4 (t=10, total=18.0km); *** RC RC1 DISCOVERED DP1 at N4 (t=10h) ***; MPS1 standing by at N5 — awaiting section clearance; RC2 redirected to fault DP1; RC1 traversing fault edge to N5

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ⚡ 0/5 · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N4 v5 r4 →N5(2km) · RC2@N6 v4 r12 →N4(8km) |
| Scout     | Scout1@V4 v10 →S8 |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 11 (t=11h)
> RC1 arrived at N5 (t=11, total=20.0km); Scout Scout1 arrived at S8; MPS1 standing by at N5 — awaiting section clearance; RC1 auto-started repair of DP1

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ⚡ 0/5 · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N5 v5 r4 REPAIR DP1 · RC2@N6 v4 r12 →N4(4km) |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 12 (t=12h)
> RC1 out of resources at t=12; MPS1 standing by at N5 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ⚡ 4/5 · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N5 v5 r0 idle · RC2@N6 v4 r12 →N4(0km) |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 13 (t=13h)
> RC2 arrived at N4 (t=13, total=34.0km); MPS1 standing by at N5 — awaiting section clearance; RC2 traversing fault edge to N5

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ⚡ 4/5 · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N5 v5 r0 idle · RC2@N4 v4 r12 →N5(2km) |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 14 (t=14h)
> RC2 arrived at N5 (t=14, total=36.0km); MPS1 standing by at N5 — awaiting section clearance; RC2 auto-started repair of DP1

| | |
|---|---|
| Loads     | 9/11 on · reward 9050 |
| Faults    | DP1@N4-N5 lv5 ⚡ 4/5 · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N5 v5 r0 idle · RC2@N5 v4 r12 REPAIR DP1 |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S3,S4,S5  ·  open: S2,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 15 (t=15h)
> RC2 repaired DP1 at t=15

| | |
|---|---|
| Loads     | 11/11 on · reward 11800 |
| Faults    | DP1@N4-N5 lv5 ✓ repaired · DP2@N6-N7 lv4 ✓ repaired · DP3@N2-N6 lv4 ✓ repaired |
| RC        | RC1@N5 v5 r0 idle · RC2@N5 v4 r11 idle |
| Scout     | Scout1@S8 v10 idle |
| MPS       | MPS1@N5 400kW e3000 idle |
| Switches  | closed: S1,S2,S3,S4,S5  ·  open: S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

**✓ All faults repaired at t=15h.**


---

## Case4
_3 hidden faults · 2 RC · 1 MPS · 1 Scout_

#### Initial (t=0h)

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ⚡ 0/5 · DP3@N10 lv5 ? hidden |
| RC        | RC1@N4 v3 r15 →N8(6km) · RC2@N8 v2 r13 →S4(2km) |
| Scout     | Scout1@N4 v10 →N5 |
| MPS       | MPS1@V3 450kW e5000 →N7 |
| Switches  | closed: S2,S5  ·  open: S1,S3,S4,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 1 (t=1h)
> RC2 arrived at S4 (t=1, total=2.0km); Scout Scout1 arrived at N5

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ⚡ 0/5 · DP3@N10 lv5 ? hidden |
| RC        | RC1@N4 v3 r15 →N8(3km) · RC2@S4 v2 r13 →N3(0km) |
| Scout     | Scout1@N5 v10 →S8 |
| MPS       | MPS1@V3 450kW e5000 →N7 |
| Switches  | closed: S2,S5  ·  open: S1,S3,S4,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 2 (t=2h)
> RC1 arrived at N8 (t=2, total=6.0km); RC2 arrived at N3 (t=2, total=2.0km); Scout Scout1 arrived at S8; MPS1 arrived at N7; MPS1 standing by at N7 — awaiting section clearance; MPS1 standing by at N7 — awaiting section clearance; RC1 traversing fault edge to N9

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ⚡ 0/5 · DP3@N10 lv5 ? hidden |
| RC        | RC1@N8 v3 r15 →N9(4km) · RC2@N3 v2 r13 →N10(2km) |
| Scout     | Scout1@S8 v10 →N9 |
| MPS       | MPS1@N7 450kW e5000 idle |
| Switches  | closed: S2,S5  ·  open: S1,S3,S4,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 3 (t=3h)
> RC2 arrived at N10 (t=3, total=4.0km); *** RC RC2 DISCOVERED DP3 at N10 (t=3h) ***; Scout Scout1 arrived at N9; MPS1 standing by at N7 — awaiting section clearance; RC2 auto-started repair of DP3

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ⚡ 0/5 · DP3@N10 lv5 ⚡ 0/5 |
| RC        | RC1@N8 v3 r15 →N9(1km) · RC2@N10 v2 r13 REPAIR DP3 |
| Scout     | Scout1@N9 v10 →V4 |
| MPS       | MPS1@N7 450kW e5000 idle |
| Switches  | closed: S2,S5  ·  open: S1,S3,S4,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 4 (t=4h)
> RC1 arrived at N9 (t=4, total=10.0km); Scout Scout1 arrived at V4; MPS1 standing by at N7 — awaiting section clearance; RC1 auto-started repair of DP2

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ⚡ 0/5 · DP3@N10 lv5 ⚡ 3/5 |
| RC        | RC1@N9 v3 r15 REPAIR DP2 · RC2@N10 v2 r10 REPAIR DP3 |
| Scout     | Scout1@V4 v10 →S7 |
| MPS       | MPS1@N7 450kW e5000 idle |
| Switches  | closed: S2,S5  ·  open: S1,S3,S4,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 5 (t=5h)
> RC2 repaired DP3 at t=5; Scout Scout1 arrived at S7; MPS1 moving to V1 (restores 5 loads)

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ⚡ 4/5 · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N9 v3 r11 REPAIR DP2 · RC2@N10 v2 r8 →N12(2km) |
| Scout     | Scout1@S7 v10 →N13 |
| MPS       | MPS1@N7 450kW e5000 →V1 |
| Switches  | closed: S2,S3,S5  ·  open: S1,S4,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 6 (t=6h)
> RC1 repaired DP2 at t=6; RC2 arrived at N12 (t=6, total=6.0km); Scout Scout1 arrived at N13; MPS1 arrived at V1; MPS1 standing by at V1 — awaiting section clearance; MPS1 standing by at V1 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N9 v3 r10 →N11(12km) · RC2@N12 v2 r8 →V2(2km) |
| Scout     | Scout1@N13 v10 →S5 |
| MPS       | MPS1@V1 450kW e5000 idle |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 7 (t=7h)
> RC2 arrived at V2 (t=7, total=8.0km); Scout Scout1 arrived at S5; MPS1 standing by at V1 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N9 v3 r10 →N11(9km) · RC2@V2 v2 r8 →V1(6km) |
| Scout     | Scout1@S5 v10 →V3 |
| MPS       | MPS1@V1 450kW e5000 idle |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 8 (t=8h)
> Scout Scout1 arrived at V3; MPS1 standing by at V1 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N9 v3 r10 →N11(6km) · RC2@V2 v2 r8 →V1(4km) |
| Scout     | Scout1@V3 v10 →N7 |
| MPS       | MPS1@V1 450kW e5000 idle |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 9 (t=9h)
> MPS1 standing by at V1 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N9 v3 r10 →N11(3km) · RC2@V2 v2 r8 →V1(2km) |
| Scout     | Scout1@V3 v10 →N7 |
| MPS       | MPS1@V1 450kW e5000 idle |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 10 (t=10h)
> RC2 arrived at V1 (t=10, total=14.0km); Scout Scout1 arrived at N7; MPS1 connected at V1 — section cleared

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ? hidden · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N9 v3 r10 →N11(0km) · RC2@V1 v2 r8 →S6(6km) |
| Scout     | Scout1@N7 v10 →N6 |
| MPS       | MPS1@V1 450kW e5000 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 11 (t=11h)
> RC1 arrived at N11 (t=11, total=22.0km); Scout Scout1 arrived at N6; *** Scout Scout1 DISCOVERED DP1 at N6 (t=11h) ***; RC2 redirected to fault DP1; RC1 moving to discovered fault DP1

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N11 v3 r10 →N2(14km) · RC2@V1 v2 r8 →N2(8km) |
| Scout     | Scout1@N6 v10 →N2 |
| MPS       | MPS1@V1 450kW e4550 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 12 (t=12h)
> Scout Scout1 arrived at N2

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N11 v3 r10 →N2(11km) · RC2@V1 v2 r8 →N2(6km) |
| Scout     | Scout1@N2 v10 →S2 |
| MPS       | MPS1@V1 450kW e4100 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 13 (t=13h)
> Scout Scout1 arrived at S2

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N11 v3 r10 →N2(8km) · RC2@V1 v2 r8 →N2(4km) |
| Scout     | Scout1@S2 v10 →S3 |
| MPS       | MPS1@V1 450kW e3650 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 14 (t=14h)
> Scout Scout1 arrived at S3

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N11 v3 r10 →N2(5km) · RC2@V1 v2 r8 →N2(2km) |
| Scout     | Scout1@S3 v10 →S1 |
| MPS       | MPS1@V1 450kW e3200 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 15 (t=15h)
> RC2 arrived at N2 (t=15, total=24.0km); Scout Scout1 arrived at S1; RC2 traversing fault edge to N6

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N11 v3 r10 →N2(2km) · RC2@N2 v2 r8 →N6(4km) |
| Scout     | Scout1@S1 v10 →S6 |
| MPS       | MPS1@V1 450kW e2750 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 16 (t=16h)
> RC1 arrived at N2 (t=16, total=36.0km); Scout Scout1 arrived at S6; RC1 traversing fault edge to N6

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N2 v3 r10 →N6(4km) · RC2@N2 v2 r8 →N6(2km) |
| Scout     | Scout1@S6 v10 idle |
| MPS       | MPS1@V1 450kW e2300 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 17 (t=17h)
> RC2 arrived at N6 (t=17, total=28.0km); RC2 auto-started repair of DP1

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N2 v3 r10 →N6(1km) · RC2@N6 v2 r8 REPAIR DP1 |
| Scout     | Scout1@S6 v10 idle |
| MPS       | MPS1@V1 450kW e1850 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 18 (t=18h)
> RC1 arrived at N6 (t=18, total=40.0km); RC1 auto-started repair of DP1

| | |
|---|---|
| Loads     | 9/11 on · reward 11560 |
| Faults    | DP1@N2-N6 lv10 ⚡ 3/10 · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N6 v3 r10 REPAIR DP1 · RC2@N6 v2 r5 REPAIR DP1 |
| Scout     | Scout1@S6 v10 idle |
| MPS       | MPS1@V1 450kW e1400 CONNECTED |
| Switches  | closed: S2,S3,S4,S5  ·  open: S1,S6,S7,S8 |
| Sections  | Area1=PARTIAL[N6,N7] · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

#### Step 19 (t=19h)
> RC2 repaired DP1 at t=19; MPS1 disconnected at V1 (grid restored)

| | |
|---|---|
| Loads     | 11/11 on · reward 11800 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N8-N9 lv5 ✓ repaired · DP3@N10 lv5 ✓ repaired |
| RC        | RC1@N6 v3 r6 REPAIR DP1 · RC2@N6 v2 r2 idle |
| Scout     | Scout1@S6 v10 idle |
| MPS       | MPS1@V1 450kW e950 idle |
| Switches  | closed: S1,S2,S3,S4,S5  ·  open: S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

**✓ All faults repaired at t=19h.**


---

## Case5
_3 hidden faults · 2 RC · 1 MPS · 1 Scout_

#### Initial (t=0h)

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N13 lv6 ? hidden · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N8 v3 r15 →N2(10km) · RC2@N2 v2 r18 →N6(4km) |
| Scout     | Scout1@N8 v10 →S4 |
| MPS       | MPS1@V3 450kW e5000 →N12 |
| Switches  | closed: S3,S4  ·  open: S1,S2,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 1 (t=1h)
> Scout Scout1 arrived at S4; MPS1 arrived at N12; MPS1 standing by at N12 — awaiting section clearance; MPS1 standing by at N12 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N13 lv6 ? hidden · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N8 v3 r15 →N2(7km) · RC2@N2 v2 r18 →N6(2km) |
| Scout     | Scout1@S4 v10 →N3 |
| MPS       | MPS1@N12 450kW e5000 idle |
| Switches  | closed: S3,S4  ·  open: S1,S2,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 2 (t=2h)
> RC2 arrived at N6 (t=2, total=4.0km); Scout Scout1 arrived at N3; MPS1 standing by at N12 — awaiting section clearance; RC2 auto-started repair of DP1

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ⚡ 0/10 · DP2@N13 lv6 ? hidden · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N8 v3 r15 →N2(4km) · RC2@N6 v2 r18 REPAIR DP1 |
| Scout     | Scout1@N3 v10 →N10 |
| MPS       | MPS1@N12 450kW e5000 idle |
| Switches  | closed: S3,S4  ·  open: S1,S2,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 3 (t=3h)
> Scout Scout1 arrived at N10; MPS1 standing by at N12 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ⚡ 3/10 · DP2@N13 lv6 ? hidden · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N8 v3 r15 →N2(1km) · RC2@N6 v2 r15 REPAIR DP1 |
| Scout     | Scout1@N10 v10 →N12 |
| MPS       | MPS1@N12 450kW e5000 idle |
| Switches  | closed: S3,S4  ·  open: S1,S2,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 4 (t=4h)
> RC1 arrived at N2 (t=4, total=10.0km); Scout Scout1 arrived at N12; MPS1 standing by at N12 — awaiting section clearance; RC1 traversing fault edge to N6

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ⚡ 6/10 · DP2@N13 lv6 ? hidden · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N2 v3 r15 →N6(4km) · RC2@N6 v2 r12 REPAIR DP1 |
| Scout     | Scout1@N12 v10 →V2 |
| MPS       | MPS1@N12 450kW e5000 idle |
| Switches  | closed: S3,S4  ·  open: S1,S2,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 5 (t=5h)
> Scout Scout1 arrived at V2; MPS1 standing by at N12 — awaiting section clearance

| | |
|---|---|
| Loads     | 0/11 on · reward 0 |
| Faults    | DP1@N2-N6 lv10 ⚡ 9/10 · DP2@N13 lv6 ? hidden · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N2 v3 r15 →N6(1km) · RC2@N6 v2 r9 REPAIR DP1 |
| Scout     | Scout1@V2 v10 →V3 |
| MPS       | MPS1@N12 450kW e5000 idle |
| Switches  | closed: S3,S4  ·  open: S1,S2,S5,S6,S7,S8 |
| Sections  | Area1=DARK[N2,N6,N7] · Area2=DARK[N4,N5] · Area3=DARK[N8,N9] · Area4=DARK[N10,N11,N12,N3] · Area5=DARK[N13,V1,V2,V3] |

#### Step 6 (t=6h)
> RC1 arrived at N6 (t=6, total=14.0km); RC2 repaired DP1 at t=6; Scout Scout1 arrived at V3; MPS1 moving to N13 (restores 1 loads)

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ? hidden · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N6 v3 r15 →V1(4km) · RC2@N6 v2 r8 →S2(4km) |
| Scout     | Scout1@V3 v10 →N13 |
| MPS       | MPS1@N12 450kW e5000 →N13 |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 7 (t=7h)
> Scout Scout1 arrived at N13; *** Scout Scout1 DISCOVERED DP2 at N13 (t=7h) ***; RC1 redirected to fault DP2

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N6 v3 r15 →N13(20km) · RC2@N6 v2 r8 →S2(2km) |
| Scout     | Scout1@N13 v10 →S5 |
| MPS       | MPS1@N12 450kW e5000 →N13 |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 8 (t=8h)
> Scout Scout1 arrived at S5; MPS1 arrived at N13; MPS1 standing by at N13 — awaiting section clearance; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N6 v3 r15 →N13(17km) · RC2@N6 v2 r8 →S2(0km) |
| Scout     | Scout1@S5 v10 →S7 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 9 (t=9h)
> RC2 arrived at S2 (t=9, total=8.0km); Scout Scout1 arrived at S7; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N6 v3 r15 →N13(14km) · RC2@S2 v2 r8 →S6(2km) |
| Scout     | Scout1@S7 v10 →V4 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 10 (t=10h)
> Scout Scout1 arrived at V4; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N6 v3 r15 →N13(11km) · RC2@S2 v2 r8 →S6(0km) |
| Scout     | Scout1@V4 v10 →S8 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 11 (t=11h)
> RC2 arrived at S6 (t=11, total=10.0km); MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N6 v3 r15 →N13(8km) · RC2@S6 v2 r8 →V1(6km) |
| Scout     | Scout1@V4 v10 →S8 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 12 (t=12h)
> Scout Scout1 arrived at S8; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ? hidden |
| RC        | RC1@N6 v3 r15 →N13(5km) · RC2@S6 v2 r8 →V1(4km) |
| Scout     | Scout1@S8 v10 →N5 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 13 (t=13h)
> Scout Scout1 arrived at N5; *** Scout Scout1 DISCOVERED DP3 at N5 (t=13h) ***; MPS1 standing by at N13 — awaiting section clearance; RC1 redirected to fault DP3; RC2 redirected to fault DP2

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ⚡ 0/5 |
| RC        | RC1@N6 v3 r15 →N4(8km) · RC2@S6 v2 r8 →N13(18km) |
| Scout     | Scout1@N5 v10 →N4 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 14 (t=14h)
> Scout Scout1 arrived at N4; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ⚡ 0/5 |
| RC        | RC1@N6 v3 r15 →N4(5km) · RC2@S6 v2 r8 →N13(16km) |
| Scout     | Scout1@N4 v10 →V1 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 15 (t=15h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ⚡ 0/5 |
| RC        | RC1@N6 v3 r15 →N4(2km) · RC2@S6 v2 r8 →N13(14km) |
| Scout     | Scout1@N4 v10 →V1 |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 16 (t=16h)
> RC1 arrived at N4 (t=16, total=43.0km); Scout Scout1 arrived at V1; MPS1 standing by at N13 — awaiting section clearance; RC2 redirected to fault DP3; RC1 traversing fault edge to N5

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ⚡ 0/5 |
| RC        | RC1@N4 v3 r15 →N5(2km) · RC2@S6 v2 r8 →N4(6km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 17 (t=17h)
> RC1 arrived at N5 (t=17, total=45.0km); MPS1 standing by at N13 — awaiting section clearance; RC2 redirected to fault DP2; RC1 auto-started repair of DP3

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ⚡ 0/5 |
| RC        | RC1@N5 v3 r15 REPAIR DP3 · RC2@S6 v2 r8 →N13(18km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 18 (t=18h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 7/11 on · reward 7690 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ⚡ 4/5 |
| RC        | RC1@N5 v3 r11 REPAIR DP3 · RC2@S6 v2 r8 →N13(16km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S3,S4  ·  open: S2,S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=DARK[N4,N5] · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 19 (t=19h)
> RC1 repaired DP3 at t=19; MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(14km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 20 (t=20h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(12km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 21 (t=21h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(10km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 22 (t=22h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(8km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 23 (t=23h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(6km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 24 (t=24h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(4km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 25 (t=25h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(2km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 26 (t=26h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@S6 v2 r8 →N13(0km) |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 27 (t=27h)
> RC2 arrived at N13 (t=27, total=40.1km); MPS1 standing by at N13 — awaiting section clearance; RC2 auto-started repair of DP2

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 0/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@N13 v2 r8 REPAIR DP2 |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 28 (t=28h)
> MPS1 standing by at N13 — awaiting section clearance

| | |
|---|---|
| Loads     | 9/11 on · reward 10440 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ⚡ 3/6 · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@N13 v2 r5 REPAIR DP2 |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4  ·  open: S5,S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=DARK[N13,V1,V2,V3] |

#### Step 29 (t=29h)
> RC2 repaired DP2 at t=29

| | |
|---|---|
| Loads     | 11/11 on · reward 11800 |
| Faults    | DP1@N2-N6 lv10 ✓ repaired · DP2@N13 lv6 ✓ repaired · DP3@N4-N5 lv5 ✓ repaired |
| RC        | RC1@N5 v3 r10 idle · RC2@N13 v2 r2 idle |
| Scout     | Scout1@V1 v10 idle |
| MPS       | MPS1@N13 450kW e5000 idle |
| Switches  | closed: S1,S2,S3,S4,S5  ·  open: S6,S7,S8 |
| Sections  | Area1=LIVE · Area2=LIVE · Area3=LIVE · Area4=LIVE · Area5=LIVE |

**✓ All faults repaired at t=29h.**

