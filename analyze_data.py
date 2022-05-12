import multiprocessing
import pickle
from collections import defaultdict, Counter
from typing import Optional, Tuple, Any

import requests
import tqdm
from requests.utils import get_encoding_from_headers, _parse_content_type_header

from neutils import storage


def get_encoding_from_headers_without_fallback(headers) -> Optional[str]:
    content_type = headers.get("content-type")

    if not content_type:
        return None

    content_type, params = _parse_content_type_header(content_type)

    if "charset" in params:
        return params["charset"].strip("'\"").lower()
    return None


def normalize_encoding_name(encoding_name: str) -> str:
    encoding_name = encoding_name.lower()
    if encoding_name == "utf8":
        return "utf-8"
    return encoding_name


def read_encoding(key: str) -> Optional[Tuple[bool, str, Any]]:
    response: requests.Response = storage[key]
    if response.status_code >= 400:
        return None
    if not response.content:
        return None
    url = response.url
    enc = get_encoding_from_headers_without_fallback(response.headers)
    if not enc:
        fallback_enc = get_encoding_from_headers(response.headers)
        if fallback_enc:
            enc = f"{normalize_encoding_name(fallback_enc)} (via fallback)"
    else:
        enc = normalize_encoding_name(enc)
    if not enc or ", " in enc:
        return (False, url, response.headers)
    return (True, url, enc)


def main():
    sites_by_encoding = defaultdict(list)
    anomalies = []

    with multiprocessing.Pool() as pool:
        keys = [k for k in storage if not k.startswith("error")]
        res_iter = pool.imap_unordered(read_encoding, keys, chunksize=8)
        for res in tqdm.tqdm(res_iter, total=len(storage)):
            if res is None:
                continue
            ok, url, encoding = res
            if ok:
                sites_by_encoding[encoding].append(url)
            else:
                anomalies.append(res[1:])

    with open("analyzed.pickle", "wb") as f:
        pickle.dump((sites_by_encoding, anomalies), f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()
