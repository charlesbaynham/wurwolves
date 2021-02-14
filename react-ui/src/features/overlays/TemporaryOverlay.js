import React, { useEffect, useState } from 'react';

import { motion } from "framer-motion"

import styles from './TemporaryOverlay.module.css'

const _ = require('lodash');


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function TemporaryOverlay({
    appear,
    img,
    time_to_appear = 0.5,
    time_to_disappear = 3,
    time_to_show = 0.1,
    custom_variants = {},
    debug = false
}) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        async function f() {
            if (appear === true) {
                setVisible(true);
                await sleep(1000 * (time_to_appear + time_to_show));
                setVisible(false);
            }
        }
        f()
    }, [appear, time_to_appear, time_to_show])

    const default_variants = {
        hidden: {
            opacity: 0,
            scale: 1,
            transitionEnd: {
                display: "none",
                scale: 0,
                opacity: 0,
            },
            transition: { duration: time_to_disappear }
        },
        visible: {
            opacity: [0, 1],
            scale: 1,
            display: "block",
            transition: {
                duration: time_to_appear,
                type: "spring"
            }
        },
    }

    // Merge in any custom variant changes passed by the user
    const variants = _.merge({}, default_variants, custom_variants);

    if (debug) {
        console.debug("variants:")
        console.debug(variants)
    }

    return (
        <motion.img
            className={styles.overlay}
            src={img}
            initial="hidden"
            animate={visible ? "visible" : "hidden"}
            variants={variants}
        />
    )
}


export default TemporaryOverlay;
