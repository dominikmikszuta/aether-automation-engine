# AETHER-QM - Multi-Level Security (MLS)

## Bell-LaPadula Model
- No read up: a subject at level L cannot read objects above L.
- No write down: a subject at level L cannot write to objects below L.

## Levels
| Level | Rank |
|-------|------|
| UNCLASSIFIED | 0 |
| CONFIDENTIAL | 1 |
| SECRET | 2 |
| TOP_SECRET | 3 |

## Compartments
Documents are labelled with (level, {compartments}). Access requires
both level dominance AND all compartments present in the subject's clearance.

## Covert Channel Mitigation
pad_to_block(data, 4096) pads all outputs to a constant 4 KiB block
to prevent timing/size side-channels.
