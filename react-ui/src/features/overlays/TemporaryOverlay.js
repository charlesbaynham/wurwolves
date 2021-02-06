import React, { useEffect, useState } from 'react';

import { motion } from "framer-motion"


import styles from './TemporaryOverlay.module.css'


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function TemporaryOverlay(props) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        async function f() {
            if (props.appear === true) {
                setVisible(true);
                await sleep(500);
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
                display: "none"
            },
            transition: { duration: 4 }
        },
        visible: {
            opacity: [0, 1],
            scale: [0, 1],
            display: "block",
            transition: { duration: 0.3 }
        },
    }

    return (
        <motion.img
            className={styles.overlay}
            src={props.img}
            initial="hidden"
            animate={visible ? "visible" : "hidden"}
            variants={variants}
            transition={{
                visible: { duration: 0.3 },
                hidden: { duration: 1 }
            }}
        />
    )
}


export default TemporaryOverlay;
