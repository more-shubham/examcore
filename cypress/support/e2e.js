// ***********************************************************
// This file is loaded automatically before your test files.
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

import './commands';

// Prevent uncaught exceptions from failing tests
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false prevents the error from failing the test
  return false;
});

// Clean up after each test if needed
afterEach(() => {
  // Clear any session storage or local storage if needed
  cy.window().then((win) => {
    win.sessionStorage.clear();
  });
});
