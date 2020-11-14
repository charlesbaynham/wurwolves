export const help_text = `
Werewolves is a social game for groups of 5 players or more. You need to be able to talk to each other to play, so either meet in person or start up a video call. If you've ever played Mafia, the rules are almost identical.

You live in a small village, tragically afflicted with an ancient curse: some of your members are Werewolves. Each night the Werewolves will kill someone. Fortunately you are not defenseless: each day the villager vote to lynch someone. Unfortunately, you don't know who the werewolves are, so they get to vote too. The game is won by the villagers if they eliminate all the wolves. It's won by the wolves if they can kill enough of the villagers that the wolves are 50% of the village's population.

There are several special characters to help (or hinder) the villagers. These are assigned randomly each night, and may or may not be present in the game. Your character is displayed at the bottom of the page, with a description of your special powers. Don't forget to check the Events box to learn any secret information that you're entitled to know. If you have a team mate (for example, the wolves know who each other are) then a chat box will appear under the Events box for you to chat in secret.

The game has three stages:

**Night** - The wolves kill someone, and many other special characters act too. If you have an action at night, select your target then click the blue button.

**Day** - The events of the night are revealed and the villagers must decide who to lynch. When everyone has Moved to Vote, the voting begins.

**Voting** - Vote who to lynch. Select your vote and click the blue button. Votes will be announced in public after the results are decided.

To learn about all the roles, click below:
`

class RoleDescription {
    constructor(name, image, description) {
      this.name = name;
      this.image = image;
      this.description = description.trim();
    }
  }

export const roles = [
    new RoleDescription("Narrator", null,
    "The Narrator is not like most roles. They are not a part of the game, and will never be assigned at the start of the game. Once a player dies, they are given the option to become Narrator. If they choose to do so, they will have everyone's roles revealed to them and they gain the sole power to decide when the voting begins. They should use their position to move the game along and keep discussions from becoming too long."
    )
]

export default null;
