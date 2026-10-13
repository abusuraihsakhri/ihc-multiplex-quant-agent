"""Numerical PD-L1 CPS/TPS summaries from preclassified cell counts.

No treatment recommendation or assay-specific clinical eligibility is inferred.
"""
from dataclasses import dataclass


@dataclass
class PDL1CPSResult:
    cps: float
    valid: bool
    pembrolizumab_eligible: bool | None
    tumor_cells_counted: int
    pdl1_positive_count: int
    immune_cells_counted: int
    reason: str = ""


def _count(value):
    return type(value) is int and value >= 0


def compute_pdl1_cps(tumor_cells: int, pdl1_positive_cells: int, immune_cells: int = 0) -> dict:
    """CPS = min(100, 100 * (PD-L1+ tumor + PD-L1+ immune) / viable tumor).

    Here pdl1_positive_cells is the number of positive TUMOR cells, and
    immune_cells is the number of PD-L1-positive lymphocytes/macrophages.
    The 100-cell minimum is a conservative demonstration guard and is not
    a substitute for assay- and indication-specific adequacy assessment.
    """
    result = {
        "cps": 0.0, "valid": False, "pembrolizumab_eligible": None,
        "tumor_cells_counted": tumor_cells,
        "pdl1_positive_count": pdl1_positive_cells,
        "immune_cells_counted": immune_cells,
        "reason": "",
    }
    if not all(_count(n) for n in (tumor_cells, pdl1_positive_cells, immune_cells)):
        result["reason"] = "Cell counts must be non-negative integers."
        return result
    if pdl1_positive_cells > tumor_cells:
        result["reason"] = "PD-L1-positive tumor cells exceed viable tumor cells."
        return result
    if tumor_cells < 100:
        result["reason"] = "Fewer than 100 viable tumor cells in demonstration input."
        return result
    cps = min(100.0, (pdl1_positive_cells + immune_cells) / tumor_cells * 100)
    result.update({
        "cps": round(cps, 1),
        "valid": True,
        "meets_cps_1_cutoff": cps >= 1,
        "meets_cps_10_cutoff": cps >= 10,
        "reason": "Descriptive CPS only; treatment eligibility requires indication- and assay-specific review.",
    })
    return result


class PDL1Scorer:
    """Descriptive cellular PD-L1 metrics; not a clinical decision engine."""

    def compute_tps(self, tumor_cells: int, pdl1_positive_tumor_cells: int) -> dict:
        """Percentage of viable tumor cells positive for PD-L1."""
        if not (_count(tumor_cells) and _count(pdl1_positive_tumor_cells)
                and tumor_cells >= 100 and pdl1_positive_tumor_cells <= tumor_cells):
            return {"tps": 0.0, "valid": False, "reason": "Invalid or insufficient tumor cell counts."}
        tps = pdl1_positive_tumor_cells / tumor_cells * 100
        return {
            "tps": round(tps, 1),
            "valid": True,
            "expression_level": "High" if tps >= 50 else "Low" if tps >= 1 else "Negative",
            "nsclc_eligible": None,
        }

    def compute_ic_score(self, immune_cells: int, total_viable_cells: int) -> dict:
        """Simple immune-cell frequency, not a validated assay-specific IC score."""
        if not (_count(immune_cells) and _count(total_viable_cells)
                and total_viable_cells >= 100 and immune_cells <= total_viable_cells):
            return {"ic_score": 0.0, "valid": False}
        ic_pct = immune_cells / total_viable_cells * 100
        return {
            "ic_score": round(ic_pct, 1),
            "valid": True,
            "ic_level": "IC2/3" if ic_pct >= 5 else "IC1" if ic_pct >= 1 else "IC0",
        }
