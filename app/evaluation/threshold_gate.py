def gate(metrics: dict, thresholds: dict) -> tuple[bool, list[str]]:
    failures = []
    for key, minimum in thresholds.items():
        if metrics.get(key, 0.0) < minimum:
            failures.append(f"{key}={metrics.get(key, 0.0)} < {minimum}")
    return (len(failures) == 0, failures)