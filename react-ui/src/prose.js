export const help_text = `
Werewolves is a social game for groups of 5 players or more. You need to be able to talk to each other to play, so either meet in person or start up a video call. If you've ever played Mafia, the rules are almost identical.

You live in a small village, tragically afflicted with an ancient curse: some of your members are Werewolves. Each night the Werewolves will kill someone. Fortunately you are not defenseless: each day the villager vote to lynch someone. Unfortunately, you don't know who the werewolves are, so they get to vote too. The game is won by the villagers if they eliminate all the wolves. It's won by the wolves if they can kill enough of the villagers that the wolves are 50% of the village's population.

There are several special characters to help (or hinder) the villagers. These are assigned randomly each night, and may or may not be present in the game. Your character is displayed at the bottom of the page, with a description of your special powers.

The game has three stages:

**Night** - The wolves kill someone, and many other special characters act too. If you have an action at night, select your target then click the blue button.

**Day** - The events of the night are revealed and the villagers must decide who to lynch. When everyone has Moved to Vote, the voting begins.

**Voting** - Vote who to lynch. Select your vote and click the blue button. Votes will be announced in public after the results are decided.

**Tips:**

* Don't forget to check the Events box to learn any secret information that you're entitled to know.
* If you have a team mate (for example, a fellow wolf) then a chat box will appear under the Events box for you to chat privately.
* Your picture might look different to you than to other people! They will see you as a normal villager unless they have secret information.
* To learn about all the roles, click the Roles tab above.
`

export const settings_text = 'Use these utilities to manage the game if something needs fixing.'

class RoleDescription {
    constructor(name, level, image, description) {
        this.name = name;
        this.image = image;
        this.description = description.trim();
        this.level = level;
    }
}

export const guaranteed_roles = [
    new RoleDescription("Villager", 0, "/images/characters/villager9.svg", `
The salt of the earth. A humble villager who just wants to live their life in peace. They have no special powers, except for the power of democracy.
    `),
    new RoleDescription("Wolf", 0, "/images/characters/wolf3.svg", `
A terrifying werewolf. Every night, the wolves must kill one person. They should decide together who to kill: the first wolf to select someone chooses for the team.

For 3-6 players there is 1 wolf, for 7-9 there are 2, for 10-15 players there are three and for more than 15 the wolves will be about 1/5 of the players.
    `),
    new RoleDescription("Seer", 0, "/images/characters/seer0.svg", `
A reclusive mystic, blessed with the third eye. Present in every game.

The seer checks the alignment of one person each night. They will find out if that person is a wolf, or not. The seer is the most powerful character on the villagers' side!
    `),
    new RoleDescription("Medic", 0, "/images/characters/medic0.svg", `
The neighbourhood medic. Present in every game.

The medic chooses one person to save each night. They can choose themselves, but they can't choose the same person twice in a row.
    `),
    new RoleDescription("Narrator", 0, null, `
The Narrator is not like most roles. They are not a part of the game, and will never be assigned at the start of the game. Once a player dies, they are given the option to become Narrator. If they choose to do so, they will have everyone's roles revealed to them and they gain the sole power to decide when the voting begins. They should use their position to move the game along and keep discussions from becoming too long.
    `),
]

export const random_roles = [
    new RoleDescription("Jester", 1, "/images/characters/jester0.svg", `
A thorn in the side of the villagers. The Jester is not trying to help: their objective is to get themselves lynched. Usually, they should act as much like a wolf as possible. The wolves know who the Jester is, but the Jester doesn't know who the wolves are.
    `),
    new RoleDescription("Vigilante", 1, "/images/characters/vigilante0.svg", `
The Vigilante knows what's best for this village - who needs psychic powers when you've got a gun?

Has a single bullet which they can use once per game to shoot someone during the night. Everyone will hear when this happens, but they won't know who shot. On the side of the villagers.
    `),
    new RoleDescription("Mayor", 1, "/images/characters/mayor0.svg", `
The Mayor is in charge here, and everyone knows it.

After the first night, the Mayor is publicly revealed so everyone knows who they are. While they live, there is no voting for lynching: the mayor makes the decision unilaterally. They can be killed by the wolves just like normal villagers.
    `),
    new RoleDescription("Miller", 1, "/images/characters/miller0.svg", `
Lives alone, never meets people and likes it that way.

The Miller is on the side of the villagers: unfortunately they don't recognize him. If the Seer checks the alignment of the Miller, they will seem like a wolf even though they're not.
    `),
    new RoleDescription("Acolyte", 2, "/images/characters/acolyte0.svg", `
Really wishes they were a werewolf. The Acolyte used to have a long fringe and listen to mopey rock, but now they worship the werewolves. They're sure that, if they work hard enough, the wolves will get in touch.

The acolyte wins if the werewolves win, but they have no special powers and don't know who the wolves are. The wolves do know who the acolyte is, however.
    `),
    new RoleDescription("Priest", 2, "/images/characters/priest0.svg", `
The most trusted person in the village: knows everyone's secrets.

The Priest, once per game, may check the **role** of a dead player. Unlike the Seer, they will find out the player's role (e.g. Medic), not just their alignment.
    `),
    new RoleDescription("Prostitute", 2, "/images/characters/prostitute0.svg", `
Her charms are impossible to resist.

The prostitute does two things: some people find her very confusing. Firstly, she prevents her target from performing their special power, if they have one. If she selects one of the wolves, the other will still make a kill.

Secondly, she brings her target back to her house. That means that if the wolves attack her target, they're not home and do not die. However, if the wolves attack the Prostitute, the wolves find the two in bed together and kill both.
    `),
    new RoleDescription("Masons", 2, "/images/characters/mason0.svg", `
They always knew that a secret society would come in useful.

The Masons do not have special powers, but they know each other's identity (they always come as a pair). They are on the side of the villagers.

    `),
    new RoleDescription("Exorcist", 2, "/images/characters/exorcist0.svg", `
The Exorcist has dabbled in the occult from a young age. Now, with the village beset by werewolves, it's finally their chance to use their knowledge.

The Exorcist is on the side of the villagers and, once per game, can perform a dark ritual to use the werewolves' powers against them: killing their target in the night. Unfortunately, if the exorcist accidentally performs the ritual on a non-wolf target, the Exorcist is instead rent by the powers they summoned from the deep.
    `),
    new RoleDescription("Fool", 2, "/images/characters/fool0.svg", `
The Fool is earnest and 100% on the side of the villagers.
In fact, they're so excited to help out that they see visions in the night of who
is good and who is bad. Unfortunately they're just dreams: the Fool
has no real information at all.

The Fool is on the side of the villagers. However, the Fool doesn't know that they
are a Fool (such is life) - they think that they are the Seer. Every night they get to check
someone's alignment and will receive an answer. This answer will just be random however:
the Fool's visions are really just dreams.
    `),
]

export default null;
