import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { selectGameConfig, selectDefaultConfig } from './selectors'

import { setGameConfig, setDefaultConfig } from '../app/store'

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import { motion } from "framer-motion"
import RangeSlider from 'react-bootstrap-range-slider';

import Form from 'react-bootstrap/Form';
import Switch from "react-switch";

import styles from './DistributionSetup.module.css'
import { make_api_url } from '../utils'


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


function DistributionSetup({ game_tag }) {
    const gameConfig = useSelector(selectGameConfig);
    const defaultConfig = useSelector(selectDefaultConfig);

    const [customise, setCustomise] = useState(false);
    const [showRoleWeights, setShowRoleWeights] = useState(false);
    const dispatch = useDispatch();

    useEffect(() => {
        // Get and store the default config
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
    useEffect(() => {
        if (game_tag !== null) {
            // If in a game, get the current config too
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
            }).then(data => {
                if (data) {
                    dispatch(setGameConfig(data));
                }
            })
        } else {
            // Otherwise, use the default
            dispatch(setGameConfig(defaultConfig));
        }
    }, [dispatch, defaultConfig, game_tag])

    var role_weights = [];

    if (gameConfig && gameConfig.role_weights) {
        for (let role in gameConfig.role_weights) {
            role_weights.push(
                <>
                    {role}:
                    <SliderAndBox
                        key={role}
                        max={100}
                        value={gameConfig.role_weights === null ? 0 : gameConfig.role_weights[role]}
                        onChange={e => {
                            var newRoles = Object.assign({}, gameConfig.role_weights)
                            newRoles[role] = parseInt(e.target.value)
                            const newConfig = Object.assign({}, gameConfig, { role_weights: newRoles })

                            console.log(newRoles)
                            console.log(newConfig)
                            dispatch(setGameConfig(newConfig))
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
            <Form className={styles.form} onSubmit={e => e.preventDefault()}>
                <Toggle
                    text="Customize role distribution"
                    checked={customise}
                    onChange={setCustomise}
                />
            </Form>

            <CollapsingDiv visible={customise}>
                <Form className={styles.form} onSubmit={e => e.preventDefault()}>
                    <Toggle
                        text="Select number of wolves"
                        checked={gameConfig.number_of_wolves !== null}
                        onChange={val => {
                            dispatch(setGameConfig(Object.assign({}, gameConfig, { number_of_wolves: val ? 1 : null })));
                        }}
                    />

                    <CollapsingDiv
                        visible={gameConfig.number_of_wolves !== null}
                    >
                        <SliderAndBox
                            max={5}
                            min={1}
                            value={gameConfig.number_of_wolves}
                            onChange={e => dispatch(setGameConfig(Object.assign({}, gameConfig, { number_of_wolves: parseInt(e.target.value) })))}
                        />
                    </CollapsingDiv>

                    <Toggle
                        text="Select roles"
                        checked={showRoleWeights}
                        onChange={setShowRoleWeights}
                        className="pb-4"
                    />

                    <CollapsingDiv visible={showRoleWeights}>
                        {role_weights}
                    </CollapsingDiv>
                </Form>
            </CollapsingDiv>
        </div >
    )
}

export default DistributionSetup;
