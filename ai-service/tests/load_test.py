import concurrent.futures
import requests
import time

URL = "http://localhost:5000/describe"
PAYLOAD = {"text": "High-risk audit for financial department."}
CONCURRENT_REQUESTS = 10  # Reduced for local testing simulation
TOTAL_REQUESTS = 50

def send_request():
    start = time.time()
    try:
        response = requests.post(URL, json=PAYLOAD, timeout=10)
        return response.status_code, time.time() - start
    except Exception as e:
        return 500, 0

def run_load_test():
    print(f"Starting load test: {TOTAL_REQUESTS} requests, {CONCURRENT_REQUESTS} concurrent.")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(send_request) for _ in range(TOTAL_REQUESTS)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    duration = time.time() - start_time
    successes = [r for r in results if r[0] == 200 or r[0] == 202] # Including async
    avg_latency = sum(r[1] for r in successes) / len(successes) if successes else 0
    
    print("\n--- Load Test Results ---")
    print(f"Total Duration: {duration:.2f}s")
    print(f"Success Rate: {len(successes)}/{TOTAL_REQUESTS}")
    print(f"Avg Latency (Successful): {avg_latency:.2f}s")
    print(f"Throughput: {len(successes)/duration:.2f} req/s")

if __name__ == "__main__":
    # Note: Service must be running for this to work live
    # simulate_results() 
    print("Load test script ready. Run with 'python ai-service/tests/load_test.py' while server is up.")
