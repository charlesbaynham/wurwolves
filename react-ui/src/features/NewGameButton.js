import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useHistory } from "react-router-dom";
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';
import { selectUIConfig } from './selectors'
import { make_api_url, isConfigDefault, set_config } from '../utils'


function NewGameButton({ callback = null }) {
    const [suggestedGameID, setSuggestedGameID] = useState(null)
    const [textBoxContents, setTextBoxContents] = useState("")
    const new_game_id = textBoxContents ? textBoxContents : suggestedGameID

    const history = useHistory();
    const gameConfig = useSelector(selectUIConfig);

    useEffect(() => {
        if (suggestedGameID === null) {
            fetch(make_api_url(null, "get_game"))
                .then(res => res.json())
                .then((data) => {
                    setSuggestedGameID(data)
                })
                .catch(console.log)
        }
    })

    // If a callback has been passed in, update its value with the new game ID
    useEffect(() => {
        if (callback !== null) {
            callback(new_game_id);
            console.log(`Calling callback with = ${new_game_id}`)
        }
    }, [new_game_id, callback])

    const startGame = () => {
        set_config(new_game_id, gameConfig)
        history.push(`/${new_game_id}`)
    }

    return (
        <Form onSubmit={startGame}>
            <InputGroup size="lg">
                <FormControl
                    placeholder={new_game_id}
                    aria-label="Game id"
                    aria-describedby="basic-addon2"
                    value={textBoxContents}
                    onChange={e => setTextBoxContents(e.target.value)}
                />
                <InputGroup.Append>
                    <Button onClick={startGame}>
                        {textBoxContents ? "Join" : "Start"}
                    </Button>
                </InputGroup.Append>
            </InputGroup>
        </Form>
    );
}

export default NewGameButton;
