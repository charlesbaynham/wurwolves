import React, { useState, useEffect } from 'react';
import { useHistory } from "react-router-dom";
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';


function NewGameButton() {

    const [newGameID, setNewGameID] = useState("")
    const [textBoxContents, setTextBoxContents] = useState("")
    const history = useHistory();

    useEffect(() => {
        if (newGameID === "") {
            fetch('/api/get_game')
                .then(res => res.json())
                .then((data) => {
                    setNewGameID(data)
                })
                .catch(console.log)
        }
    })

    const navToGame = () => {
        if (textBoxContents) {
            history.push(`/${textBoxContents}`)
        } else {
            history.push(`/${newGameID}`)
        }
    }

    return (
        <Form onSubmit={navToGame}>
            <InputGroup size="lg">
                <FormControl
                    placeholder={newGameID}
                    aria-label="Game id"
                    aria-describedby="basic-addon2"
                    value={textBoxContents}
                    onChange={e => setTextBoxContents(e.target.value)}
                />
                <InputGroup.Append>
                    <Button onClick={navToGame}>
                        {textBoxContents ? "Join" : "Start"}
                    </Button>
                </InputGroup.Append>
            </InputGroup>
        </Form>
    );
}

export default NewGameButton;
