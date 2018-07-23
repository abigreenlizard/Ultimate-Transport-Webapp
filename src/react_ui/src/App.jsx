import React, { Component } from "react"
import { Grid, Row, Col, Container } from "react-bootstrap"
import  OpenWeatherMap  from "react-weather"
import  ReactWeather  from "react-open-weather"
import TimePicker from "react-bootstrap-time-picker"
import "./App.css"
import MapContainer from "./components/MapContainer"
import ContentBlock from "./components/ContentBlock"


// import DropdownInput from 'react-dropdown-input';
// import Select from 'react-select';


require("bootstrap/dist/css/bootstrap.css")
require("react-select/dist/react-select.css")

class App extends Component {
  constructor(props){
    super(props)

    this.state = {
      stopsInRoute: [],
      selectedJourney: [],
    }
  }

  // this is only to be used when a new route is chosen (ie. by RouteSelect)
  // Changes to the selected journey and markers within a given route should be
  // handled with onSelectedJourneyUpdate
  onRouteUpdate(data) {
    this.setState({
      stopsInRoute: data,
      selectedJourney: data,
    })
  }

  onSelectedJourneyUpdate(data) {
    this.setState({
      selectedJourney: data
    })
    console.log(data)
  }

  // componentDidUpdate(prevState) {
  //   if (prevState.selectedJourney === []) {
  //     const stops = this.state.stopsInRoute
  //     this.setState({
  //       selectedJourney: stops
  //     })
  //   }
  // }

  render() {
    // var StatesField = require('./components/StatesField').StatesField;
    // const myMarker = [{'stop_id': 1089, 'stop_lat': 53.3518, 'stop_lon': -6.2814}]
    // const searchNames = ['Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart'];
    return (
      <Grid fluid={true}><Row><Col xs={4} md={4}>
              <ContentBlock data={this.state.testState} onRouteUpdate={this.onRouteUpdate.bind(this)}
                onSelectedJourneyUpdate={this.onSelectedJourneyUpdate.bind(this)}/></Col>
            <Col xs={12} md={8}>
              <MapContainer selectedStops={ this.state.selectedJourney}/>
            </Col></Row>
      </Grid>

    )
  }
}

export default App