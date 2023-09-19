import React, { Component } from 'react';
import './App.css';
import OpenSheetMusicDisplay from './lib/OpenSheetMusicDisplay'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      file: null,
      musicxml: null,
      showModal: false,
      inputStrings: ['', ''],
      boolValues: Array(7).fill(false),
      apiUrl: window.location.href
    };
    this.fileInput = React.createRef();
    this.handleChange = this.handleChange.bind(this);
  }
  
  handleSubmitApiUrl(event) {
    event.preventDefault();
 }

  handleChange(event) {
      this.setState({apiUrl: event.target.value});
  }  
  
  handleSubmit(event) {
    event.preventDefault();
    const file = this.fileInput.current.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      this.setState({
        file: file,
        musicxml: reader.result,
      });
    };
    reader.readAsText(file);
  }

  async handleNumberMeasures() {
    if (!this.state.musicxml) {
      alert("No file uploaded yet.");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", this.state.file);
  
    try {
      const response = await fetch(`${this.state.apiUrl}/number`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const updatedMusicxml = await response.text();
      this.setState({
        musicxml: updatedMusicxml,
      });
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  }

  async randomMeasures() {  
    try {
      console.log(`${this.state.apiUrl}/random`)
      const response = await fetch(`${this.state.apiUrl}/random`, {
        method: "GET",
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const updatedMusicxml = await response.text();
      this.setState({
        musicxml: updatedMusicxml,
      });
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  }

  async handleConvert() {
    const file = this.fileInput.current.files[0];
    if (!file) {
      alert("Please select a file before submitting");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch(`${this.state.apiUrl}/convert`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
  
      const updatedMusicxml = await response.text();
      
      this.setState({
        musicxml: updatedMusicxml,
      });
      
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  }

  showDialog = () => {
    this.setState({ showDialog: true });
  }
  hideDialog = () => {
    this.setState({ showDialog: false });
  }
  handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.startsWith('string')) {
      const index = parseInt(name.replace('string', ''), 10) - 1;
      const updatedStrings = [...this.state.inputStrings];
      updatedStrings[index] = value;
      this.setState({ inputStrings: updatedStrings });
    } else if (name.startsWith('bool')) {
      const index = parseInt(name.replace('bool', ''), 10) - 1;
      const updatedBools = [...this.state.boolValues];
      updatedBools[index] = checked;
      this.setState({ boolValues: updatedBools });
    }
  }
  
  handleGenerate = async (event) => {
    event.preventDefault();
    const { inputStrings, boolValues } = this.state;
    const boolMapping = {
      'content-lead': String(boolValues[0]),
      'content-bass': String(boolValues[1]),
      'content-drums': String(boolValues[2]),
      'content-guitar': String(boolValues[3]),
      'content-piano': String(boolValues[4]),
      'content-strings': String(boolValues[5])
    };
    const stringMapping = {
      'time_signature': inputStrings[0],
      'number_measures': inputStrings[1]
    };
    const dataToSend = { ...boolMapping, ...stringMapping };
    const formData = new FormData();
    for (const key in dataToSend) {
      formData.append(key, dataToSend[key]);
    }
    try {
      const response = await fetch(`${this.state.apiUrl}/generate`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const updatedMusicxml = await response.text();
      this.setState({
        musicxml: updatedMusicxml,
      });
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
      this.hideDialog();
  }
    
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h2 className="App-title">Tune Ease</h2>
        </header>
        <form onSubmit={this.handleSubmitApiUrl.bind(this)}>
          Api base url: 
          <input 
              type="text" 
              value={this.state.apiUrl}
              onChange={this.handleChange} 
          />
        </form>
        <form onSubmit={this.handleSubmit.bind(this)} >
          <label>
            Upload file:
            <input type="file" ref={this.fileInput} accept=".xml,.mid,.midi,.mscz,.mxl,.musicxml" />
          </label>
          <button type="submit">Submit</button>
          <button type="button" onClick={this.handleConvert.bind(this)}>Convert</button>
          <button type="button" onClick={this.randomMeasures.bind(this)}>Random</button>
        </form>
        <form >
          <button type="button" onClick={this.handleNumberMeasures.bind(this)}>Number Measures</button>
        </form>
        <form >
          <button type="button" onClick={this.showDialog}>Generate</button>
          {
          this.state.showDialog && (
            <div className="dialog-overlay">
              <div className="dialog">
                <h2>Generate Dialog</h2>
                <input name="string1" value={this.state.inputStrings[0]} onChange={this.handleInputChange} placeholder="The time signature for the file to be generated." />
                <input name="string2" value={this.state.inputStrings[1]} onChange={this.handleInputChange} placeholder="The number of beats for the file to be generated" />
                <label>
                  Generate a lead track
                  <input type="checkbox" name="bool1" checked={this.state.boolValues[0]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a bass track
                  <input type="checkbox" name="bool2" checked={this.state.boolValues[1]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a drums track
                  <input type="checkbox" name="bool3" checked={this.state.boolValues[2]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a guitar track
                  <input type="checkbox" name="bool4" checked={this.state.boolValues[3]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate piano track
                  <input type="checkbox" name="bool5" checked={this.state.boolValues[4]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a strings track
                  <input type="checkbox" name="bool6" checked={this.state.boolValues[5]} onChange={this.handleInputChange} />
                </label>
                <button onClick={this.handleGenerate}>Generate</button>
                <button onClick={this.hideDialog}>Close</button>
              </div>
            </div>
          )
        }
        <button type="button" onClick={this.showDialog}>Suggestions</button>
          {
          this.state.showDialog && (
            <div className="dialog-overlay">
              <div className="dialog">
                <h2>Generate Dialog</h2>
                
                <input name="string1" value={this.state.inputStrings[0]} onChange={this.handleInputChange} placeholder="The time signature for the file to be generated." />
                <input name="string2" value={this.state.inputStrings[1]} onChange={this.handleInputChange} placeholder="The number of beats for the file to be generated" />
                <label>
                  Generate a lead track
                  <input type="checkbox" name="bool1" checked={this.state.boolValues[0]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a bass track
                  <input type="checkbox" name="bool2" checked={this.state.boolValues[1]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a drums track
                  <input type="checkbox" name="bool3" checked={this.state.boolValues[2]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a guitar track
                  <input type="checkbox" name="bool4" checked={this.state.boolValues[3]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate piano track
                  <input type="checkbox" name="bool5" checked={this.state.boolValues[4]} onChange={this.handleInputChange} />
                </label>
                <label>
                  Generate a strings track
                  <input type="checkbox" name="bool6" checked={this.state.boolValues[5]} onChange={this.handleInputChange} />
                </label>
                <button onClick={this.handleGenerate}>Generate</button>
                <button onClick={this.hideDialog}>Close</button>
              </div>
            </div>
          )
        }
        </form>

        {
          this.state.musicxml && (
            <OpenSheetMusicDisplay file={this.state.musicxml} />
          )
        }
      </div>
    );
  }
}

export default App;