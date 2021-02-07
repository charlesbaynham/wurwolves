import React, { useState } from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import { motion } from "framer-motion"
import RangeSlider from 'react-bootstrap-range-slider';

import Form from 'react-bootstrap/Form';
import Switch from "react-switch";

import styles from './DistributionSetup.module.css'


function Toggle({ text, checked, onChange }) {
    return (
        <div className={styles.toggle}>
            <Switch onChange={onChange} checked={checked} />
            <p>{text}</p>
        </div>
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


function DistributionSetup() {
    const [customise, setCustomise] = useState(false);
    const [settings, setSettings] = useState({
        numWolves: null,
        roles: null,
    });

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
                        checked={settings.numWolves !== null}
                        onChange={val => {
                            setSettings(Object.assign({}, settings, { numWolves: val ? 1 : null }));
                        }}
                    />

                    <CollapsingDiv
                        visible={settings.numWolves !== null}
                    >
                        <Form.Group as={Row}>
                            <Col xs="9">
                                <RangeSlider
                                    className={styles.wideSlider}
                                    max={5}
                                    style={{ width: "100%" }}
                                    value={settings.numWolves}
                                    onChange={e => setSettings(Object.assign({}, settings, { numWolves: e.target.value }))}
                                />
                            </Col>
                            <Col xs="3">
                                <Form.Control
                                    value={settings.numWolves}
                                    onChange={e => setSettings(Object.assign({}, settings, { numWolves: e.target.value }))}
                                />
                            </Col>
                        </Form.Group>
                    </CollapsingDiv>

                    <Toggle
                        text="Select roles"
                        checked={settings.roles !== null}
                        onChange={val => {
                            if (val) {
                                setSettings(Object.assign({}, settings, { roles: 1 }))
                            } else {
                                setSettings(Object.assign({}, settings, { roles: null }))
                            }
                        }}
                    />
                </Form>
            </CollapsingDiv>
        </div >
    )
}

export default DistributionSetup;
