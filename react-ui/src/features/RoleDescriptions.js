import React from 'react';

import {roles} from '../prose'

import Tab from 'react-bootstrap/Tab'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import Nav from 'react-bootstrap/Nav'
import Image from 'react-bootstrap/Image'


function RoleDescriptions() {

    console.log(roles);

    return (
        <Tab.Container defaultActiveKey={roles[0].name}>
            <Row>
                <Col sm={3}>
                <Nav variant="pills" className="flex-column">
                    {
                        roles.map((value, index) => {return (
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
                        roles.map((value, index) => {return (
                            <Tab.Pane eventKey={value.name} key={index}>
                                {value.image ?
                                    <Image src={value.image} alt={value.name} thumbnail className="role-desc-image" />
                                : null}
                                {value.description}
                            </Tab.Pane>
                        )})
                    }
                </Tab.Content>
                </Col>
            </Row>
        </Tab.Container>
    )
}


export default RoleDescriptions;
