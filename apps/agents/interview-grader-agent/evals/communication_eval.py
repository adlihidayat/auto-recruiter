"""
What: Verification and Precision/Recall/Hallucination metrics evaluator for Communication extraction.
Why: Used by LangSmith experiment runner to compare LLM extracted communication signals against human answer keys.
Boundaries: Pure evaluation functions; no LLM network calls.
"""
from typing import Dict, List, Any, Tuple
from ..state import CommunicationExtraction
from ..nodes.communication import COMMUNICATION_RUBRIC

# Extract valid signal IDs from rubric
VALID_SIGNAL_IDS = set()
for trait_data in COMMUNICATION_RUBRIC.values():
    for pos_sig in trait_data.get("positive_signals", []):
        VALID_SIGNAL_IDS.add(pos_sig["id"])
    for neg_sig in trait_data.get("negative_signals", []):
        VALID_SIGNAL_IDS.add(neg_sig["id"])


def verify_and_filter_extraction(
    transcript: List[Dict[str, str]], 
    extraction: CommunicationExtraction
) -> Tuple[Dict[str, Dict[str, List[Dict[str, str]]]], int, int]:
    """
    Verifies that extracted quotes are exact substrings of the specified turn_id's content,
    turn_id exists, and signal_id is valid according to the rubric.
    
    Returns:
        - verified_matches: Dict mapping trait -> {"positive": [...], "negative": [...]}
        - total_extracted: Int total extracted matches by LLM
        - total_dropped: Int count of dropped/hallucinated matches
    """
    history_map = {t["turn_id"]: t["content"] for t in transcript if "turn_id" in t and "content" in t}
    
    verified_matches = {}
    total_extracted = 0
    total_dropped = 0

    for trait_name in ["active_listening", "structure", "assertiveness", "clarity"]:
        verified_matches[trait_name] = {"positive": [], "negative": []}
        trait_extract = getattr(extraction, trait_name, None)
        
        if not trait_extract:
            continue
            
        for pos in trait_extract.positive:
            total_extracted += 1
            turn_id = pos.turn_id or ""
            quote = pos.quote or ""
            sig_id = pos.signal_id or ""
            
            is_valid = (
                sig_id in VALID_SIGNAL_IDS and
                turn_id in history_map and
                quote in history_map[turn_id]
            )
            
            if is_valid:
                verified_matches[trait_name]["positive"].append({
                    "signal_id": sig_id,
                    "turn_id": turn_id,
                    "quote": quote
                })
            else:
                total_dropped += 1

        for neg in trait_extract.negative:
            total_extracted += 1
            turn_id = neg.turn_id or ""
            quote = neg.quote or ""
            sig_id = neg.signal_id or ""
            
            is_valid = (
                sig_id in VALID_SIGNAL_IDS and
                turn_id in history_map and
                quote in history_map[turn_id]
            )
            
            if is_valid:
                verified_matches[trait_name]["negative"].append({
                    "signal_id": sig_id,
                    "turn_id": turn_id,
                    "quote": quote
                })
            else:
                total_dropped += 1

    return verified_matches, total_extracted, total_dropped


def evaluate_communication(
    transcript: List[Dict[str, str]],
    extraction: CommunicationExtraction,
    answer_key: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes Precision, Recall, and Hallucination Rate against human answer key.
    
    A match is considered a True Positive if both (signal_id, turn_id) match the answer_key.
    """
    verified_matches, total_extracted, total_dropped = verify_and_filter_extraction(transcript, extraction)
    
    hallucination_rate = (total_dropped / total_extracted) if total_extracted > 0 else 0.0
    
    total_tp = 0
    total_fp = 0
    total_fn = 0

    trait_metrics = {}

    for trait_name in ["active_listening", "structure", "assertiveness", "clarity"]:
        key_pos = answer_key.get(trait_name, {}).get("positive", [])
        key_neg = answer_key.get(trait_name, {}).get("negative", [])

        target_set = set((item["signal_id"], item["turn_id"]) for item in key_pos + key_neg)
        
        found_pos = verified_matches[trait_name]["positive"]
        found_neg = verified_matches[trait_name]["negative"]
        found_set = set((item["signal_id"], item["turn_id"]) for item in found_pos + found_neg)

        tp = len(found_set.intersection(target_set))
        fp = len(found_set - target_set)
        fn = len(target_set - found_set)

        precision = (tp / (tp + fp)) if (tp + fp) > 0 else (1.0 if len(target_set) == 0 else 0.0)
        recall = (tp / (tp + fn)) if (tp + fn) > 0 else (1.0 if len(target_set) == 0 else 0.0)

        trait_metrics[trait_name] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall
        }

        total_tp += tp
        total_fp += fp
        total_fn += fn

    overall_precision = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 1.0
    overall_recall = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 1.0

    return {
        "overall_precision": overall_precision,
        "overall_recall": overall_recall,
        "hallucination_rate": hallucination_rate,
        "total_extracted": total_extracted,
        "total_dropped": total_dropped,
        "total_tp": total_tp,
        "total_fp": total_fp,
        "total_fn": total_fn,
        "trait_metrics": trait_metrics
    }
