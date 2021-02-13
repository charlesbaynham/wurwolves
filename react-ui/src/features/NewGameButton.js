import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useHistory } from "react-router-dom";
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';
import { selectGameConfig, selectDefaultConfig } from './selectors'
import { make_api_url, isConfigDefault } from '../utils'


function NewGameButton() {
    const [newGameID, setNewGameID] = useState("")
    const [textBoxContents, setTextBoxContents] = useState("")
    const history = useHistory();

    const gameConfig = useSelector(selectGameConfig);
    const defaultConfig = useSelector(selectDefaultConfig);

    useEffect(() => {
        if (newGameID === "") {
            fetch(make_api_url(null, "get_game"))
                .then(res => res.json())
                .then((data) => {
                    setNewGameID(data)
                })
                .catch(console.log)
        }
    })

    const startGame = () => {
        const new_game_id = textBoxContents ? textBoxContents : newGameID

        if (!isConfigDefault(gameConfig, defaultConfig)) {
            fetch(make_api_url(new_game_id, "game_config", { new_config: JSON.stringify(gameConfig) }),
                { method: 'post' })
                .catch(console.log)
        }

        history.push(`/${new_game_id}`)
    }

    return (
        <Form onSubmit={startGame}>
            <InputGroup size="lg">
                <FormControl
                    placeholder={newGameID}
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
