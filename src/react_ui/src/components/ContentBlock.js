import { Grid, Row, Col, Container } from 'react-bootstrap';
import React, { Component } from "react"
import RouteSelect from "./RouteSelect"
import StopSelect from "./StopSelect"
import CalendarButton from "./CalendarButton"
import TimeDropdown from "./TimeDropdown"
import { Button } from "react-bootstrap"
import {PageHeader} from 'react-bootstrap';
import dublin_bus_icon from './dublin_bus_icon.png';
import WeatherWidget from "./Weather";
import PredictionContainer from './PredictionContainer';

class ContentBlock extends Component {
  constructor(props) {
    super(props)

    this.state = {
      stops: [],
      chosenRoute: "",
      startStop: "",
      finishStop: "",
      predictionForJourney: null,
    }

  }

  //Save the list of stops to contentBlock's state before
  //Calling App.js setState function
  routeUpdate (route) {
    this.setState({
      stops: route
    })
    this.props.onRouteUpdate(route)
    // console.log(this.state.route)
  }

  async onChosenRouteUpdate(route) {
    this.setState({
      chosenRoute: route,
      predictionForJourney: null,
    })
  }

  async onStartStopUpdate(stop) {
    this.setState({
      startStop: stop,
      predictionForJourney: null,
    })
  }

  async onFinishStopUpdate(stop) {
    this.setState({
      finishStop: stop,
      predictionForJourney: null,
    })
  }

  // onSelectedJourneyUpdate(journey){
  //   this.setState({
  //     selectedJourney: {
  //       route: this.state.chosenRoute,
  //       start: this.state.startStop,
  //       finish: this.state.finishStop,
  //     }
  //   })
  // }

  handleClick = () => {

    // const numOfStops = this.calculateNumberOfStops()
    this.getPrediction()
    // this.setState({
    //   predictionForJourney: prediction
    // })
  }

  getPrediction = () => {
    const endpoint = '/api/getPredictionForJourney' 
    try {
      // const result = fetch(endpoint, {
      fetch(endpoint, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body : JSON.stringify({
          route: this.state.chosenRoute,
          start: this.state.startStop,
          start: this.state.startStop,
        })
      })
        .then((response) => response.json())
        .then((resp) => {
          const prediction = resp.prediction
          this.setState({
            predictionForJourney: prediction
          })
        })
        // .then((resp) => console.log(resp.prediction))
    } catch(e) {
        console.log(e)
      }
  }

  render(){

    return (
      <div>
		<PageHeader className='fontForTitle'> Ultimate Transport </PageHeader>
		{/*<img src={dublin_bus_icon} alt="dublin_bus_icon" />;*/}
	     <RouteSelect className="mb-3" onRouteUpdate={this.routeUpdate.bind(this)}
                      onChosenRouteUpdate={this.onChosenRouteUpdate.bind(this)}/>
	     <div style={{marginTop: '2em'}}> </div>
	     <StopSelect stops={this.state.stops}
                    onStartStopUpdate={this.onStartStopUpdate.bind(this)}
                    onFinishStopUpdate={this.onFinishStopUpdate.bind(this)}/>
	     <div style={{marginTop: '2em'}}> </div>
        
        <Grid>
          <Row>
            <Col>
           <TimeDropdown />
              </Col>
            <Col>
           <CalendarButton />
            </Col>
              </Row>
          </Grid>
        <div style={{marginTop: '1em'}}></div>
        
        <Button onClick={this.handleClick} bsStyle='primary' bsSize='large' block>Go!</Button>
        <PredictionContainer prediction={this.state.predictionForJourney} />
        <WeatherWidget />
	</div>
    )
  }
}

export default ContentBlock
