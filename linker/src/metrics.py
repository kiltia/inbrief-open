import numpy as np
from hdbscan import validity_index
from sklearn.metrics import calinski_harabasz_score, silhouette_score
from utils import noises_to_single_cluster, normalize


def silhouette(X, labels, metric="cityblock"):
    labels_copy = noises_to_single_cluster(labels)
    try:
        return silhouette_score(X, labels_copy, metric=metric)
    except ValueError:
        return None


def calinski_harabasz(X, labels, **kwargs):
    labels_copy = noises_to_single_cluster(labels)
    try:
        return calinski_harabasz_score(X, labels_copy)
    except ValueError:
        return None


def weighted_scorer(X, labels, metric):
    labels_copy = noises_to_single_cluster(labels)
    try:
        return calinski_harabasz_score(X, labels_copy), silhouette_score(
            X, labels_copy, metric=metric
        )
    except ValueError:
        return None


def business_scorer(X, labels, metric=None):
    validity = (validity_index(X, labels, metric=metric) + 1) / 2
    if np.isnan(validity) or max(labels) == -1:
        return None
    n_noise = len(labels[labels == -1])
    noise_penalty = 1 - n_noise / len(labels)
    normalized_num_clusters = (max(labels) + 1) / len(labels)
    clusters_num_samples = [
        len(labels[labels == i]) for i in range(max(labels) + 1)
    ]
    z_scores = normalize(
        (clusters_num_samples - np.mean(clusters_num_samples))
        / np.std(clusters_num_samples)
    )
    clusters_size_penalty = 2 / (
        1 / np.median(z_scores) + 1 / np.mean(z_scores)
    )
    return 4 / (
        1 / validity
        + 1 / noise_penalty
        + 1 / normalized_num_clusters
        + 1 / clusters_size_penalty
    )


def apply_weighted_scorer(embeddings, method, scorer, params_range, metric):
    ranked_entries = method.fine_tune(
        embeddings, scorer, metric, params_range, sort=False
    )
    calinski_harabasz = normalize(np.array([i[0][0] for i in ranked_entries]))
    silhouette = normalize(np.array([i[0][1] for i in ranked_entries]))
    scores = list(zip(calinski_harabasz, silhouette, strict=False))
    for i in range(len(scores)):
        ranked_entries[i] = (
            2 * scores[i][0] * scores[i][1] / (scores[i][0] + scores[i][1]),
            ranked_entries[i][1],
        )
    return sorted(ranked_entries, key=lambda x: x[0], reverse=True)
