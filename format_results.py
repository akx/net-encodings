import pickle
from collections import Counter


def filter_anomalies(anomalies):
    for url, headers in anomalies:
        ctype = headers.get("Content-Type", "")
        if ctype == "application/octet-stream":
            continue
        if ctype.startswith("image/"):
            continue
        yield (url, headers)


def main():
    with open("analyzed.pickle", "rb") as f:
        (sites_by_encoding, anomalies) = pickle.load(f)
    encoding_counts = Counter()
    for encoding, sites in sites_by_encoding.items():
        encoding_counts[encoding] += len(sites)
    filtered_anomalies = list(filter_anomalies(anomalies))
    total_pages = sum(encoding_counts.values())
    print(
        f"Out of {total_pages} pages, there are {len(anomalies)} pages ({len(anomalies) / total_pages:.2%}) where an encoding wasn't (correctly) declared."
    )
    print(
        f"With binary responses filtered out, there are {len(filtered_anomalies)} such pages ({len(filtered_anomalies) / total_pages:.2%}):\n"
    )
    print("| URL | Content-Type | Remarks |")
    print("| --- | --- | --- |")
    for url, headers in sorted(filtered_anomalies):
        ctype = headers.get("Content-Type", "(no content-type)")
        print(f"| {url} | {ctype} |")
    print()
    print()
    print(
        "For the rest, the following encodings were declared (`via fallback` meaning gleaned with requests' [internal fallback for text](https://github.com/psf/requests/blob/cb233a101d6333cf1895e3f46bde11874fcaba07/requests/utils.py#L550-L551):\n"
    )
    print("| Encoding | Count | % |")
    print("| --- | --: | --: |")
    for encoding, count in encoding_counts.most_common():
        print(f"| {encoding} | {count} | {count / total_pages:.2%} |")
    print()
    print(
        "The top 3 encodings account for {:.2%} of the pages analyzed.".format(
            sum(v for k, v in encoding_counts.most_common(3)) / total_pages
        )
    )


"""
* Out of 5368 pages, there are 11 results (0.2%) where the headers do not specify a valid encoding.
  * 7 of those results do not represent text content (either an image, application/octet-stream, or an error page).
  * unicode.org (ironically enough) serves a redirection page to home.unicode.org without any content type. However, that redirection page is pure ASCII and as such decodable as utf-8.
  * sberbank.ru/sbrf.ru has a malformed content-type header with `utf-8, text/html` as the charset. This will decode fine as utf-8, anyway.
  * mob.com serves no content-type header, but the content itself is UTF-8.
* Out of these 5368 pages, 4427 (82.4%) declare themselves to be UTF-8.
* The next most popular encoding is ISO-8859-1 with 498 pages (487 instances via , 11 explicitly declared), so that's about 16.4%.
* The remaining 1.2% are other encodings.
"""


if __name__ == "__main__":
    main()
