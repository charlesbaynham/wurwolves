import React from 'react';

import Tab from 'react-bootstrap/Tab'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import Nav from 'react-bootstrap/Nav'
import Image from 'react-bootstrap/Image'
import ReactMarkdown from 'react-markdown';


function RoleDescriptions(props) {
    return (
        <Tab.Container id="roles-display" defaultActiveKey={props.roles[0].name}>
            <Row>
                <Col sm={3}>
                <Nav variant="pills" className="flex-column">
                    {
                        props.roles.map((value, index) => {return (
                            <Nav.Item key={index}>
                                <Nav.Link eventKey={value.name}>{value.name}</Nav.Link>
                            </Nav.Item>
                        )})
                    }
                </Nav>
                </Col>
                <Col sm={9}>
                <Tab.Content>
                    {
                        props.roles.map((value, index) => {return (
                            <Tab.Pane eventKey={value.name} key={index}>
                                {value.image ?
                                    <Image src={value.image} alt={value.name} thumbnail className="role-desc-image" />
                                : null}
                                <ReactMarkdown source={value.description}/>
                            </Tab.Pane>
                        )})
                    }
                </Tab.Content>
                </Col>
            </Row>
        </Tab.Container>
    )
}

// function RoleDescriptions() {

//     return (
//         <Tab.Container id="roles-types" defaultActiveKey="guaranteed">
//             <Nav className="flex-row">
//                 <Nav.Item>
//                     <Nav.Link eventKey="guaranteed">Guaranteed</Nav.Link>
//                     <Nav.Link eventKey="random">Random</Nav.Link>
//                 </Nav.Item>
//             </Nav>

//             <Tab.Content>
//             <Tab.Pane eventKey="guaranteed">
//                 <RolesDisplay roles={guaranteed_roles} />
//             </Tab.Pane>
//             <Tab.Pane eventKey="random">
//                 <RolesDisplay roles={random_roles} />
//             </Tab.Pane>
//             </Tab.Content>
//         </Tab.Container>
//     )
// }


export default RoleDescriptions;
