import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import validators


def validate_domain(value):
    if not validators.domain(value):
        raise ValidationError(_("%(value)s is not a valid domain Name"), params={"value": value})


def validate_url(value):
    if not validators.url(value):
        raise ValidationError(_("%(value)s is not a valid URL Name"), params={"value": value})


def validate_short_name(value):
    regex = re.compile(r"[@!#$%^&*()<>?/\|}{~:]")
    if regex.search(value):
        raise ValidationError(
            _("%(value)s is not a valid short name," + " can only contain - and _"), params={"value": value}
        )


def validate_ip(ip):
    if not (validators.ipv4(ip) or validators.ipv6(ip)):
        raise ValidationError(_("Invalid IP address: %(ip)s"), params={"ip": ip})


from .import_validators import (
    CIDRValidator,
    DomainValidator,
    ImportValidationError,
    URLValidator,
)

__all__ = [
    "DomainValidator",
    "URLValidator",
    "CIDRValidator",
    "ImportValidationError",
    "validate_domain",
    "validate_url",
    "validate_short_name",
    "validate_ip",
]