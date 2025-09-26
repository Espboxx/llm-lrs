from modules.roles.seer import Seer


def test_seer_uses_configured_cooldown():
    custom_cooldowns = {'seer': {'check': 3}}
    config = {
        'ROLE_COOLDOWNS': custom_cooldowns,
        'SEER_CONFIG': {
            'max_checks': 3,
            'result_format': "{target}:{role}:{team}",
            'allow_self_check': False,
            'night_only': True,
        },
    }

    seer = Seer('seer1', config)

    assert seer.cooldowns['check'] == 0
    assert seer.cooldown_defaults['check'] == 3

    seer.use_skill('check')
    assert seer.cooldowns['check'] == 3


def test_seer_can_use_check_immediately():
    custom_cooldowns = {'seer': {'check': 3}}
    config = {
        'ROLE_COOLDOWNS': custom_cooldowns,
        'SEER_CONFIG': {
            'max_checks': 3,
            'result_format': "{target}:{role}:{team}",
            'allow_self_check': False,
            'night_only': True,
        },
    }

    seer = Seer('seer1', config)

    assert seer.can_use_skill('check') is True

    seer.use_skill('check')
    assert seer.cooldowns['check'] == 3
