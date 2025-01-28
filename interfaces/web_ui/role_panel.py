class RolePanel:
    def render_cooldowns(self, player):
        return {
            skill: {
                'current': cd,
                'max': self.config['ROLE_COOLDOWNS'].get(
                    type(player.role).__name__.lower(), {}
                ).get(skill, cd)
            }
            for skill, cd in player.role.cooldowns.items()
        } 