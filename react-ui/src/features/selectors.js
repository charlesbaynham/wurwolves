export const selectMessages = (state => state.backend.chat);

export const selectStage = (state => state.backend.stage);

export const selectMyID = (state => state.backend.myID);
export const selectMyName = (state => state.backend.myName);
export const selectMyNameIsGenerated = (state => state.backend.myNameIsGenerated);


export function getPlayerById(players, id) {
    return players.find(p => id === p.id);
}

export const selectPlayer = id => (state => getPlayerById(state.backend.players, id));

export const selectPlayerName = id => (state => getPlayerById(state.backend.players, id).name);
export const selectPlayerStatus = id => (state => getPlayerById(state.backend.players, id).status);

export const selectAllPlayers = state => state.backend.players;

export const selectRoles = (state => state.backend.roles);

export const selectStateHash = (state => state.backend.state_hash);

// Frontend stuff:

export const selectSelectedPlayer = (state => state.selectedPlayer)