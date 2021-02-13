import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import { selectMyStatus, selectAllPlayers } from '../selectors'

import TemporaryOverlay from './TemporaryOverlay'

import shot_image from './shot.svg'
import lynched_image from './lynched.svg'
import wolfed_image from './wolfed.svg'
import jester_win from './jester_win.svg'


function AllOverlays() {
    const [previousStatus, setPreviousStatus] = useState(null);
    const myStatus = useSelector(selectMyStatus);
    const allPlayers = useSelector(selectAllPlayers);

    const [previousJesterWon, setPreviousJesterWon] = useState(false);

    const [showWolfed, setShowWolfed] = useState(false);
    const [showLynched, setShowLynched] = useState(false);
    const [showShot, setShowShot] = useState(false);
    const [showJester, setShowJester] = useState(false);

    useEffect(() => {
        setShowWolfed(myStatus === "WOLFED" && previousStatus === "ALIVE")
        setShowLynched(myStatus === "LYNCHED" && previousStatus === "ALIVE")
        setShowShot(myStatus === "SHOT" && previousStatus === "ALIVE")

        setPreviousStatus(myStatus);
    }, [myStatus, previousStatus])

    // Check for a jester win
    const didJesterWin = (players) => {
        for (const player of players) {
            if (player.status === "LYNCHED" && player.role === "Jester") {
                return true;
            }
        }
        return false;
    }

    useEffect(() => {
        const won = didJesterWin(allPlayers);
        setShowJester(won && !previousJesterWon);
        setPreviousJesterWon(previousJesterWon);
    }, [allPlayers, previousJesterWon])

    return (
        <>
            <TemporaryOverlay img={wolfed_image} appear={showWolfed} />
            <TemporaryOverlay img={lynched_image} appear={showLynched} />
            <TemporaryOverlay img={shot_image} appear={showShot} />
            <TemporaryOverlay
                img={jester_win}
                appear={showJester}
                time_to_show={1}
                time_to_disappear={4}
                custom_variants={{
                    visible: {
                        rotate: [0, 0],
                    },
                    hidden: {
                        rotate: 360 * 3,
                        scale: 0,
                    }
                }}
            />
        </>
    )
}

export default AllOverlays;
