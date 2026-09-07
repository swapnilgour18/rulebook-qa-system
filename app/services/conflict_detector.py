import os
import json
from typing import List, Dict, Any

def chunk_matches_rule(chunk: Dict[str, Any], rule_def: Dict[str, str]) -> bool:
    """
    Helper function to deterministically check if a retrieved chunk matches 
    a rule definition from conflicts.json based on metadata or content.
    """
    if chunk.get("source") != rule_def["document"]:
        return False
        
    target_sec = rule_def.get("section", "")
    meta = chunk.get("metadata", {})
    
    # Check if the section number is in the Markdown headers (e.g. "2.1 Minimum Attendance")
    for k, v in meta.items():
        if str(k).startswith("Header") and str(v).startswith(target_sec):
            return True
            
    # Fallback for fee_deadlines.csv which lacks Markdown headers but references Even Semester 2027
    if rule_def["document"] == "fee_deadlines.csv":
        content = chunk.get("content", "")
        if "Even Semester 2027" in content or "15 March 2027" in content:
            return True
            
    return False

def detect_conflicts(retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Examines retrieved chunks to determine if any genuine known contradictions are present.
    Treats conflicts.json as configuration.
    
    Args:
        retrieved_chunks: A list of chunk dictionaries from the retrieval service.
        
    Returns:
        A dictionary indicating if a conflict was found and detailing the conflicts.
    """
    # Load conflicts configuration deterministically
    conflicts_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "data", "rulebook", "conflicts.json"
    )
    
    with open(conflicts_path, "r", encoding="utf-8") as f:
        known_conflicts = json.load(f)
        
    detected_conflicts = []
    
    for conflict in known_conflicts:
        a_matched = False
        b_matched = False
        a_score = None
        b_score = None
        
        # Check if BOTH sides of the contradiction are present in the retrieved context
        for chunk in retrieved_chunks:
            if chunk_matches_rule(chunk, conflict["section_a"]):
                a_matched = True
                a_score = chunk.get("similarity_score")
            if chunk_matches_rule(chunk, conflict["section_b"]):
                b_matched = True
                b_score = chunk.get("similarity_score")
                
        if a_matched and b_matched:
            # Add similarity_score to the returned objects
            sec_a = dict(conflict["section_a"])
            sec_a["similarity_score"] = a_score
            sec_b = dict(conflict["section_b"])
            sec_b["similarity_score"] = b_score
            
            detected_conflicts.append({
                "conflict_id": conflict["conflict_id"],
                "topic": conflict["topic"],
                "description": conflict["description"],
                "section_a": sec_a,
                "section_b": sec_b
            })
            
    return {
        "has_conflict": len(detected_conflicts) > 0,
        "conflicts": detected_conflicts
    }
