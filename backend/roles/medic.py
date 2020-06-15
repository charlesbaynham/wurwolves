from .common import RoleDescription, DEFAULT_ROLE, GameAction


MEDIC = RoleDescription(
    display_name="Medic",
    night_action=True,
    day_text="""
You are a medic! You get to save one person each night. 

You win if all the wolves are eliminated. 
    """,
    night_text="""
Choose who to save...
    """,
    vote_text=None,
    fallback_role=DEFAULT_ROLE,
)


class MedicAction(GameAction):
    def execute(self, game):
        pass


class MedicMixin():
    def medic_action(self, payload):
        print(payload)
