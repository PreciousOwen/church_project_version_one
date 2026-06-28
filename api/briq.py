import hashlib
import hmac


def verify_briq_signature(*, raw_body: bytes, secret: str, signature_header: str) -> bool:
    """Verify Briq webhook HMAC signature.

    Expected header format: sha256=<hex>
    """
    prefix = "sha256="
    if not signature_header or not signature_header.startswith(prefix):
        return False
    expected_hex = signature_header[len(prefix) :]
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, expected_hex)
