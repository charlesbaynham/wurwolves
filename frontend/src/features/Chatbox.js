import React from 'react';


export function Chatbox() {
    return (
        <div class="col-md-5">
            <div class="card card-body d-flex flex-column chat-holder bg-night-black">
                <h5 class="card-title">Events / secret chat</h5>
                <div id="chat-box" class="flex-grow-1">
                    <p>4 votes for Gaby (Charles, James, Parav, Harry)</p>
                    <p>3 votes for Euan (Rosie, Rachel, Gaby)</p>
                    <p><strong>Gaby was voted off</strong></p>
                    <p><strong>Sophie was killed in the night</strong></p>
                    <p>Rob was nominated by Charles</p>
                    <p>James was nominated by Charles</p>
                    <p>James was seconded by Parav</p>
                    <p>4 votes for Gaby (Charles, James, Parav, Harry)</p>
                    <p>3 votes for Euan (Rosie, Rachel, Gaby)</p>
                    <p><strong>Gaby was voted off</strong></p>
                    <p><strong>Sophie was killed in the night</strong></p>
                    <p>Rob was nominated by Charles</p>
                    <p>James was nominated by Charles</p>
                    <p>James was seconded by Parav</p>
                    <p>4 votes for Gaby (Charles, James, Parav, Harry)</p>
                    <p>3 votes for Euan (Rosie, Rachel, Gaby)</p>
                    <p><strong>Gaby was voted off</strong></p>
                    <p><strong>Sophie was killed in the night</strong></p>
                    <p>Rob was nominated by Charles</p>
                    <p>James was nominated by Charles</p>
                    <p>James was seconded by Parav</p>
                </div>
                <div class="mt-3">
                    <input type="text" class="form-control" id="chatInput"
                        placeholder="Secret message to the wolves" />
                </div>
            </div>
        </div>
    )
}

export default Chatbox;