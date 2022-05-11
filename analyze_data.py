from collections import defaultdict, Counter
from typing import Optional

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


def main():
    sites_by_encoding = defaultdict(list)
    encoding_counts = Counter()

    for key in tqdm.tqdm(list(storage)):
        response: requests.Response = storage[key]
        if response.status_code >= 400:
            continue
        if not response.content:
            continue
        url = response.url
        enc = get_encoding_from_headers_without_fallback(response.headers)
        if not enc:
            fallback_enc = get_encoding_from_headers(response.headers)
            if fallback_enc:
                enc = f"{fallback_enc} (via fallback)"
        if not enc or ", " in enc:
            print("???", url, response.headers)
        sites_by_encoding[enc].append(url)
        encoding_counts[enc] += 1

    print(encoding_counts)
    print(sum(encoding_counts.values()))


if __name__ == "__main__":
    main()
