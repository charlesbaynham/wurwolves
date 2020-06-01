import React from 'react';

function Controls() {
    return (
        <div className="row pt-4 pt-md-0 d-flex  flex-row-reverse align-items-center">
            <div className="col-md">
                <button type="button" className="btn btn-secondary btn-block btn-lg"><em>Select someone to
                          lynch...</em></button>
            </div>
            <div className="col-md pt-4 pt-md-0">
                <h5>You are a Seer</h5>
                <p>You win the game if the villagers lynch all the wolves. During the night, you may check the identity
                      of one person and discover if they are a wolf. </p>
            </div>
        </div>
    )
}

export default Controls;
