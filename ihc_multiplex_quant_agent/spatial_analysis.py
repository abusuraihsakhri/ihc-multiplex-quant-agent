"""
Spatial Distance Matrix for Tumor-Infiltrating Lymphocytes for IHC Multiplex Quant Agent.
Compute pairwise distances between tumor and immune cell populations.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import math


@dataclass
class SpatialDistanceResult:
    """Spatial distance analysis result."""
    marker: str
    mean_dist_um: float
    median_dist_um: float
    max_dist_um: float
    min_dist_um: float
    cell_count: int
    nearest_neighbor_mean_um: float


def compute_spatial_distances(tumor_centroids: List[dict], immune_centroids: List[dict], marker: str) -> dict:
    """Compute Euclidean distance matrix between tumor and immune cells.
    Returns mean, median, max distances per immune cell type."""
    if not tumor_centroids or not immune_centroids:
        return {
            "marker": marker,
            "mean_dist_um": -1,
            "median_dist_um": -1,
            "max_dist_um": -1,
            "min_dist_um": -1,
            "cell_count": 0,
            "nearest_neighbor_mean_um": -1,
        }

    # Compute minimum distance from each immune cell to nearest tumor cell
    min_distances = []
    for ic in immune_centroids:
        ic_x, ic_y = ic["x"], ic["y"]
        dists_to_tumor = []
        for tc in tumor_centroids:
            tc_x, tc_y = tc["x"], tc["y"]
            dist = math.sqrt((ic_x - tc_x) ** 2 + (ic_y - tc_y) ** 2)
            dists_to_tumor.append(dist)
        min_distances.append(min(dists_to_tumor))

    min_distances.sort()
    n = len(min_distances)

    return {
        "marker": marker,
        "mean_dist_um": round(sum(min_distances) / n, 2),
        "median_dist_um": round(min_distances[n // 2], 2),
        "max_dist_um": round(max(min_distances), 2),
        "min_dist_um": round(min(min_distances), 2),
        "cell_count": len(immune_centroids),
        "nearest_neighbor_mean_um": round(sum(min_distances) / n, 2),
    }


class SpatialAnalyzer:
    """Advanced spatial analysis for tumor-immune interactions."""

    def compute_hotspot_density(self, cells: List[dict], grid_size: int = 100, threshold: int = 5) -> dict:
        """Identify spatial hotspots of immune cell density."""
        if not cells:
            return {"hotspots": [], "total_cells": 0}

        grid = {}
        for c in cells:
            gx = int(c["x"] // grid_size)
            gy = int(c["y"] // grid_size)
            key = (gx, gy)
            grid[key] = grid.get(key, 0) + 1

        hotspots = [
            {"grid_x": k[0], "grid_y": k[1], "cell_count": v,
             "density_per_100um2": round(v / (grid_size * grid_size) * 1e6, 2)}
            for k, v in grid.items() if v >= threshold
        ]

        return {
            "hotspots": sorted(hotspots, key=lambda h: h["cell_count"], reverse=True),
            "total_hotspots": len(hotspots),
            "total_cells": len(cells),
        }

    def compute_tumor_border_infiltration(self, tumor_centroids: List[dict],
                                           immune_centroids: List[dict],
                                           border_width_um: float = 50.0) -> dict:
        """Compute immune cell density within tumor border zone."""
        if not tumor_centroids or not immune_centroids:
            return {"border_density": 0, "interior_density": 0, "ratio": 0}

        border_cells = 0
        interior_cells = 0
        for ic in immune_centroids:
            min_dist = min(
                math.sqrt((ic["x"] - tc["x"]) ** 2 + (ic["y"] - tc["y"]) ** 2)
                for tc in tumor_centroids
            )
            if min_dist <= border_width_um:
                border_cells += 1
            elif min_dist <= border_width_um * 3:
                interior_cells += 1

        total = len(immune_centroids)
        return {
            "border_cells": border_cells,
            "interior_cells": interior_cells,
            "exterior_cells": total - border_cells - interior_cells,
            "border_density_pct": round(border_cells / total * 100, 1) if total else 0,
            "infiltration_pattern": "Inflamed" if border_cells > interior_cells else "Excluded",
        }
