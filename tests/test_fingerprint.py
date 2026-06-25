from traceframe.fingerprint import sha256_file


def test_sha256_file_streams_digest(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("traceframe\n", encoding="utf-8")

    assert sha256_file(path).startswith("sha256:")
    assert len(sha256_file(path)) == len("sha256:") + 64

