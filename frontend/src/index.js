import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './components/App/App';

function Main() {
  return(
    <>
      <App />
    </>
  )
}

ReactDOM.render(
  <Main />,
  document.getElementById('root')
);

