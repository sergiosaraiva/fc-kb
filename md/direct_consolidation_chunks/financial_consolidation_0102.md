# Chunk 102: Complex Multi-Path Ownership Structure

## Context

This section covers Complex Multi-Path Ownership Structure.

## Content

# Complex Multi-Path Ownership Structure

```
         ┌─────┐
         │  P  │─────────────┐
         └─┬─┬─┘             │40%
          / │ \              │
      80%/  │  \60%          │
        /   │   \            ↓
       ↓    ↓    ↓        ┌────┐
    ┌────┐ ┌────┐ ┌────┐  │    │
    │ C1 │ │ C2 │ │ C3 │──┴────┘
    └──┬─┘ └──┬─┘ └──┬─┘  10%
       │      │20%    │20%
       │30%   ↓       ↓
       └────→┌────┐←──┘
             │ C4 │
             └────┘
```


---
*Chunk 102 | Complex Multi-Path Ownership Structure*