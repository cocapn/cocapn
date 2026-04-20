from fleet_homunculus.core import Homunculus, ReflexArc, PainLevel, BodyState


def test_body_state_health():
    state = BodyState(cpu_percent=50, memory_percent=60, disk_percent=70)
    assert state.is_healthy()
    
    state.cpu_percent = 95
    assert not state.is_healthy()


def test_homunculus_pain():
    h = Homunculus("test-vessel")
    h.feel_pain("memory", PainLevel.PAIN, "OOM detected")
    assert len(h.pain_history) == 1
    assert h.pain_history[0].source == "memory"


def test_reflex():
    triggered = False
    def action():
        nonlocal triggered
        triggered = True
    
    h = Homunculus("test")
    h.add_reflex(ReflexArc(
        name="cpu_alert",
        condition=lambda s: s.cpu_percent > 80,
        action=action,
        cooldown_seconds=0,
    ))
    h.update_state(cpu_percent=90)
    assert triggered
