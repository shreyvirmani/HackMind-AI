from threading import Lock


class Telemetry:

    def __init__(self):
        self.lock = Lock()

        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "retries": 0,
            "fallbacks": 0,
            "total_response_time": 0.0,
        }

    def increment(self, metric: str, value: int = 1):
        with self.lock:
            if metric in self.metrics:
                self.metrics[metric] += value

    def add_response_time(self, seconds: float):
        with self.lock:
            self.metrics["total_response_time"] += seconds

    def get_metrics(self):

        with self.lock:

            metrics = self.metrics.copy()

            total = metrics["successful_requests"]

            if total > 0:
                metrics["average_response_time"] = (
                    metrics["total_response_time"] / total
                )
            else:
                metrics["average_response_time"] = 0

            return metrics

    def reset(self):

        with self.lock:

            for key in self.metrics:

                self.metrics[key] = 0


telemetry = Telemetry()