import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import { selectMyStatus } from '../selectors'


import TemporaryOverlay from './TemporaryOverlay'

import clawed_image from './clawmarks.svg'


function AllOverlays() {
    const [previousStatus, setPreviousStatus] = useState(null);

    const myStatus = useSelector(selectMyStatus);

    const [showClaws, setShowClaws] = useState(false);

    useEffect(() => {
        setShowClaws(myStatus === "WOLFED" && previousStatus === "ALIVE")

        setPreviousStatus(myStatus);
    }, [myStatus, previousStatus])

    return (
        <TemporaryOverlay img={clawed_image} appear={showClaws} />
    )
}

export default AllOverlays;
