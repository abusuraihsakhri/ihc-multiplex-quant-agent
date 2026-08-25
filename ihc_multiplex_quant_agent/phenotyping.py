"""
Immune Hot/Cold Phenotype Scoring with Spatial Context for IHC Multiplex Quant Agent.
Classify tumor microenvironments based on immune cell density and proximity to tumor.
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ImmunePhenotypeResult:
    """Result of immune phenotype classification."""
    phenotype: str  # "Immune Hot", "Immune Cold", "Immune Excluded", "Immune Intermediate"
    cd8_density: float
    cd8_to_tumor_distance_um: float
    foxp3_cd8_ratio: float
    pdl1_cps: float
    confidence: float


class ImmunePhenotypeScorer:
    """Classify tumor microenvironment immune phenotype."""

    def compute_immune_score(self, cell_counts: dict, distances: dict) -> ImmunePhenotypeResult:
        cd8_count = cell_counts.get("cd8", 0)
        foxp3_count = cell_counts.get("foxp3", 0)
        area_mm2 = cell_counts.get("tumor_area_mm2", 1.0)
        cd8_density = cd8_count / area_mm2 if area_mm2 > 0 else 0
        mean_dist = distances.get("cd8_to_tumor_mean_um", 100)
        foxp3_cd8_ratio = foxp3_count / cd8_count if cd8_count > 0 else 0

        if cd8_density > 50 and mean_dist < 50:
            phenotype = "Immune Hot"
            confidence = 0.9
        elif cd8_density < 10:
            phenotype = "Immune Cold"
            confidence = 0.85
        elif cd8_density > 10 and mean_dist > 100:
            phenotype = "Immune Excluded"
            confidence = 0.8
        else:
            phenotype = "Immune Intermediate"
            confidence = 0.7

        return ImmunePhenotypeResult(
            phenotype=phenotype,
            cd8_density=round(cd8_density, 2),
            cd8_to_tumor_distance_um=round(mean_dist, 1),
            foxp3_cd8_ratio=round(foxp3_cd8_ratio, 3),
            pdl1_cps=0.0,
            confidence=confidence,
        )

    def get_therapeutic_implications(self, phenotype: str) -> dict:
        implications = {
            "Immune Hot": {
                "checkpoint_inhibitor_response": "High likelihood",
                "recommendation": "Consider anti-PD-1/PD-L1 therapy",
                "biomarker_validation": "Confirm PD-L1 CPS and TMB",
            },
            "Immune Cold": {
                "checkpoint_inhibitor_response": "Low likelihood",
                "recommendation": "Consider combination therapy or vaccine approaches",
                "biomarker_validation": "Evaluate for immune priming strategies",
            },
            "Immune Excluded": {
                "checkpoint_inhibitor_response": "Variable",
                "recommendation": "Consider anti-VEGF or stromal-modifying agents",
                "biomarker_validation": "Assess CXCL9/CXCL10 expression",
            },
            "Immune Intermediate": {
                "checkpoint_inhibitor_response": "Uncertain",
                "recommendation": "Additional biomarker testing recommended",
                "biomarker_validation": "Repeat with expanded panel",
            },
        }
        return implications.get(phenotype, {"recommendation": "Unknown phenotype"})
