import pytest
from src.utils.config import Config
from src.knowledge.disease_kb import get_knowledge_base, DiseaseKnowledgeBase

def test_knowledge_base_supported_classes():
    kb = get_knowledge_base()
    supported = kb.get_supported_diseases()
    for target_cls in Config.TARGET_CLASSES:
        assert target_cls in supported

def test_knowledge_base_retrieval_keys():
    kb = get_knowledge_base()
    for target_cls in Config.TARGET_CLASSES:
        info = kb.get_disease_info(target_cls)
        assert info["disease_name"] == target_cls
        assert info["crop"] == "Tomato"
        assert "symptoms" in info and isinstance(info["symptoms"], list)
        assert len(info["symptoms"]) > 0
        assert "general_causes" in info
        assert "favorable_conditions" in info
        assert "preventive_measures" in info
        assert "general_management_practices" in info
        assert "disclaimer" in info and len(info["disclaimer"]) > 0

def test_knowledge_base_unmapped_class_fallback():
    kb = get_knowledge_base()
    info = kb.get_disease_info("Unknown Crop Disease X")
    assert info["disease_name"] == "Unknown Crop Disease X"
    assert info["crop"] == "Tomato"
    assert "disclaimer" in info
