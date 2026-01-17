/**
 * Login Flow Test
 *
 * Tests login functionality using data created by registration test.
 * IMPORTANT: This test depends on 01-registration.cy.js running first.
 *
 * Run: npm run cy:run:login
 * Or run all setup tests: npm run cy:run:setup
 */

describe('Admin Login Flow', () => {
  // Use the same credentials from registration test
  const testData = {
    admin: {
      email: 'admin@examcore.local',
      password: 'Admin@123',
    },
  };

  // NO setupAdminUser needed - registration test already created the data

  it('should login with valid credentials', () => {
    cy.visit('/');

    // Should see login form (admin exists from registration)
    cy.get('input[name="username"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');

    // Enter credentials
    cy.get('input[name="username"]').type(testData.admin.email);
    cy.get('input[name="password"]').type(testData.admin.password);
    cy.get('button[type="submit"]').click();

    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains(/dashboard|welcome/i).should('be.visible');

    // Verify logo is visible (uploaded during registration)
    cy.get('img[src*="institution/"]').should('be.visible');
  });

  it('should reject invalid password', () => {
    cy.visit('/');

    cy.get('input[name="username"]').type(testData.admin.email);
    cy.get('input[name="password"]').type('WrongPassword123');
    cy.get('button[type="submit"]').click();

    // Should show error and stay on login page
    cy.url().should('eq', Cypress.config().baseUrl + '/');
    cy.contains(/invalid|incorrect|error/i).should('be.visible');
  });

  it('should reject non-existent user', () => {
    cy.visit('/');

    cy.get('input[name="username"]').type('nonexistent@example.com');
    cy.get('input[name="password"]').type('SomePassword123');
    cy.get('button[type="submit"]').click();

    // Should show error
    cy.url().should('eq', Cypress.config().baseUrl + '/');
    cy.contains(/invalid|incorrect|error/i).should('be.visible');
  });

  it('should logout successfully', () => {
    // First login
    cy.visit('/');
    cy.get('input[name="username"]').type(testData.admin.email);
    cy.get('input[name="password"]').type(testData.admin.password);
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');

    // Then logout
    cy.get('form[action="/logout/"]').submit();

    // Should redirect to login page
    cy.url().should('eq', Cypress.config().baseUrl + '/');
  });
});
