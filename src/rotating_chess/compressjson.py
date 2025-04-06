import zlib, json, base64


def json_compress(j):
    """
    takes a json-encodable Any and compresses it into a base64 string.

    >>> json_compress({"hello": "world!"})
    'eJyrVspIzcnJV7JSUCrPL8pJUVSqBQA/dAY4'

    >>> json_compress({"not", "good!"})
    Traceback (most recent call last):
    ...
    TypeError: Object of type set is not JSON serializable
    """
    return base64.b64encode(zlib.compress(json.dumps(j).encode("utf-8"))).decode(
        "utf-8"
    )


def json_decompress(s: str):
    """
    decompresses a string compressed by json_compress.

    >>> json_decompress(json_compress({"hello": "world!"}))
    {'hello': 'world!'}
    """
    return json.loads(zlib.decompress(base64.b64decode(s)))
