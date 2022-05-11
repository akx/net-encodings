import diskcache

storage = diskcache.Cache(
    directory="cache", eviction_policy="none", size_limit=10 * 1024 * 1024 * 1024
)
