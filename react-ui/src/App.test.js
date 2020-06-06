import React from 'react';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import store from './app/store';
import App from './App';
import Controls from './features/Controls';

test('renders homepage', () => {
  const { getByText } = render(
    <Provider store={store}>
      <App />
    </Provider>
  );

  expect(getByText(/Start a new game/i)).toBeInTheDocument();
});


test('renders role', () => {
  const { getByText } = render(
    <Provider store={store}>
      <Controls />
    </Provider>
  );

  expect(getByText(/You are a /i)).toBeInTheDocument();
});
