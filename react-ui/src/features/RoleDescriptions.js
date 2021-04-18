import React from 'react';

import Badge from 'react-bootstrap/Badge'
import Tab from 'react-bootstrap/Tab'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import Nav from 'react-bootstrap/Nav'
import Image from 'react-bootstrap/Image'

import ReactMarkdown from 'react-markdown';


function RoleDescriptions(props) {

    const badges = {
        0: <Badge variant="success">Beginner</Badge>,
        1: <Badge variant="primary">Fledgling</Badge>,
        2: <Badge variant="danger">Expert</Badge>
    }

    return (
        <Tab.Container id="roles-display" defaultActiveKey={props.roles[0].name}>
            <Row>
                <Col sm={3}>
                <Nav variant="pills" className="flex-column">
                    {
                        props.roles.map((value, index) => {return (
                            <Nav.Item key={index}>
                                <Nav.Link eventKey={value.name}>
                                    {value.name}
                                </Nav.Link>
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
                                { badges[value.level] }
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


export default RoleDescriptions;
