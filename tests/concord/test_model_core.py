from concord232 import model

def test_zone_bypassed():
    z = model.Zone(1)
    z.condition_flags = ['Bypass']
    assert z.bypassed is True
    z.condition_flags = ['Inhibit']
    assert z.bypassed is True
    z.condition_flags = []
    assert z.bypassed is False

def test_partition_armed():
    p = model.Partition(1)
    p.condition_flags = ['Armed']
    assert p.armed is True
    p.condition_flags = []
    assert p.armed is False

def test_zone_init():
    z = model.Zone(5)
    assert z.number == 5
    assert z.name == 'Unknown'
    assert z.state is None
    assert z.condition_flags == []
    assert z.type_flags == []

def test_partition_init():
    p = model.Partition(2)
    assert p.number == 2
    assert p.condition_flags == []
    assert p.last_user is None

def test_system_status_flags():
    s = model.System()
    assert isinstance(s.STATUS_FLAGS, list) 