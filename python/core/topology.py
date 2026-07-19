from __future__ import annotations

__all__ = ["TopologicalDataAnalysis"]

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn import manifold

from python.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


class TopologicalDataAnalysis:
    """
    Topological Data Analysis for decision space visualization.

    Uses dimensionality reduction (MDS/Isomap) and connectivity
    analysis to reveal the structure of the decision space:
    - Cluster detection: which options form natural groups
    - Decision boundaries: how factors separate options
    - Connectivity: stability of rankings under perturbation
    """

    @staticmethod
    def analyze(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
    ) -> Dict[str, Any]:
        if not mc_results or len(mc_results) < 2:
            return {"error": "Need at least 2 options for TDA"}

        names = list(mc_results.keys())
        n_opts = len(names)
        fnames = [f.name for f in factors if f.name in mc_results[names[0]].factor_stats]
        if not fnames:
            return {"error": "No factor data available"}

        # Build feature matrix: options x normalized factor means
        X = np.zeros((n_opts, len(fnames)))
        bounds = {}
        for j, fn in enumerate(fnames):
            vals = [mc_results[name].factor_stats[fn]["mean"] for name in names]
            bounds[fn] = {"min": min(vals), "max": max(vals)}
            for i, name in enumerate(names):
                raw = mc_results[name].factor_stats[fn]["mean"]
                lo, hi = bounds[fn]["min"], bounds[fn]["max"]
                X[i, j] = (raw - lo) / (hi - lo + 1e-9)

        # Distance matrix (Euclidean in normalized factor space)
        dist_matrix = np.zeros((n_opts, n_opts))
        for i in range(n_opts):
            for j in range(n_opts):
                dist_matrix[i, j] = float(np.linalg.norm(X[i] - X[j]))

        # MDS embedding to 2D
        embedding_2d = None
        stress = None
        if n_opts >= 2:
            mds = manifold.MDS(n_components=2, dissimilarity="precomputed",
                               random_state=42, normalized_stress=False)
            embedding_2d = mds.fit_transform(dist_matrix)
            stress = float(mds.stress_)

        # Isomap embedding (uses direct features, not distances)
        isomap_2d = None
        isomap_err = None
        if n_opts >= 3:
            try:
                iso = manifold.Isomap(n_components=2, n_neighbors=max(2, n_opts - 1))
                isomap_2d = iso.fit_transform(X)
                isomap_err = float(iso.reconstruction_error())
            except (ValueError, np.linalg.LinAlgError):
                pass

        # Connectivity analysis: at what distance threshold does the
        # graph become connected? (Vietoris-Rips-inspired)
        sorted_dists = np.sort(dist_matrix[dist_matrix > 0].flatten())
        if len(sorted_dists) == 0:
            return {"error": "All options are identical — no topological variation"}
        connectivity = []
        for threshold in np.linspace(0, max(sorted_dists), 20):
            adj = (dist_matrix > 0) & (dist_matrix <= threshold)
            # Count connected components via BFS
            visited = set()
            components = 0
            for start in range(n_opts):
                if start in visited:
                    continue
                components += 1
                stack = [start]
                while stack:
                    v = stack.pop()
                    if v in visited:
                        continue
                    visited.add(v)
                    for u in range(n_opts):
                        if adj[v, u] and u not in visited:
                            stack.append(u)
            connectivity.append({
                "threshold": float(threshold),
                "components": components,
            })

        # Cluster detection: find natural gaps in distances
        clusters = []
        if n_opts >= 3:
            linkage = TopologicalDataAnalysis._single_linkage(dist_matrix)
            # Find the largest gap in linkage distances
            gaps = [(linkage[i + 1] - linkage[i], i) for i in range(len(linkage) - 1)]
            if gaps:
                max_gap_idx = max(gaps, key=lambda x: x[0])[1]
                if gaps[max(gaps, key=lambda x: x[0])[1]][0] > 0.1:
                    # Split at max gap
                    threshold = (linkage[max_gap_idx] + linkage[max_gap_idx + 1]) / 2
                    adj = (dist_matrix > 0) & (dist_matrix <= threshold)
                    visited = set()
                    for start in range(n_opts):
                        if start in visited:
                            continue
                        cluster = [start]
                        stack = [start]
                        while stack:
                            v = stack.pop()
                            if v in visited:
                                continue
                            visited.add(v)
                            for u in range(n_opts):
                                if adj[v, u] and u not in visited:
                                    stack.append(u)
                                    cluster.append(u)
                        clusters.append([names[i] for i in cluster])

        return {
            "num_options": n_opts,
            "num_factors": len(fnames),
            "distance_matrix": dist_matrix.tolist(),
            "embedding_2d": embedding_2d.tolist() if embedding_2d is not None else None,
            "mds_stress": stress,
            "isomap_embedding": isomap_2d.tolist() if isomap_2d is not None else None,
            "isomap_error": isomap_err,
            "connectivity": connectivity,
            "clusters": clusters,
            "average_distance": float(np.mean(sorted_dists)),
            "min_distance": float(sorted_dists[0]) if len(sorted_dists) > 0 else 0,
            "max_distance": float(sorted_dists[-1]) if len(sorted_dists) > 0 else 0,
        }

    @staticmethod
    def _single_linkage(dist_matrix: np.ndarray) -> List[float]:
        """Compute single-linkage dendrogram heights."""
        dim = dist_matrix.shape[0]
        # Start with each point as its own cluster
        clusters = [{i} for i in range(dim)]
        heights = []
        # Distance between two clusters
        def cluster_dist(c1, c2):
            return min(dist_matrix[i, j] for i in c1 for j in c2)

        while len(clusters) > 1:
            # Find closest pair
            min_dist = float("inf")
            merge_pair = (0, 1)
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    d = cluster_dist(clusters[i], clusters[j])
                    if d < min_dist:
                        min_dist = d
                        merge_pair = (i, j)
            heights.append(min_dist)
            # Merge
            i, j = merge_pair
            clusters[i] |= clusters[j]
            clusters.pop(j)

        return sorted(heights)
