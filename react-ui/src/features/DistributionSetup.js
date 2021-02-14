import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { selectGameConfig, selectDefaultConfig, selectUIConfig, selectStateHash } from './selectors'

import { setGameConfig, setDefaultConfig, setUIConfig } from '../app/store'

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import { motion } from "framer-motion"
import RangeSlider from 'react-bootstrap-range-slider';

import Form from 'react-bootstrap/Form';
import Switch from "react-switch";

import styles from './DistributionSetup.module.css'
import { make_api_url, isConfigDefault, set_config } from '../utils'
import ReactMarkdown from 'react-markdown';

const _ = require('lodash');


function Toggle({ text, checked, onChange, className = null }) {
    var totalClassName = styles.toggle
    if (className !== null) {
        totalClassName = totalClassName + " " + className
    }

    return (
        <div className={totalClassName}>
            <Switch onChange={onChange} checked={checked} />
            <p>{text}</p>
        </div>
    )
}


function SliderAndBox({ value, onChange, min = 0, max = 5 }) {
    return (
        <Form.Group as={Row}>
            <Col xs="9">
                <RangeSlider
                    className={styles.wideSlider}
                    min={min}
                    max={max}
                    style={{ width: "100%" }}
                    value={value ? value : 0}
                    onChange={onChange}
                />
            </Col>
            <Col xs="3">
                <Form.Control
                    value={value ? value : 0}
                    onChange={onChange}
                />
            </Col>
        </Form.Group>
    )
}


function CollapsingDiv({ visible, children }) {
    return (
        <motion.div
            initial="hidden"
            animate={visible ? "visible" : "hidden"}
            variants={{
                hidden: {
                    opacity: 0,
                    scaleY: 0,
                    height: 0,
                    transitionEnd: {
                        display: "none",
                    },
                    transition: {
                        type: "tween"
                    }
                },
                visible: {
                    opacity: 1,
                    scaleY: 1,
                    height: "auto",
                    display: "block",
                    transition: {
                        type: "tween"
                    }
                },
            }}
        >
            {children}
        </motion.div>
    )
}


function DistributionSetup({ game_tag = null, auto_update = false }) {
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

    const gameConfig = useSelector(selectGameConfig);
    const defaultConfig = useSelector(selectDefaultConfig);
    const UIConfig = useSelector(selectUIConfig);

    const stateHash = useSelector(selectStateHash);

    const [customise, setCustomise] = useState(false);
    const [showRoleWeights, setShowRoleWeights] = useState(false);
    const dispatch = useDispatch();

    // Set up the toggles to match the UI state
    const setupToggles = (config) => {
        if (config === null || defaultConfig === null) return;

        if (isConfigDefault(config, defaultConfig)) {
            setCustomise(false)
            setShowRoleWeights(false)
        } else {
            setCustomise(true)
            setShowRoleWeights(!_.isEqual(config.role_weights, defaultConfig.role_weights))
        }
    }

    // Just once, get and store the default config
    useEffect(() => {
        fetch(
            make_api_url(
                null, "default_game_config"
            ),
            { method: 'get' }
        ).then(r => {
            if (!r.ok) {
                throw Error("Fetch default config failed with error " + r.status)
            }
            return r.json()
        }).then(data => {
            if (data) {
                dispatch(setDefaultConfig(data));
            }
        })
    }, [dispatch, game_tag])

    // On first render, and whenever the game hash changes and this component is loaded,
    // get the current gameConfig
    useEffect(() => {
        fetch(
            make_api_url(
                game_tag, "game_config"
            ),
            { method: 'get' }
        ).then(r => {
            if (!r.ok) {
                throw Error("Fetch game config failed with error " + r.status)
            }
            return r.json()
        }).then(config => {
            dispatch(setGameConfig(config));
        })
    }, [dispatch, game_tag, stateHash])

    // If the gameConfig changes, update the UI state and recalculate the toggle states
    // ONLY if the UIConfig and gameConfig were previously equal
    const [previousGameConfig, setPreviousGameConfig] = useState(null);
    useEffect(() => {
        if (_.isEqual(previousGameConfig, UIConfig)) {
            dispatch(setUIConfig(gameConfig))
            setupToggles(gameConfig)
        }
        setPreviousGameConfig(gameConfig)
    }, [gameConfig])

    var role_weights = [];

    if (UIConfig && UIConfig.role_weights) {
        for (let role in UIConfig.role_weights) {
            role_weights.push(
                <>
                    {role}:
                    <SliderAndBox
                        key={role}
                        max={100}
                        value={UIConfig.role_weights === null ? 0 : UIConfig.role_weights[role]}
                        onChange={e => {
                            var newRoles = Object.assign({}, UIConfig.role_weights)
                            newRoles[role] = parseInt(e.target.value)
                            const newUIConfig = Object.assign({}, UIConfig, { role_weights: newRoles })

                            dispatch(setUIConfig(newUIConfig))
                        }}
                    />
                </>
            )
        }
    }

    return (
        <div
            className={styles.container}
        >
            <Form
                className={styles.form}
                onSubmit={e => e.preventDefault()}
                onBlur={() => {
                    if (auto_update === true && game_tag !== null) {
                        if (customise) {
                            set_config(game_tag, UIConfig)
                        } else {
                            set_config(game_tag, null)
                        }
                    }
                }}
            >
                <Toggle
                    text="Customize role distribution"
                    checked={customise}
                    onChange={setCustomise}
                />
                <CollapsingDiv visible={customise}>
                    <div
                        className={styles.form}
                    >
                        <Toggle
                            text="Select number of wolves"
                            checked={UIConfig ? UIConfig.number_of_wolves !== null : false}
                            onChange={val => {
                                dispatch(setUIConfig(Object.assign({}, UIConfig, { number_of_wolves: val ? 1 : null })));
                            }}
                        />

                        <CollapsingDiv
                            visible={UIConfig ? UIConfig.number_of_wolves !== null : null}
                        >
                            <SliderAndBox
                                max={5}
                                min={1}
                                value={UIConfig ? UIConfig.number_of_wolves : null}
                                onChange={e => dispatch(setUIConfig(Object.assign({}, UIConfig, { number_of_wolves: parseInt(e.target.value) })))}
                            />
                        </CollapsingDiv>

                        <Toggle
                            text="Select roles"
                            checked={showRoleWeights}
                            onChange={setShowRoleWeights}
                            className="pb-4"
                        />

                        <ReactMarkdown>
                            Adjust the weightings for respective roles below. All roles will be assigned at most once.
                        </ReactMarkdown>

                        <CollapsingDiv visible={showRoleWeights}>
                            {role_weights}
                        </CollapsingDiv>
                    </div>
                </CollapsingDiv>
            </Form>
        </div >
    )
}

export default DistributionSetup;
