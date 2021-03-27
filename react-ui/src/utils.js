
// const _ = require('lodash');


// This ID is used until the client is assigned a proper UUID
const temporary_id = Math.random();

export function set_config_mode(game_id, new_mode) {
    fetch(make_api_url(game_id, "game_config_mode", {"new_config_mode": new_mode}),
        { method: 'post' })
        .catch(console.log)
}


export function make_api_url(game_tag, endpoint, extra_params) {
    var url;
    if (game_tag === null) {
        url = new URL(`/api/${endpoint}`, document.baseURI)
    } else {
        url = new URL(`/api/${game_tag}/${endpoint}`, document.baseURI)
    }

    const params = {
        temporary_id: temporary_id
    }
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

    if (extra_params) {
        Object.keys(extra_params).forEach(key => url.searchParams.append(key, extra_params[key]))
    }

    return url;
}


export default null;
