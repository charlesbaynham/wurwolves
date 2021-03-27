import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { selectGameConfigMode, selectStateHash } from './selectors'

import { setGameConfigMode } from '../app/store'

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Card from 'react-bootstrap/Card';


import Form from 'react-bootstrap/Form';

import styles from './DistributionSetup.module.css'
import { make_api_url, set_config_mode } from '../utils'

import villagerImage from './characters/villager.svg'
import jesterImage from './characters/jester.svg'
import seerImage from './characters/seer.svg'


function ModeSelector({selected, setSelected, no_padding = false}) {

    const RoleCard = ({title, description, img, active=false, onClick=null}) => (
        <Col xs={6} s={4} md={no_padding ? 4 : 3}>
            <button className={styles.debuttonedButton} onClick={onClick}>
            <Card className={active ? styles.difficulty_box + " " + styles.difficulty_box_active : styles.difficulty_box}>
                <Card.Img variant="top" src={img} style={{height: "3cm"}} />
                <Card.Body>
                    <Card.Title>{title}</Card.Title>
                    <Card.Text>
                        {description}
                    </Card.Text>
                </Card.Body>
            </Card>
            </button>
        </Col>
    )

    return (
    <Row className="justify-content-center">
        <RoleCard
            title="Beginner"
            description="Just the basics"
            img={villagerImage}
            active={selected === "easy"}
            onClick={(e) => {
                setSelected("easy");
                e.preventDefault();
            }}
        />
        <RoleCard
            title="Fledgling"
            description="Four extra roles"
            img={jesterImage}
            active={selected === "medium"}
            onClick={(e) => {
                setSelected("medium");
                e.preventDefault();
            }}
        />
        <RoleCard
            title="Expert"
            description="All the roles!"
            img={seerImage}
            active={selected === "hard"}
            onClick={(e) => {
                setSelected("hard");
                e.preventDefault();
            }}
        />
    </Row>
)
}


function DistributionSetup({ game_tag = null, auto_update = false, no_padding = false }) {
    // The redux store maintains three config objects:
    // * gameConfig:    The current config of the game, as stored in the database
    // * UIConfig:      The UI state as drawn locally. Might difer from
    //                  gameConfig while settings are being changed
    // * defaultConfig: The default config. Static.
    //
    // Also, this object keeps track of which toggles are selected. Initially these are set
    // according to whether a) the state is marked as customized by the backend (in the frontent parser)
    // and b) if so, which bits (if any) have been customised.
    //
    // To allow the user to change the settings, the UI state can be altered. If this happens, the frontend
    // sends an API request to alter the backend state to match. gameConfig updates are copied
    // to UIConfig only if before the update UIConfig == gameConfig. This updates the state displayed to the
    // user, but doesn't interrupt them if they're busy configuring it already. Such updates trigger a
    // recalculation of the slider states too.

    const gameConfigMode = useSelector(selectGameConfigMode);
    const stateHash = useSelector(selectStateHash);
    const dispatch = useDispatch();

    console.log(`gameConfigMode = ${gameConfigMode}`)

    // On first render, and whenever the game hash changes and this component is loaded,
    // get the current gameConfigMode.
    useEffect(() => {
        if (game_tag !== null) {
            console.debug(`getting game_config_mode with tag ${game_tag}`)
            fetch(
                make_api_url(
                    game_tag, "game_config_mode"
                ),
                { method: 'get' }
            ).then(r => {
                if (!r.ok) {
                    throw Error("Fetch game config failed with error " + r.status)
                }
                return r.json()
            }).then(game_mode => {
                console.debug(`Retrieved game mode: ${game_mode}`)
                if (game_mode === null) {
                    throw Error('No game mode returned');
                }
                dispatch(setGameConfigMode(game_mode));
            })
        }
    }, [dispatch, game_tag, stateHash])

    // If the game config mode changes, send a request to change it on the server
    const changeMode = (newMode) => {
        dispatch(setGameConfigMode(newMode))
        if (auto_update === true && game_tag !== null) {
            console.debug("triggerUpdate: sending request to change config mode to")
            console.debug(newMode)
            set_config_mode(game_tag, newMode)
        }
    }

    return (
        <div
            className={styles.container}
        >
            <Form
                className={styles.form}
                onSubmit={e => e.preventDefault()}
            >
                <ModeSelector
                    selected={gameConfigMode}
                    setSelected={(v) => changeMode(v)}
                    no_padding={no_padding}
                />
            </Form>
        </div >
    )
}

export default DistributionSetup;
