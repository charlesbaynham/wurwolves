import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import { selectMyStatus } from '../selectors'


import TemporaryOverlay from './TemporaryOverlay'

import shot_image from './shot.svg'
import lynched_image from './lynched.svg'
import wolfed_image from './wolfed.svg'
import jester_win from './jester_win.svg'


function AllOverlays() {
    const [previousStatus, setPreviousStatus] = useState(null);
    const myStatus = useSelector(selectMyStatus);

    const [showWolfed, setShowWolfed] = useState(false);
    const [showLynched, setShowLynched] = useState(false);
    const [showShot, setShowShot] = useState(false);

    useEffect(() => {
        setShowWolfed(myStatus === "WOLFED" && previousStatus === "ALIVE")
        setShowLynched(myStatus === "LYNCHED" && previousStatus === "ALIVE")
        setShowShot(myStatus === "SHOT" && previousStatus === "ALIVE")

        setPreviousStatus(myStatus);
    }, [myStatus, previousStatus])

    return (
        <>
            <TemporaryOverlay img={wolfed_image} appear={showWolfed} />
            <TemporaryOverlay img={lynched_image} appear={showLynched} />
            <TemporaryOverlay img={shot_image} appear={showShot} />
            <TemporaryOverlay
                img={jester_win}
                appear={myStatus === "ALIVE"}
                time_to_show={1}
                time_to_show={1}
                time_to_disappear={4}
                custom_variants={{
                    visible: {
                        rotate: [0,0],
                    },
                    hidden: {
                        rotate: 360 * 3,
                        scale: 0,
                    }
                }}
                debug={true}
            />
        </>
    )
}

export default AllOverlays;
