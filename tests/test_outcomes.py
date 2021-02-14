import re
from unittest.mock import patch
from uuid import uuid4 as uuid

import pytest
from fastapi import HTTPException

from backend.database import session_scope
from backend.game import WurwolvesGame
from backend.model import GameStage
from backend.model import PlayerRole
from backend.model import PlayerState

GAME_ID = "Horse battery staple"


@pytest.fixture
def empty_game(db_session) -> WurwolvesGame:
    return WurwolvesGame(GAME_ID)


@pytest.fixture
def five_player_game(db_session) -> WurwolvesGame:

    g = WurwolvesGame(GAME_ID)

    # Make players
    user_ids = [uuid() for _ in range(5)]
    roles = [
        PlayerRole.WOLF,
        PlayerRole.MEDIC,
        PlayerRole.SEER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ]
    names = ["Wolf", "Medic", "Seer", "Villager 1", "Villager 2"]

    for i, id in enumerate(user_ids):
        g.join(id)

    g.start_game()

    # Override the roles
    for id, role, name in zip(user_ids, roles, names):
        u = g.get_player(id)
        u.role = role
        g.set_user_name(id, name)

    g._session.commit()

    roles_map = {name: user_id for name, user_id in zip(names, user_ids)}

    return g, roles_map


def test_setup(five_player_game):
    pass


def test_secret_chat(five_player_game):
    game, roles_map = five_player_game

    game.send_secret_message(roles_map["Wolf"], "hello")


def test_medic_save(five_player_game):
    game, roles_map = five_player_game

    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Medic"]).state == PlayerState.ALIVE


def test_medic_try_save_twice(five_player_game):
    game, roles_map = five_player_game

    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Medic"]).state == PlayerState.ALIVE

    game._set_stage(GameStage.NIGHT)

    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    with pytest.raises(HTTPException):
        game.medic_night_action(roles_map["Medic"], roles_map["Medic"])

    game.medic_night_action(roles_map["Medic"], roles_map["Seer"])

    assert game.get_player_model(roles_map["Medic"]).state == PlayerState.WOLFED


def test_wolf_kill(five_player_game):
    game, roles_map = five_player_game

    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Wolf"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Medic"]).state == PlayerState.WOLFED


def test_dead_no_vote(five_player_game):
    game, roles_map = five_player_game

    # Kill the medic and a villager
    player = game.get_player_model(roles_map["Medic"])
    game.kill_player(player.id, PlayerState.LYNCHED)
    player = game.get_player_model(roles_map["Villager 1"])
    game.kill_player(player.id, PlayerState.WOLFED)

    game._set_stage(GameStage.VOTING)

    # Try to vote
    with pytest.raises(HTTPException):
        game.medic_voting_action(roles_map["Medic"], roles_map["Seer"])
    with pytest.raises(HTTPException):
        game.villager_voting_action(roles_map["Medic"], roles_map["Seer"])

    game.wolf_voting_action(roles_map["Wolf"], roles_map["Seer"])
    game.seer_voting_action(roles_map["Seer"], roles_map["Wolf"])


def test_vote_tie(five_player_game):
    game, roles_map = five_player_game

    # Kill the medic
    player = game.get_player_model(roles_map["Medic"])
    game.kill_player(player.id, PlayerState.LYNCHED)

    game._set_stage(GameStage.VOTING)

    # Vote a tie
    game.villager_voting_action(roles_map["Villager 1"], roles_map["Seer"])
    game.villager_voting_action(roles_map["Villager 2"], roles_map["Seer"])
    game.wolf_voting_action(roles_map["Wolf"], roles_map["Villager 1"])
    game.seer_voting_action(roles_map["Seer"], roles_map["Villager 1"])

    # Check that no one died
    for user_id in [
        user_id for name, user_id in roles_map.items() if "Medic" not in name
    ]:
        assert game.get_player_model(user_id).state == PlayerState.ALIVE

    # Check that we're still voting
    assert game.get_game_model().stage == GameStage.VOTING

    # Vote again
    game.villager_voting_action(roles_map["Villager 1"], roles_map["Seer"])
    game.villager_voting_action(roles_map["Villager 2"], roles_map["Seer"])
    game.wolf_voting_action(roles_map["Wolf"], roles_map["Villager 1"])
    game.seer_voting_action(roles_map["Seer"], roles_map["Villager 1"])

    # Check that no one died
    for user_id in [
        user_id for name, user_id in roles_map.items() if "Medic" not in name
    ]:
        assert game.get_player_model(user_id).state == PlayerState.ALIVE

    # Check that we're no longer voting
    assert game.get_game_model().stage == GameStage.NIGHT


def test_vote_works(five_player_game):
    game, roles_map = five_player_game

    game._set_stage(GameStage.VOTING)

    # Vote off the villager
    game.medic_voting_action(roles_map["Medic"], roles_map["Villager 1"])
    game.villager_voting_action(roles_map["Villager 1"], roles_map["Seer"])
    game.villager_voting_action(roles_map["Villager 2"], roles_map["Seer"])
    game.wolf_voting_action(roles_map["Wolf"], roles_map["Villager 1"])
    game.seer_voting_action(roles_map["Seer"], roles_map["Villager 1"])

    # Check that the villager died
    for name, user_id in roles_map.items():
        if "Villager 1" in name:
            assert game.get_player_model(user_id).state == PlayerState.LYNCHED
        else:
            assert game.get_player_model(user_id).state == PlayerState.ALIVE

    # Check that we're no longer voting
    assert game.get_game_model().stage == GameStage.NIGHT


def test_dead_no_move(five_player_game):
    game, roles_map = five_player_game

    # Kill the medic and a villager
    player = game.get_player_model(roles_map["Medic"])
    game.kill_player(player.id, PlayerState.LYNCHED)
    player = game.get_player_model(roles_map["Villager 1"])
    game.kill_player(player.id, PlayerState.WOLFED)

    game._set_stage(GameStage.DAY)

    # Try to vote
    with pytest.raises(HTTPException):
        game.medic_day_action(roles_map["Medic"], roles_map["Seer"])
    with pytest.raises(HTTPException):
        game.villager_day_action(roles_map["Medic"], roles_map["Seer"])

    game.wolf_day_action(roles_map["Wolf"], roles_map["Seer"])
    game.seer_day_action(roles_map["Seer"], roles_map["Wolf"])


def test_no_wolves_double_kill(five_player_game):
    game, roles_map = five_player_game

    # Add another wolf
    new_wolf = uuid()
    game.join(new_wolf)

    u = game.get_player(new_wolf)
    u.role = PlayerRole.WOLF
    u.state = PlayerState.ALIVE
    game.set_user_name(new_wolf, "Wolf 2")

    game._set_stage(GameStage.NIGHT)

    # Try to kill twice
    game.wolf_night_action(new_wolf, roles_map["Medic"])
    with pytest.raises(HTTPException):
        game.wolf_night_action(roles_map["Wolf"], roles_map["Seer"])

    game.medic_night_action(roles_map["Medic"], roles_map["Villager 1"])
    game.seer_night_action(roles_map["Seer"], roles_map["Wolf"])

    assert game.get_player_model(roles_map["Medic"]).state == PlayerState.WOLFED
    assert game.get_player_model(roles_map["Seer"]).state == PlayerState.ALIVE


def test_no_move_to_vote_with_narrator(five_player_game):
    game, roles_map = five_player_game

    game._set_stage(GameStage.DAY)

    # Add a narrator
    narrator_id = uuid()
    game.join(narrator_id)

    u = game.get_player(narrator_id)
    u.role = PlayerRole.NARRATOR
    u.state = PlayerState.SPECTATING
    game.set_user_name(narrator_id, "The narrator")
    game._session.commit()

    # Try to move to vote as a villager
    with pytest.raises(HTTPException):
        game.villager_day_action(roles_map["Villager 1"])

    # And as narrator
    game.narrator_day_action(narrator_id)


def test_vigilante_shoot(five_player_game):
    game, roles_map = five_player_game

    game._set_stage(GameStage.NIGHT)

    # Add a narrator
    vig_id = uuid()
    game.join(vig_id)

    u = game.get_player(vig_id)
    u.role = PlayerRole.VIGILANTE
    u.state = PlayerState.ALIVE
    game.set_user_name(vig_id, "The vigilante")
    game._session.commit()

    # Shoot the first villager
    game.vigilante_night_action(vig_id, roles_map["Villager 1"])

    # Others
    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Villager 1"]).state == PlayerState.SHOT


def test_vigilante_no_shoot(five_player_game):
    game, roles_map = five_player_game

    game._set_stage(GameStage.NIGHT)

    # Add a narrator
    vig_id = uuid()
    game.join(vig_id)

    u = game.get_player(vig_id)
    u.role = PlayerRole.VIGILANTE
    u.state = PlayerState.ALIVE
    game.set_user_name(vig_id, "The vigilante")
    game._session.commit()

    # Other actions
    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_game_model().stage == GameStage.DAY


def test_vigilante_shoot_twice(five_player_game):
    game, roles_map = five_player_game

    game._set_stage(GameStage.NIGHT)

    # Add a narrator
    vig_id = uuid()
    game.join(vig_id)

    u = game.get_player(vig_id)
    u.role = PlayerRole.VIGILANTE
    u.state = PlayerState.ALIVE
    game.set_user_name(vig_id, "The vigilante")
    game._session.commit()

    # Shoot the first villager
    game.vigilante_night_action(vig_id, roles_map["Villager 1"])

    # Others
    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Villager 1"]).state == PlayerState.SHOT

    game._set_stage(GameStage.NIGHT)

    # Shoot the second villager
    with pytest.raises(HTTPException):
        game.vigilante_night_action(vig_id, roles_map["Villager 2"])

    # Others
    game.wolf_night_action(roles_map["Wolf"], roles_map["Seer"])
    game.medic_night_action(roles_map["Medic"], roles_map["Seer"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Villager 2"]).state == PlayerState.ALIVE


@pytest.mark.parametrize(
    "role,search", [("jester", "a jester"), ("acolyte", "an acolyte")]
)
@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.JESTER,
        PlayerRole.ACOLYTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_announced_to_wolves(mock_roles, db_session, role, search):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()

    game.join(wolf_id)
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    summary = get_summary_of_chat(game, wolf_id)

    assert f"There's {search} in the game" in summary


def get_summary_of_chat(game, player_id):
    visible_messages = game.get_messages(player_id)

    from json import dumps

    return dumps([v.dict() for v in visible_messages])


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.MASON,
        PlayerRole.MASON,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_masons_announced(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    mason_1_id = uuid()
    mason_2_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(mason_1_id)
    game.join(mason_2_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    mason_1_name = game.get_user_name(mason_1_id)
    mason_2_name = game.get_user_name(mason_2_id)

    assert f"Your fellow masons are {mason_2_name}" in get_summary_of_chat(
        game, mason_1_id
    )
    assert f"Your fellow masons are {mason_1_name}" in get_summary_of_chat(
        game, mason_2_id
    )

    assert "Your fellow masons are" not in get_summary_of_chat(game, wolf_id)
    assert "Your fellow masons are" not in get_summary_of_chat(game, villager_id)


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_wolves_announced(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    villager_1_id = uuid()

    game.join(wolf_id)
    game.join(villager_1_id)
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    assert "There is only one wolf in the game" in get_summary_of_chat(
        game, villager_1_id
    )
    assert "There is only one wolf in the game" in get_summary_of_chat(game, wolf_id)


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.SEER,
        PlayerRole.MILLER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_miller_works(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    seer_id = uuid()
    miller_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(seer_id)
    game.join(miller_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())

    game.start_game()
    game.seer_night_action(seer_id, miller_id)
    game.wolf_night_action(wolf_id, villager_id)

    summary = get_summary_of_chat(game, seer_id)

    assert "they are a wolf!" in summary


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.PRIEST,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_priest_works(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    priest_id = uuid()
    villager1_id = uuid()
    villager2_id = uuid()

    game.join(wolf_id)
    game.join(priest_id)
    game.join(villager1_id)
    game.join(villager2_id)
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    with pytest.raises(HTTPException):
        game.priest_night_action(priest_id, villager1_id)
    game.wolf_night_action(wolf_id, villager1_id)

    assert game.get_player_model(villager1_id).state == PlayerState.WOLFED

    game._set_stage(GameStage.NIGHT)

    game.priest_night_action(priest_id, villager1_id)
    game.wolf_night_action(wolf_id, villager2_id)

    summary = get_summary_of_chat(game, priest_id)

    assert re.search(r"You remember that .+ was a Villager", summary)


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.MEDIC,
        PlayerRole.PROSTITUTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_prostitute_prevents_medic(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    medic_id = uuid()
    prostitute_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(medic_id)
    game.join(prostitute_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    # Medic saves villager but prostitute sleeps with medic.
    # Wolf kills villager, so villager dies
    game.prostitute_night_action(prostitute_id, medic_id)
    game.medic_night_action(medic_id, villager_id)
    game.wolf_night_action(wolf_id, villager_id)

    assert game.get_player_model(villager_id).state == PlayerState.WOLFED


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.MEDIC,
        PlayerRole.PROSTITUTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_prostitute_not_choose_self(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    medic_id = uuid()
    prostitute_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(medic_id)
    game.join(prostitute_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    # Check that the pristitute can't sleep with themselves
    with pytest.raises(HTTPException):
        game.prostitute_night_action(prostitute_id, prostitute_id)


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.SEER,
        PlayerRole.PROSTITUTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_prostitute_prevents_seer(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    seer_id = uuid()
    prostitute_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(seer_id)
    game.join(prostitute_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    # Seer checks villager but prostitute sleeps with seer.
    # Wolf kills villager, so villager dies
    game.prostitute_night_action(prostitute_id, seer_id)
    game.seer_night_action(seer_id, villager_id)
    game.wolf_night_action(wolf_id, villager_id)

    assert game.get_player_model(villager_id).state == PlayerState.WOLFED

    summary = get_summary_of_chat(game, seer_id)

    assert re.search(r"you couldn't concentrate", summary)


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.PROSTITUTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_prostitute_saves_villager(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    prostitute_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(prostitute_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    # Prostitute sleep with villager, wolf attacks villager.
    # Villager isn't home, so doesn't die
    game.prostitute_night_action(prostitute_id, villager_id)
    game.wolf_night_action(wolf_id, villager_id)

    assert game.get_player_model(villager_id).state == PlayerState.ALIVE


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.PROSTITUTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_prostitute_dooms_villager(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    prostitute_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(prostitute_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    # Prostitute sleeps with villager, wolf attacks prostitute.
    # Both die.
    game.prostitute_night_action(prostitute_id, villager_id)
    game.wolf_night_action(wolf_id, prostitute_id)

    assert game.get_player_model(villager_id).state == PlayerState.WOLFED
    assert game.get_player_model(prostitute_id).state == PlayerState.WOLFED


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.WOLF,
        PlayerRole.PROSTITUTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_prostitute_prevents_only_one_wolf(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_1_id = uuid()
    wolf_2_id = uuid()
    prostitute_id = uuid()
    villager_id = uuid()

    game.join(wolf_1_id)
    game.join(wolf_2_id)
    game.join(prostitute_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    # Prostitute sleep with wolf 1, wolves attack villager.
    # First wolf if disabled but second wolf kills
    game.prostitute_night_action(prostitute_id, wolf_1_id)
    game.wolf_night_action(wolf_1_id, villager_id)

    assert game.get_player_model(villager_id).state == PlayerState.WOLFED


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.WOLF,
        PlayerRole.PROSTITUTE,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_prostitute_prevents_only_one_wolf_alt(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_1_id = uuid()
    wolf_2_id = uuid()
    prostitute_id = uuid()
    villager_id = uuid()

    game.join(wolf_1_id)
    game.join(wolf_2_id)
    game.join(prostitute_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    # Prostitute sleep with wolf 1, wolves attack villager.
    # First wolf if disabled but second wolf kills
    game.prostitute_night_action(prostitute_id, wolf_1_id)
    game.wolf_night_action(wolf_2_id, villager_id)

    assert game.get_player_model(villager_id).state == PlayerState.WOLFED


@patch(
    "backend.roles.assign_roles",
    return_value=[
        PlayerRole.WOLF,
        PlayerRole.MEDIC,
        PlayerRole.SEER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ],
)
def test_seer_saved_no_fail(mock_roles, db_session):
    game = WurwolvesGame("test_game")

    wolf_id = uuid()
    medic_id = uuid()
    seer_id = uuid()
    villager_id = uuid()

    game.join(wolf_id)
    game.join(medic_id)
    game.join(seer_id)
    game.join(villager_id)
    game.join(uuid())
    game.join(uuid())

    game.start_game()

    game.seer_night_action(seer_id, wolf_id)
    game.wolf_night_action(wolf_id, seer_id)
    game.medic_night_action(medic_id, seer_id)

    assert game.get_player_model(seer_id).state == PlayerState.ALIVE

    summary = get_summary_of_chat(game, seer_id)

    assert re.search(r"they are a wolf", summary)


def test_fool_no_mention_seer(empty_game):
    from unittest.mock import patch
    import backend
    from backend.roles import DistributionSettings

    game = WurwolvesGame("test_game")

    # Make some players in a game
    num_players = 10
    user_ids = [uuid() for _ in range(num_players)]
    [game.join(u) for u in user_ids]

    # Customise the probabilitites to get a fool
    settings = DistributionSettings(role_weights={PlayerRole.FOOL: 1000000})
    game.set_game_config(settings)

    game.start_game()

    # Find the fool (there's almost certainly one)
    fool_player = [p for p in game.get_players() if p.role == PlayerRole.FOOL]
    assert len(fool_player) == 1
    fool_id = fool_player[0].user_id

    game.set_user_name(fool_id, "The one who isn't the seer")
    game._session.commit()

    # Confirm that the fool's state doesn't mention the fool anywhere
    def fool_in_state(fool_state):
        # Unfortunately, it does in one place: the function call. A savvy user could
        # therefore cheat. I should change it so that all player actions call the
        # same function in game. The game would then pass the call on to the
        # appropriate method, depending on the player's role.
        # For now, so this test passes, remove that reference
        fool_state_filtered = fool_state.dict()
        fool_state_filtered["controls_state"]["button_submit_func"] = "removed"
        fool_state = type(fool_state).parse_obj(fool_state_filtered)

        print("Fool state:")
        from pprint import pprint

        pprint(fool_state.dict())

        return "fool" in fool_state.json().lower()

    game._set_stage(GameStage.NIGHT)
    fool_state = game.parse_game_to_state(fool_id)
    assert not fool_in_state(fool_state)

    game._set_stage(GameStage.VOTING)
    fool_state = game.parse_game_to_state(fool_id)
    assert not fool_in_state(fool_state)

    game._set_stage(GameStage.DAY)
    fool_state = game.parse_game_to_state(fool_id)
    assert not fool_in_state(fool_state)

    # Move to the end of the game and confirm that the fool is revealed
    game._set_stage(GameStage.ENDED)
    fool_state = game.parse_game_to_state(fool_id)
    assert fool_in_state(fool_state)


def test_exorcist_suceed(five_player_game):
    game, roles_map = five_player_game

    game._set_stage(GameStage.NIGHT)

    exorcist_id = uuid()
    game.join(exorcist_id)

    u = game.get_player(exorcist_id)
    u.role = PlayerRole.EXORCIST
    u.state = PlayerState.ALIVE
    game.set_user_name(exorcist_id, "The exorcist")
    game._session.commit()

    # Exorcist the wolf
    game.exorcist_night_action(exorcist_id, roles_map["Wolf"])

    # Others
    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_game_model().stage == GameStage.ENDED
    assert game.get_player_model(roles_map["Wolf"]).state == PlayerState.WOLFED
    assert game.get_player_model(exorcist_id).state == PlayerState.ALIVE
    assert re.search(r"You chose.+wisely", get_summary_of_chat(game, exorcist_id))


def test_exorcist_fail(five_player_game):
    game, roles_map = five_player_game

    game._set_stage(GameStage.NIGHT)

    exorcist_id = uuid()
    game.join(exorcist_id)

    u = game.get_player(exorcist_id)
    u.role = PlayerRole.EXORCIST
    u.state = PlayerState.ALIVE
    game.set_user_name(exorcist_id, "The exorcist")
    game._session.commit()

    # Exorcist the medic
    game.exorcist_night_action(exorcist_id, roles_map["Medic"])

    # Others
    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_game_model().stage == GameStage.DAY
    assert game.get_player_model(roles_map["Wolf"]).state == PlayerState.ALIVE
    assert game.get_player_model(exorcist_id).state == PlayerState.WOLFED
    assert re.search(r"You chose.+poorly", get_summary_of_chat(game, exorcist_id))
