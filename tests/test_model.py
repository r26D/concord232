from concord232.model import Zone

def test_zone_bypassed():
    zone = Zone(1)
    assert not zone.bypassed
    zone.condition_flags = ['Bypass']
    assert zone.bypassed
    zone.condition_flags = ['Inhibit']
    assert zone.bypassed
    zone.condition_flags = []
    assert not zone.bypassed 