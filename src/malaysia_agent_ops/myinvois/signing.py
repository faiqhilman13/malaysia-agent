"""Digital signature for v1.1 (and SVDP 1.3) documents, following the LHDN SDK signature steps for JSON.

1. Remove UBLExtensions and Signature, minify, and hash the document (DocDigest).
2. Sign the minified document with RSA-SHA256 using the certificate's private key.
3. Hash the certificate (CertDigest) and build the XAdES SignedProperties.
4. Hash the minified SignedProperties (PropsDigest).
5. Insert UBLExtensions and Signature into the document.

UNVERIFIED: this follows the published steps but has not yet been validated against LHDN preprod.
Run the nightly preprod round-trip before relying on it in production; keep version 1.0 until then.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs12

from ..errors import NotConfigured
from .ubl import serialize, v

SHA256_URI = "http://www.w3.org/2001/04/xmlenc#sha256"
RSA_SHA256_URI = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
SIGNED_PROPS_ID = "id-xades-signed-props"


@dataclass(frozen=True)
class SigningKey:
    certificate: x509.Certificate
    private_key: rsa.RSAPrivateKey

    @classmethod
    def from_secret(cls, secret: dict[str, Any]) -> SigningKey:
        """Load from a vault secret: {"pkcs12_b64", "password"} or {"cert_pem", "key_pem"}."""
        if "pkcs12_b64" in secret:
            password = secret.get("password")
            key, cert, _ = pkcs12.load_key_and_certificates(
                base64.b64decode(secret["pkcs12_b64"]), password.encode() if password else None
            )
        elif "cert_pem" in secret and "key_pem" in secret:
            cert = x509.load_pem_x509_certificate(secret["cert_pem"].encode())
            key = serialization.load_pem_private_key(secret["key_pem"].encode(), password=None)
        else:
            raise NotConfigured("Signing certificate secret must hold pkcs12_b64 or cert_pem + key_pem.")
        if cert is None or not isinstance(key, rsa.RSAPrivateKey):
            raise NotConfigured("Signing certificate must contain an RSA private key and certificate.")
        return cls(certificate=cert, private_key=key)


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _minify(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def strip_signature(document: dict[str, Any]) -> dict[str, Any]:
    stripped = copy.deepcopy(document)
    invoice = stripped["Invoice"][0]
    invoice.pop("UBLExtensions", None)
    invoice.pop("Signature", None)
    return stripped


def sign_document(document: dict[str, Any], key: SigningKey, signing_time: datetime | None = None) -> dict[str, Any]:
    unsigned = strip_signature(document)
    unsigned_bytes = serialize(unsigned)
    doc_digest = _b64(hashlib.sha256(unsigned_bytes).digest())
    signature_value = _b64(key.private_key.sign(unsigned_bytes, padding.PKCS1v15(), hashes.SHA256()))

    cert = key.certificate
    cert_der = cert.public_bytes(serialization.Encoding.DER)
    cert_digest = _b64(hashlib.sha256(cert_der).digest())
    issuer_name = cert.issuer.rfc4514_string()
    serial = str(cert.serial_number)
    when = (signing_time or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    signed_properties = {
        "Id": SIGNED_PROPS_ID,
        "SignedSignatureProperties": [
            {
                "SigningTime": v(when),
                "SigningCertificate": [
                    {
                        "Cert": [
                            {
                                "CertDigest": [
                                    {
                                        "DigestMethod": [{"_": "", "Algorithm": SHA256_URI}],
                                        "DigestValue": v(cert_digest),
                                    }
                                ],
                                "IssuerSerial": [{"X509IssuerName": v(issuer_name), "X509SerialNumber": v(serial)}],
                            }
                        ]
                    }
                ],
            }
        ],
    }
    props_digest = _b64(hashlib.sha256(_minify(signed_properties)).digest())

    signature = {
        "Id": "signature",
        "Object": [{"QualifyingProperties": [{"Target": "signature", "SignedProperties": [signed_properties]}]}],
        "KeyInfo": [
            {
                "X509Data": [
                    {
                        "X509Certificate": v(_b64(cert_der)),
                        "X509SubjectName": v(cert.subject.rfc4514_string()),
                        "X509IssuerSerial": [{"X509IssuerName": v(issuer_name), "X509SerialNumber": v(serial)}],
                    }
                ]
            }
        ],
        "SignatureValue": v(signature_value),
        "SignedInfo": [
            {
                "SignatureMethod": [{"_": "", "Algorithm": RSA_SHA256_URI}],
                "Reference": [
                    {
                        "Type": "http://uri.etsi.org/01903/v1.3.2#SignedProperties",
                        "URI": f"#{SIGNED_PROPS_ID}",
                        "DigestMethod": [{"_": "", "Algorithm": SHA256_URI}],
                        "DigestValue": v(props_digest),
                    },
                    {
                        "Type": "",
                        "URI": "",
                        "DigestMethod": [{"_": "", "Algorithm": SHA256_URI}],
                        "DigestValue": v(doc_digest),
                    },
                ],
            }
        ],
    }

    signed = copy.deepcopy(unsigned)
    invoice = signed["Invoice"][0]
    invoice["UBLExtensions"] = [
        {
            "UBLExtension": [
                {
                    "ExtensionURI": v("urn:oasis:names:specification:ubl:dsig:enveloped:xades"),
                    "ExtensionContent": [
                        {
                            "UBLDocumentSignatures": [
                                {
                                    "SignatureInformation": [
                                        {
                                            "ID": v("urn:oasis:names:specification:ubl:signature:1"),
                                            "ReferencedSignatureID": v(
                                                "urn:oasis:names:specification:ubl:signature:Invoice"
                                            ),
                                            "Signature": [signature],
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                }
            ]
        }
    ]
    invoice["Signature"] = [
        {
            "ID": v("urn:oasis:names:specification:ubl:signature:Invoice"),
            "SignatureMethod": v("urn:oasis:names:specification:ubl:dsig:enveloped:xades"),
        }
    ]
    return signed


def verify_document(document: dict[str, Any]) -> bool:
    """Check the embedded signature and digests. Used in tests and as a pre-submission self-check."""
    invoice = document["Invoice"][0]
    sig = invoice["UBLExtensions"][0]["UBLExtension"][0]["ExtensionContent"][0]["UBLDocumentSignatures"][0][
        "SignatureInformation"
    ][0]["Signature"][0]
    unsigned_bytes = serialize(strip_signature(document))
    cert = x509.load_der_x509_certificate(base64.b64decode(sig["KeyInfo"][0]["X509Data"][0]["X509Certificate"][0]["_"]))
    references = sig["SignedInfo"][0]["Reference"]
    if references[1]["DigestValue"][0]["_"] != _b64(hashlib.sha256(unsigned_bytes).digest()):
        return False
    props = sig["Object"][0]["QualifyingProperties"][0]["SignedProperties"][0]
    if references[0]["DigestValue"][0]["_"] != _b64(hashlib.sha256(_minify(props)).digest()):
        return False
    public_key = cert.public_key()
    assert isinstance(public_key, rsa.RSAPublicKey)
    try:
        public_key.verify(
            base64.b64decode(sig["SignatureValue"][0]["_"]), unsigned_bytes, padding.PKCS1v15(), hashes.SHA256()
        )
    except Exception:
        return False
    return True
