import json
import logging
import re
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_tz_phone(phone: str) -> str:
    """Normalize TZ phone input to 255XXXXXXXXX format."""
    digits = re.sub(r"\D+", "", phone or "")
    if digits.startswith("255") and len(digits) == 12:
        return digits
    if digits.startswith("0") and len(digits) == 10:
        return "255" + digits[1:]
    if len(digits) == 9:
        return "255" + digits
    return ""


def _briq_post_json(*, url: str, payload: dict, api_key: str, timeout: int = 15) -> tuple[int, dict | None, str | None]:
    data = json.dumps(payload).encode("utf-8")
    user_agent = getattr(settings, "BRIQ_OTP_USER_AGENT", "curl/8.0.1")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "User-Agent": user_agent,
            "Accept": "*/*",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                parsed = json.loads(raw.decode("utf-8")) if raw else None
            except Exception:
                parsed = None
            return resp.status, parsed, None
    except urllib.error.HTTPError as e:
        raw = e.read()
        detail = raw.decode("utf-8", errors="ignore") if raw else str(e)
        parsed = None
        try:
            parsed = json.loads(detail) if detail else None
        except Exception:
            parsed = None
        return int(getattr(e, "code", 0) or 0), parsed, detail
    except Exception as e:
        return 0, None, str(e)


def _format_briq_error(parsed: dict | None, err: str | None) -> str | None:
    if isinstance(parsed, dict):
        code = parsed.get("error_code") or parsed.get("code")
        message = (
            parsed.get("message")
            or parsed.get("error_message")
            or parsed.get("error")
            or parsed.get("detail")
        )
        if message and code and str(code) not in str(message):
            return f"{message} (code {code})"
        if message:
            return str(message)
        if code:
            return f"Error code {code}."
    return err


def _mask_key(value: str) -> str:
    if not value:
        return "<empty>"
    if len(value) <= 6:
        return "*" * len(value)
    return f"{'*' * (len(value) - 4)}{value[-4:]}"


def request_signup_otp(*, phone_number: str) -> tuple[bool, str | None]:
    api_key = (getattr(settings, "BRIQ_OTP_API_KEY", "") or "").strip()
    app_key = (getattr(settings, "BRIQ_OTP_APP_KEY", "") or "").strip()
    base_url = getattr(settings, "BRIQ_OTP_BASE_URL", "https://karibu.briq.tz/v1/otp")
    message_template = getattr(settings, "BRIQ_OTP_MESSAGE_TEMPLATE", "Your verification code for KKKT-DMP is {code}")

    logger.info(
        "OTP Request config: api_key=%s, app_key=%s, base_url=%s, message_template=%s",
        _mask_key(api_key),
        _mask_key(app_key),
        base_url,
        message_template,
    )
    if not api_key or not app_key:
        return False, "OTP service is not configured."

    phone = normalize_tz_phone(phone_number)
    url = base_url.rstrip("/") + "/request"
    payload = {
        "phone_number": phone,
        "app_key": app_key,
        "otp_length": int(getattr(settings, "BRIQ_OTP_LENGTH", 6)),
        "minutes_to_expire": int(getattr(settings, "BRIQ_OTP_EXPIRE_MINUTES", 10)),
        "sender_id": "KKKTDMP",
        "delivery_method": getattr(settings, "BRIQ_OTP_DELIVERY_METHOD", "sms"),
        "message_template": message_template,
    }

    status, parsed, err = _briq_post_json(url=url, payload=payload, api_key=api_key)
    if status and 200 <= status < 300:
        return True, None

    detail = _format_briq_error(parsed, err) or "Failed to request OTP."
    logger.error(
        "Briq OTP request failed (status=%s, phone=%s, api_key=%s, app_key=%s, base_url=%s, detail=%s, parsed=%s)",
        status,
        phone,
        _mask_key(api_key),
        _mask_key(app_key),
        base_url,
        detail,
        parsed,
    )
    if status:
        return False, f"{detail} (HTTP {status})"
    return False, detail


def verify_signup_otp(*, phone_number: str, code: str) -> tuple[bool, str | None]:
    api_key = (getattr(settings, "BRIQ_OTP_API_KEY", "") or "").strip()
    app_key = (getattr(settings, "BRIQ_OTP_APP_KEY", "") or "").strip()
    base_url = getattr(settings, "BRIQ_OTP_BASE_URL", "https://karibu.briq.tz/v1/otp")

    if not api_key or not app_key:
        return False, "OTP service is not configured."

    phone = normalize_tz_phone(phone_number)
    url = base_url.rstrip("/") + "/verify"
    payload = {
        "phone_number": phone,
        "app_key": app_key,
        "code": (code or "").strip(),
    }

    status, parsed, err = _briq_post_json(url=url, payload=payload, api_key=api_key)
    if status and 200 <= status < 300:
        return True, None

    detail = _format_briq_error(parsed, err) or "Invalid verification code."
    logger.error(
        "Briq OTP verify failed (status=%s, phone=%s, api_key=%s, app_key=%s, base_url=%s, detail=%s, parsed=%s)",
        status,
        phone,
        _mask_key(api_key),
        _mask_key(app_key),
        base_url,
        detail,
        parsed,
    )
    if status:
        return False, f"{detail} (HTTP {status})"
    return False, detail
