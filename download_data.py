import csv
import random
from multiprocessing.pool import ThreadPool

import requests
import tqdm

from neutils import storage

sess = requests.Session()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
sess.headers.update({"User-Agent": user_agent})


def download_domain(domain):
    errors_cache_key = f"errors-{domain}"
    if errors_cache_key in storage:
        return f"{domain}: errored already"
    urls = [
        f"https://{domain}/",
        f"http://{domain}/",
        f"https://www.{domain}/",
        f"http://www.{domain}/",
    ]
    errors = []
    for url in urls:
        if url in storage:
            return f"{domain}: {url} @ already in cache"
        try:
            r = sess.get(url, timeout=8)
            storage[url] = r
            return f"{domain} - {url} - {r.status_code}"
        except Exception as e:
            errors.append(f"{url} ! {e}")
    storage[errors_cache_key] = errors
    return f"{domain} = {errors}"


def read_domains():
    with open("tranco.csv") as f:
        domains = [r[1] for r in csv.reader(f)]
    return domains


def main():
    domains = read_domains()
    with ThreadPool(50) as pool:
        for result in tqdm.tqdm(
            pool.imap_unordered(download_domain, domains), total=len(domains)
        ):
            # pass
            if result:
                print(result)


if __name__ == "__main__":
    main()
