import React from 'react';
import ReactDOM from 'react-dom';
import { render } from '@testing-library/react';
import { shallow, configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import App from './App';
import './App.css';

/*
configure({ adapter: new Adapter() });

// Todo test upload 
describe('App', () => {
  it('fetches data from server with expected parameters', done => {
    const mockSuccessResponse = {};
    const mockJsonPromise = Promise.resolve(mockSuccessResponse);
    const mockFetchPromise = Promise.resolve({
      json: () => mockJsonPromise,
    });
    jest.spyOn(global, 'fetch').mockImplementation(() => mockFetchPromise);

    const wrapper = shallow(<App />);
    // the app should call the api once on load
    expect(global.fetch).toHaveBeenCalledTimes(1);

    expect(global.fetch).toHaveBeenCalledWith("/upload/");

    process.nextTick(() => {
      expect(wrapper.state()).toEqual({
        // Todo test intial state
      });

      global.fetch.mockClear();
      done();
    });
  });
  it('Renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(
      <App />,
      div
    );
  });
  it('Renders with the expected initial state', () => {
    const wrapper = shallow(<App />);
    const div = document.createElement('div');
    ReactDOM.render(
      <App />,
      div
    );
    process.nextTick(() => {
      expect(wrapper.state()).toEqual({
        // exampleStateVal: false,
      });
    });

  });
  it('renders with an API waiting message shows up', () => {
    const { getByText } = render(<App />);
    const linkElement = getByText(/default text/i);
    expect(linkElement).toBeInTheDocument();
  });
 
  it('render with the app logo', () => {
    const div = document.createElement('div');
    ReactDOM.render(<img id="logoImg" alt="example.com Logo" width="9%" height="9%" src={Logo} />, div);
    ReactDOM.unmountComponentAtNode(div);
  });
  */
})
