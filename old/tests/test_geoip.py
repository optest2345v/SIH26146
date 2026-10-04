"""
SIH26146 — Offline Geo-IP Module Test Suite
Fulfills REQ-014 (Local Geo-IP support without external APIs).
"""

from src.geoip.local_geoip import OfflineGeoIP, default_geoip


def test_offline_private_ip():
    loc = default_geoip.lookup("192.168.1.100")
    assert loc.is_private is True
    assert loc.country_code == "PRIVATE"

    loc_10 = default_geoip.lookup("10.0.0.5")
    assert loc_10.is_private is True


def test_offline_loopback_ip():
    loc = default_geoip.lookup("127.0.0.1")
    assert loc.country_code == "LOOPBACK"


def test_offline_known_subnets():
    # Cloudflare IP
    loc = default_geoip.lookup("1.1.1.1")
    assert loc.country_code == "US"
    assert loc.asn == "AS13335"

    # Tor exit node subnet
    loc_tor = default_geoip.lookup("185.220.101.45")
    assert loc_tor.country_code == "DE"
    assert loc_tor.asn == "AS208294"


def test_offline_malformed_ip():
    loc = default_geoip.lookup("invalid.ip.string")
    assert loc.country_code == "MALFORMED"

    loc_none = default_geoip.lookup(None)
    assert loc_none.country_code == "UNKNOWN"
