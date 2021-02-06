import React, { useEffect, useState } from 'react';

import { motion } from "framer-motion"


import styles from './TemporaryOverlay.module.css'


const time_to_appear = 0.3;
const time_to_disappear = 3;


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function TemporaryOverlay(props) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        async function f() {
            if (props.appear === true) {
                setVisible(true);
                await sleep(1000 * time_to_appear + 100);
                setVisible(false);
            }
        }
        f()
    }, [props.appear])

    const variants = {
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

    return (
        <motion.img
            className={styles.overlay}
            src={props.img}
            initial="hidden"
            animate={visible ? "visible" : "hidden"}
            variants={variants}
        />
    )
}


export default TemporaryOverlay;
