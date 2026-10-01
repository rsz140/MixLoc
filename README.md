# MixLoc: A Large-Scale Multilingual Benchmark for Mixed Human-AI Authorship Detection and Character-Level Localization

**Authors:**
- Shizhe Ru — 1975831774@qq.com
- Jiaye Li — 1718936744@qq.com

## Dataset Download

- **Baidu Pan**: [https://pan.baidu.com/s/1EkfV7gcdFdtuQtcszZfa4g](https://pan.baidu.com/s/1EkfVgcdFdtuQtcszZfa4g)

## Overview

MixLoc is a benchmark dataset for detecting and localizing AI-generated content in mixed human-AI documents. It covers:

- **20 languages** across diverse language families
- **601,846 documents** (HUMAN: 300,963 / PARTIAL_AI: 190,085 / FULL_AI: 110,798)
- **180,971 controlled-generation documents** with construction-derived character-level provenance ground truth
- **5 controlled mixed-authorship operations**: sentence replacement, sentence insertion, multi-sentence insertion, style-constrained rewrite, continuation (+ full generation as control)
- **2→6 generator held-out design**: train/val uses 2 generators (DeepSeek-V4-Flash, MiniMax-M2.5), test uses 6 unseen generators
- **C1-C11 coverage quota control** (1%-99%) to prevent distribution shortcuts
- **Leakage-aware splitting**: zero cross-split source-group overlap (SHA-256 verified)

## Repository Structure

```
mixloc-github/
├── manuscript/          # Paper manuscript (Word format)
├── figures/             # Publication figures (600 DPI PNG + vector PDF)
├── results/             # Benchmark evaluation results (JSON)
├── scripts/             # Figure generation and analysis scripts
├── LICENSE              # CC BY-NC-SA 4.0
└── README.md            # This file
```

## Dataset

The dataset is available via [Baidu Pan](https://pan.baidu.com/s/1EkfVgcdFdtuQtcszZfa4g). A HuggingFace release is planned.

### Data Schema

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Full document text (Unicode) |
| `label` | enum | HUMAN / PARTIAL_AI / FULL_AI |
| `gold_machine_spans` | list[[int,int]] | AI character intervals (half-open, Unicode codepoint offsets) |
| `gold_human_spans` | list[[int,int]] | Human character intervals |
| `sentence_labels` | list[int] | Sentence-level 0/1 labels |
| `language` | string | ISO 639-1 language code |
| `generator` | string | Generator identifier (controlled-generation rows) |
| `operation` | string | Mixed-authorship operation type |
| `coverage` | float | AI character ratio (derived from spans) |
| `source_group_hash` | string | Source-group leakage control unit |
| `split` | enum | train / val / test |

## Benchmark Results

### Overall Detection Performance (Full Test Set, n=202,762)

| Method | AUROC | BACC | Macro-F1 (3-class) | Venue |
|--------|-------|------|---------------------|-------|
| XLM-R-CLS | 0.885 | 0.828 | 0.585 | ACL 2020 |
| XLM-R-span | 0.851 | 0.826 | 0.580 | ACL 2020 |
| GLTR | 0.821 | 0.799 | — | ACL 2019-D |
| DetectLLM-LRR | 0.809 | 0.795 | — | EMNLP 2023-F |
| Fast-DetectGPT | 0.527 | 0.619 | — | ICLR 2024 |
| Binoculars (adapted) | 0.396 | 0.574 | — | ICML 2024 |

### Key Findings

1. **Low-coverage collapse**: Supervised detectors' F1 drops to 0.27 (span) / 0.11 (CLS) when AI content is <5% of the document
2. **FULL_AI detection failure**: F1 ≈ 0 across most languages — existing detectors cannot distinguish mixed from fully AI-generated text
3. **Language-dependent performance**: Japanese easiest (CLS Macro-F1 = 0.64); English hardest (0.30)
4. **Cross-generator generalization gap**: PARTIAL_AI F1 drops from 0.78-0.80 (seen) to 0.55-0.64 (unseen generators)
5. **Source confound**: Source-only features achieve ~0.98 Macro-F1, motivating strict text-only input protocol

## Evaluation Protocol

| Dimension | Setting | Primary Metric |
|-----------|---------|----------------|
| Document 3-class | HUMAN/PARTIAL/FULL | Macro-F1 |
| Binary detection | HUMAN vs AI-involved | AUROC, BACC |
| Character-level localization | Unicode character space | Char-F1, Exact-span F1, IoU@0.5, Boundary MAE |
| Coverage-stratified | 5 buckets (0-100%) | Per-bucket F1 |
| Generator generalization | 2 seen → 6 unseen | Per-generator F1 |
| Cross-dataset transfer | MixLoc → MixSet/LLMTrace | F1, AUROC |
| Shortcut diagnostics | Majority/Length/Source | Macro-F1 |

## Usage

### Loading the Dataset

```python
import json

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def derive_label3(row):
    spans = row.get("gold_machine_spans") or []
    if not spans:
        return row.get("document_label"), 0.0
    n = len(row["text"])
    cov = sum(min(e, n) - s for s, e in spans) / n
    return ("full_ai" if cov >= 1.0 else "partial_ai"), cov
```

### Important Usage Guidelines

1. **Input restriction**: Detector input must be `text` only. All provenance metadata (generator, source, operation, coverage) must be excluded from model features.
2. **Split discipline**: Official splits must not be modified. Any re-splitting must group by `source_group_hash`.
3. **Test set**: Run only once for final results. All development (hyperparameters, checkpoints, thresholds) must use train/val only.
4. **Label derivation**: Three-class labels must be derived from spans (coverage = 0 / (0,1) / = 1), not from the coarse `document_label` field.

## Citation

```bibtex
@dataset{mixloc_2026,
  title   = {MixLoc: A Large-Scale Multilingual Benchmark for Mixed
             Human-AI Authorship Detection and Character-Level Localization},
  author  = {Ru, Shizhe and Li, Jiaye},
  year    = {2026},
  note    = {601,846 documents, 20 languages, 180,971 controlled-generation
             documents with character-level provenance ground truth},
  license = {CC BY-NC-SA 4.0}
}
```

## Contact

- **Shizhe Ru** — 1975831774@qq.com
- **Jiaye Li** — 1718936744@qq.com

## License

This project is licensed under CC BY-NC-SA 4.0. The Zhihu supplementary subset is for research use only and must not be redistributed.

## Acknowledgments

We acknowledge the following upstream datasets: SemEval-2024 Task 8, LLMTrace, Wiki-Lingua. Please cite these works when using the external resource archive.
