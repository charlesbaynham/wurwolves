import React, { useState } from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import { motion } from "framer-motion"
import RangeSlider from 'react-bootstrap-range-slider';

import Form from 'react-bootstrap/Form';
import Switch from "react-switch";

import styles from './DistributionSetup.module.css'


const default_roles = {
    JESTER: 10,
    VIGILANTE: 10,
    MAYOR: 10,
    MILLER: 10,
    ACOLYTE: 5,
    PRIEST: 10,
    PROSTITUTE: 10,
    MASON: 7,
    EXORCIST: 10,
    FOOL: 10,
}



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


function SliderAndBox({ value, onChange, max = 5 }) {
    return (
        <Form.Group as={Row}>
            <Col xs="9">
                <RangeSlider
                    className={styles.wideSlider}
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


function DistributionSetup() {
    const [customise, setCustomise] = useState(false);
    const [settings, setSettings] = useState({
        numWolves: null,
        roles: null,
    });

    var role_weights = [];

    for (let role in default_roles) {
        role_weights.push(
            <>
                {role}:
                <SliderAndBox
                    max={100}
                    value={settings.roles === null ? 0 : settings.roles[role]}
                    onChange={(e => {
                        var newRoles = Object.assign({}, settings.roles)
                        newRoles[role] = parseInt(e.target.value)
                        setSettings(Object.assign({}, settings, { roles: newRoles }));
                    }).bind(role)}
                />
            </>
        )
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
                        checked={settings.numWolves !== null}
                        onChange={val => {
                            setSettings(Object.assign({}, settings, { numWolves: val ? 1 : null }));
                        }}
                    />

                    <CollapsingDiv
                        visible={settings.numWolves !== null}
                    >
                        <SliderAndBox
                            max={5}
                            value={settings.numWolves}
                            onChange={e => setSettings(Object.assign({}, settings, { numWolves: e.target.value }))}
                        />
                    </CollapsingDiv>

                    <Toggle
                        text="Select roles"
                        checked={settings.roles !== null}
                        onChange={val => {
                            if (val) {
                                setSettings(Object.assign({}, settings, { roles: default_roles }))
                            } else {
                                setSettings(Object.assign({}, settings, { roles: null }))
                            }
                        }}
                        className="pb-4"
                    />

                    <CollapsingDiv visible={settings.roles !== null}>
                        {role_weights}
                    </CollapsingDiv>
                </Form>
            </CollapsingDiv>
        </div >
    )
}

export default DistributionSetup;
