import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import './bootstrap.min.css';
import App from './App';
// import jquery from './jquery.min.js'
// import * as serviceWorker from './serviceWorker';
// Note: this JS is also inline in index.html to avoid extra request from flask

ReactDOM.render(<App />, document.querySelector("#root"))

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
// serviceWorker.unregister();
