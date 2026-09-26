# Reliability Upgrade Implementation Plan

## ✅ COMPLETED (Committed)
1. Created `src/utils/prediction_status.py` - Status enums and helper functions
2. Started `src/utils/image_quality.py` - Image validation framework

## 🔄 IN PROGRESS - Priority Order

### Phase 1: Complete Image Quality Module
- File: `src/utils/image_quality.py`
- Add: ImageQualityValidator class with validation methods

### Phase 2: Refactor Inference Pipeline
- File: `src/inference/pipeline.py`
- Changes:
  - Add image quality validation before classification
  - Use prediction status instead of forcing disease names
  - Return structured status in results

### Phase 3: Make Severity Status-Aware
- File: `src/severity/estimator.py`
- Changes:
  - Accept prediction_status parameter
  - Return UNRELIABLE when diagnosis uncertain
  - Distinguish "visible affected area" from "disease severity"

### Phase 4: Redesign Risk Engine
- File: `src/risk_engine/engine.py`
- Changes:
  - Add INSUFFICIENT_DATA state
  - Check for required inputs before computing
  - Never fabricate risk scores

### Phase 5: Improve Recommendations
- File: `src/recommendations/recommendation_engine.py`
- Changes:
  - Accept prediction_status parameter
  - Provide general guidance when uncertain
  - Disease-specific only when confident

### Phase 6: Update Alert Engine
- File: `src/alerts/engine.py`
- Changes:
  - Check data sufficiency before activating
  - Suppress alerts when evidence insufficient

### Phase 7: Refactor API
- File: `api/main.py`
- Changes:
  - Use new prediction status system
  - Pass status through pipeline
  - Return structured responses

### Phase 8: Transform Streamlit UI
- File: `app/streamlit_app.py`
- Major redesign with status-aware sections

### Phase 9: Update Tests
- Add tests for all new status paths
- Update existing tests for new schema

### Phase 10: Update README
- Document new uncertainty handling
- Update limitations section

## Key Design Principles

1. **Conservative**: Only diagnose when confident
2. **Transparent**: Always show uncertainty explicitly
3. **Modular**: Each component checks its own requirements
4. **Safe**: Never fabricate data when information missing

## Status Thresholds (Engineering Estimates)

- HIGH_CONFIDENCE: ≥ 0.70
- LOW_CONFIDENCE: ≥ 0.40
- UNCERTAIN: < 0.40

These are NOT scientifically validated and must be documented as such.
