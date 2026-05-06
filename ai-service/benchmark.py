import time
import requests
import statistics
import concurrent.futures

ENDPOINTS = [
    {"url": "http://localhost:5000/categorise", "payload": {"text": "test"}},
    {"url": "http://localhost:5000/describe", "payload": {"text": "test"}},
    {"url": "http://localhost:5000/recommend", "payload": {"text": "test"}},
    {"url": "http://localhost:5000/query", "payload": {"question": "test"}},
    {"url": "http://localhost:5000/generate-report", "payload": {"text": "test"}},
]

def run_benchmark(endpoint, runs=50):
    latencies = []
    
    def fetch():
        start = time.time()
        try:
            requests.post(endpoint["url"], json=endpoint["payload"], timeout=10)
        except:
            pass
        return (time.time() - start) * 1000

    # Warmup
    fetch()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch) for _ in range(runs)]
        for f in concurrent.futures.as_completed(futures):
            latencies.append(f.result())

    latencies.sort()
    
    return {
        "p50": latencies[int(runs * 0.50)],
        "p95": latencies[int(runs * 0.95)],
        "p99": latencies[int(runs * 0.99)],
        "avg": statistics.mean(latencies)
    }

if __name__ == "__main__":
    print("Starting benchmark run...")
    for ep in ENDPOINTS:
        print(f"Benchmarking {ep['url']}...")
        stats = run_benchmark(ep)
        print(f"Results for {ep['url']}:")
        print(f"  P50: {stats['p50']:.2f} ms")
        print(f"  P95: {stats['p95']:.2f} ms")
        print(f"  P99: {stats['p99']:.2f} ms")
        print(f"  AVG: {stats['avg']:.2f} ms")
        print("-" * 40)
