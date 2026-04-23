# Field Generator Flowcharts

## 1. Overall Workflow

```mermaid
flowchart LR
    A[📝 Edit YAML config] --> B[🔨 colcon build]
    B --> C[⚙️ generate_world]
    C --> D[generated.world]
    C --> E[gt_map.png]
    C --> F[gt_map.csv]
    C --> G[robot_spawner.launch.py]
    C --> H[heightmap.png]
    D --> I[🚀 Launch Gazebo]
    I --> J[🤖 Spawn Robot]
    J --> K[🎮 Teleop Drive]
```

## 2. World Generation Pipeline

```mermaid
flowchart TD
    A[Load YAML Config] --> B[Initialize RNG with seed]
    B --> C[Generate Row Segments]
    C --> D[Place Plants Along Rows]
    D --> E[Remove Plants for Gaps]
    E --> F[Scatter Weeds]
    F --> G[Place Litter Objects]
    G --> H[Generate Terrain Heightmap]
    H --> I[Write SDF World File]
    I --> J[Save Ground Truth Map]
    I --> K[Save Ground Truth CSV]
    I --> L[Save Robot Spawner]

    style A fill:#4a90d9,color:#fff
    style B fill:#4a90d9,color:#fff
    style C fill:#5cb85c,color:#fff
    style D fill:#5cb85c,color:#fff
    style E fill:#f0ad4e,color:#fff
    style F fill:#f0ad4e,color:#fff
    style G fill:#f0ad4e,color:#fff
    style H fill:#d9534f,color:#fff
    style I fill:#d9534f,color:#fff
```

## 3. Row Segment Generation

```mermaid
flowchart TD
    START([Start: current_length = 0]) --> CHECK{current_length<br/>< row_length?}
    CHECK -- No --> DONE([Row Complete])
    CHECK -- Yes --> PICK[Pick random segment<br/>from row_segments list]
    PICK --> TYPE{Segment type?}

    TYPE -- straight --> ST[Generate straight segment<br/>length = random in min..max]
    TYPE -- curved --> CV[Generate curved segment<br/>radius = random in min..max<br/>arc = random in min..max]
    TYPE -- sincurved --> SC[Generate S-curve segment<br/>offset = random in min..max<br/>length = random in min..max]
    TYPE -- island --> IS[Generate island segment<br/>radius = random in min..max]

    ST --> BUDGET{Within curve<br/>budget?}
    CV --> BUDGET
    SC --> BUDGET
    IS --> BUDGET

    BUDGET -- Yes --> ADD[Add segment<br/>Update current_length]
    BUDGET -- No --> PICK
    ADD --> CHECK

    style START fill:#4a90d9,color:#fff
    style DONE fill:#5cb85c,color:#fff
    style CHECK fill:#f0ad4e,color:#000
    style TYPE fill:#f0ad4e,color:#000
    style BUDGET fill:#f0ad4e,color:#000
    style ST fill:#e8f5e9,color:#000
    style CV fill:#fff3e0,color:#000
    style SC fill:#fce4ec,color:#000
    style IS fill:#e3f2fd,color:#000
```

## 4. Parameter Priority Map

```mermaid
flowchart TD
    subgraph MUST["🔴 MUST SET (will break without these)"]
        R1[row_length]
        R2[rows_count]
        R3[row_segments]
        R4[seed]
    end

    subgraph REC["🟡 RECOMMENDED (set for most use cases)"]
        O1[row_width]
        O2[ground_elevation_max]
        O3[plant_height_min]
        O4[plant_height_max]
        O5[hole_prob]
        O6[hole_size_max]
    end

    subgraph OPT["🟢 OPTIONAL (defaults work fine)"]
        P1[plant_spacing_min/max]
        P2[plant_radius / noise]
        P3[plant_mass]
        P4[ground_resolution]
        P5[ground_headland]
        P6[ground_ditch_depth]
        P7[weeds / weed_types]
        P8[litters / litter_types]
        P9[ghost_objects]
        P10[location_markers]
        P11[crop_types]
        P12[All segment min/max params]
    end

    style MUST fill:#ffe0e0,stroke:#d9534f,stroke-width:2px
    style REC fill:#fff3d0,stroke:#f0ad4e,stroke-width:2px
    style OPT fill:#e0ffe0,stroke:#5cb85c,stroke-width:2px
```

## 5. Available 3D Models

```mermaid
flowchart LR
    subgraph CROPS["🌽 Crops"]
        C1[maize_01 ✅]
        C2[maize_02 ✅]
    end

    subgraph WEEDS["🌿 Weeds"]
        W1[nettle ✅]
        W2[unknown_weed ✅]
        W3[dandelion ❌<br/>models not shipped]
    end

    subgraph LITTER["🗑️ Litter"]
        L1[ale ✅]
        L2[beer ✅]
        L3[coke_can ✅]
        L4[retro_pepsi_can ✅]
    end

    subgraph OBSTACLES["🪨 Obstacles (code only)"]
        O1[stone_01 ✅]
        O2[stone_02 ✅]
        O3[box ✅]
    end

    subgraph MARKERS["📍 Markers"]
        M1[location_marker_a ✅]
        M2[location_marker_b ✅]
    end

    style CROPS fill:#e8f5e9,stroke:#4caf50
    style WEEDS fill:#fff3e0,stroke:#ff9800
    style LITTER fill:#fce4ec,stroke:#e91e63
    style OBSTACLES fill:#e3f2fd,stroke:#2196f3
    style MARKERS fill:#f3e5f5,stroke:#9c27b0
    style W3 fill:#ffcdd2,stroke:#d32f2f
```

## 6. Config Decision Tree

```mermaid
flowchart TD
    Q1{What are you testing?} 
    
    Q1 -- Navigation --> NAV[Use curved/sincurved segments<br/>Add weeds + litter<br/>Enable location_markers]
    Q1 -- Perception --> PER[Use straight segments<br/>Dense planting, tall corn<br/>No gaps]
    Q1 -- Quick debug --> DBG[Short rows, few rows<br/>Flat terrain, no obstacles<br/>Fixed seed]
    Q1 -- Weed detection --> WEED[Straight segments<br/>Many weeds: 15-30<br/>weed_types: nettle, unknown_weed]
    Q1 -- Object detection --> OBJ[Straight segments<br/>Many litters: 10-20<br/>ghost_objects: true]

    NAV --> CFG1["row_segments: [straight, curved, sincurved]<br/>weeds: 10, litters: 5<br/>location_markers: true<br/>ground_elevation_max: 0.3"]
    PER --> CFG2["row_segments: [straight]<br/>plant_height_min: 0.5<br/>plant_height_max: 0.9<br/>plant_spacing_min: 0.10<br/>hole_prob: 0.0"]
    DBG --> CFG3["row_length: 4.0<br/>rows_count: 3<br/>row_segments: [straight]<br/>ground_elevation_max: 0.0<br/>seed: 1"]
    WEED --> CFG4["weeds: 20<br/>weed_types: [nettle, unknown_weed]<br/>hole_prob: 0.02"]
    OBJ --> CFG5["litters: 15<br/>litter_types: [ale, beer, coke_can]<br/>ghost_objects: true"]

    style Q1 fill:#4a90d9,color:#fff
    style NAV fill:#5cb85c,color:#fff
    style PER fill:#f0ad4e,color:#000
    style DBG fill:#5bc0de,color:#fff
    style WEED fill:#d9534f,color:#fff
    style OBJ fill:#9c27b0,color:#fff
```

## 7. Dynamic Fields — Workarounds

```mermaid
flowchart TD
    Q{Need dynamic behavior?}
    
    Q -- Different field each run --> S1[Set seed: -1]
    Q -- Growth stages --> S2[Create configs:<br/>stage1.yaml height 0.1-0.2<br/>stage2.yaml height 0.3-0.5<br/>stage3.yaml height 0.6-0.9]
    Q -- Runtime spawn/remove --> S3[Use Ignition services:<br/>ign service /world/.../create<br/>ign service /world/.../remove]
    Q -- Weather variation --> S4[Edit generated.world<br/>Modify scene lighting]
    Q -- Multiple trials --> S5[Use fixed seeds:<br/>seed: 1, seed: 2, seed: 3...]

    style Q fill:#4a90d9,color:#fff
    style S1 fill:#e8f5e9
    style S2 fill:#fff3e0
    style S3 fill:#fce4ec
    style S4 fill:#e3f2fd
    style S5 fill:#f3e5f5
```
