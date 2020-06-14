export const selectMessages = (state => state.chat);

export const selectStage = (state => state.stage);

export const selectMyID = (state => state.myID);
export const selectMyName = (state => state.myName);
export const selectMyNameIsGenerated = (state => state.myNameIsGenerated);


export function getPlayerById(players, id) {
    return players.find(p => id === p.id);
}

export const selectPlayer = id => (state => getPlayerById(state.players, id));

export const selectPlayerName = id => (state => getPlayerById(state.players, id).name);
export const selectPlayerStatus = id => (state => getPlayerById(state.players, id).status);
export const selectPlayerSelected = id => (state => getPlayerById(state.players, id).selected);

export const selectAllPlayers = state => state.players;

export const selectRoles = (state => state.roles);

export const selectStateHash = (state => state.state_hash);
