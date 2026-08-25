"""
PD-L1 Combined Positive Score (CPS) Computation for IHC Multiplex Quant Agent.
Compute PD-L1 CPS per KEYNOTE-048/158 guidelines for immunotherapy eligibility.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PDL1CPSResult:
    """PD-L1 Combined Positive Score result."""
    cps: float
    valid: bool
    pembrolizumab_eligible: bool
    tumor_cells_counted: int
    pdl1_positive_count: int
    immune_cells_counted: int
    reason: str = ""


def compute_pdl1_cps(tumor_cells: int, pdl1_positive_cells: int, immune_cells: int = 0) -> dict:
    """Compute PD-L1 Combined Positive Score per KEYNOTE guidelines.
    CPS = (PD-L1+ cells / total viable tumor cells) * 100
    CPS >= 10 indicates pembrolizumab eligibility for HNSCC, gastric, cervical cancers."""
    if tumor_cells < 100:
        return {
            "cps": 0.0,
            "valid": False,
            "pembrolizumab_eligible": False,
            "tumor_cells_counted": tumor_cells,
            "pdl1_positive_count": pdl1_positive_cells,
            "immune_cells_counted": immune_cells,
            "reason": "Insufficient tumor cells (<100); specimen inadequate for CPS",
        }

    cps = (pdl1_positive_cells / tumor_cells) * 100

    # CPS thresholds per tumor type
    eligibility = {
        "hnscc": cps >= 1,
        "gastric": cps >= 1,
        "cervical": cps >= 1,
        "nsclc": cps >= 50,
        "tnbc": cps >= 10,
    }

    return {
        "cps": round(cps, 1),
        "valid": True,
        "pembrolizumab_eligible": cps >= 10,
        "tumor_cells_counted": tumor_cells,
        "pdl1_positive_count": pdl1_positive_cells,
        "immune_cells_counted": immune_cells,
        "eligibility_by_tumor_type": eligibility,
        "reason": "Valid CPS computed",
    }


class PDL1Scorer:
    """PD-L1 scoring agent with CPS and TPS computation."""

    def compute_tps(self, tumor_cells: int, pdl1_positive_tumor_cells: int) -> dict:
        """Compute Tumor Proportion Score (TPS).
        TPS = (PD-L1+ tumor cells / total tumor cells) * 100"""
        if tumor_cells < 100:
            return {"tps": 0.0, "valid": False, "reason": "Insufficient tumor cells"}

        tps = (pdl1_positive_tumor_cells / tumor_cells) * 100
        return {
            "tps": round(tps, 1),
            "valid": True,
            "expression_level": "High" if tps >= 50 else "Low" if tps >= 1 else "Negative",
            "nsclc_eligible": tps >= 50,
        }

    def compute_ic_score(self, immune_cells: int, total_viable_cells: int) -> dict:
        """Compute Immune Cell (IC) score for atezolizumab eligibility."""
        if total_viable_cells < 100:
            return {"ic_score": 0.0, "valid": False}

        ic_pct = (immune_cells / total_viable_cells) * 100
        return {
            "ic_score": round(ic_pct, 1),
            "valid": True,
            "ic_level": "IC2/3" if ic_pct >= 5 else "IC1" if ic_pct >= 1 else "IC0",
        }
