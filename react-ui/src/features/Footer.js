import React from 'react';

function Footer() {
    return (
        <div className="text-muted text-nowrap footer d-flex flex-row px-5 bg-light bg-night-black">
            <a id="buymeabeer" href="https://www.buymeacoffee.com/wurwolves">
                Buy me a beer
                <span role="img" aria-label="beer">🍺</span>
            </a>
            <span className="flex-grow-1"></span>
            <div id="bike" className="d-flex flex-column justify-content-center"><img src="images/bike.png" alt="Baynham design motorbike logo" /></div>
            <p>Baynham Design</p>
        </div >
    )
}

export default Footer;
