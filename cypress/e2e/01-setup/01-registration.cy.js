/**
 * Registration Flow Test
 *
 * This test resets the database once, runs validation tests first,
 * then completes successful registration LAST so the data persists
 * for subsequent test files (login, dashboard, etc.)
 *
 * Requirements:
 * 1. Django server running on localhost:8000
 * 2. Mailpit running on localhost:8025
 *
 * Run: npm run cy:run:register
 */

describe('Admin Registration Flow', () => {
  const testData = {
    admin: {
      email: 'admin@examcore.local',
      password: 'Admin@123',
    },
    institution: {
      name: 'Model Polytechnic College, Mumbai',
      email: 'principal@modelpolytechnic.edu.in',
      phone: '+91-22-26543210',
      address: 'Plot No. 5, Sector-10, Vashi, Navi Mumbai - 400703, Maharashtra',
    },
  };

  before(() => {
    // Reset database and clear Mailpit ONCE before all tests
    cy.task('resetDatabase');
    cy.task('clearMailpit');
  });

  // ========================================
  // VALIDATION TESTS FIRST (before registration)
  // ========================================

  it('should show validation error for empty form submission', () => {
    cy.visit('/');

    // Verify we see the registration form
    cy.contains('Create Your Account').should('be.visible');

    // Try submitting empty form
    cy.contains('button', 'Continue').click();
    cy.get('input[name="email"]:invalid').should('exist');
  });

  it('should show validation error for invalid email format', () => {
    cy.visit('/');

    // Try invalid email
    cy.get('input[name="email"]').type('invalid-email');
    cy.get('input[name="password"]').type('Admin@123');
    cy.get('input[name="confirm_password"]').type('Admin@123');
    cy.contains('button', 'Continue').click();

    // Should show invalid email error
    cy.get('input[name="email"]:invalid').should('exist');
  });

  it('should show validation error for password mismatch', () => {
    cy.visit('/');

    // Fill form with mismatched passwords
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('Admin@123');
    cy.get('input[name="confirm_password"]').type('DifferentPassword@123');
    cy.contains('button', 'Continue').click();

    // Should show password mismatch error or stay on page
    cy.url().should('not.include', '/dashboard');
  });

  // ========================================
  // SUCCESSFUL REGISTRATION LAST
  // This creates the data that persists for all subsequent tests
  // ========================================

  it('should complete full registration with OTP and logo upload', () => {
    // Clear mailpit before this test
    cy.task('clearMailpit');

    // Step 1: Visit root - should see registration form (no admin exists)
    cy.visit('/');
    cy.log('Step 1: Checking for registration form');

    // Verify we see the registration form
    cy.contains('Create Your Account').should('be.visible');
    cy.get('input[name="email"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('input[name="confirm_password"]').should('be.visible');

    // Step 2: Fill registration form
    cy.log('Step 2: Filling registration form');
    cy.get('input[name="email"]').type(testData.admin.email);
    cy.get('input[name="password"]').type(testData.admin.password);
    cy.get('input[name="confirm_password"]').type(testData.admin.password);
    cy.contains('button', 'Continue').click();

    // Step 3: OTP verification screen should appear
    cy.log('Step 3: Verifying OTP screen');
    cy.contains('Verify Your Email', { timeout: 10000 }).should('be.visible');
    cy.contains(testData.admin.email).should('be.visible');
    cy.get('input[name="otp"]').should('be.visible');

    // Step 4: Fetch OTP from Mailpit and enter it
    cy.log('Step 4: Fetching OTP from Mailpit');
    cy.getOTPFromMailpit(testData.admin.email).then((otp) => {
      cy.log(`Found OTP: ${otp}`);
      cy.get('input[name="otp"]').type(otp);
      cy.contains('button', 'Verify').click();
    });

    // Step 5: Institution setup form should appear
    cy.log('Step 5: Setting up institution');
    cy.contains(/setup|institution/i, { timeout: 10000 }).should('be.visible');

    // Fill institution details
    cy.get('input[name="name"]').type(testData.institution.name);
    cy.get('input[name="email"]').type(testData.institution.email);
    cy.get('input[name="phone"]').type(testData.institution.phone);
    cy.get('textarea[name="address"]').type(testData.institution.address);

    // Step 5b: Upload institution logo
    cy.log('Step 5b: Uploading institution logo');
    cy.get('input#id_logo, input[name="logo"]').selectFile('cypress/fixtures/logo.png', { force: true });
    cy.log('Logo uploaded successfully');

    cy.contains('button', /complete|setup|submit/i).click();

    // Step 6: Should be redirected to dashboard
    cy.log('Step 6: Verifying dashboard redirect');
    cy.url().should('include', '/dashboard', { timeout: 10000 });

    // Step 7: Verify institution name and logo appear on dashboard
    cy.log('Step 7: Verifying institution info on dashboard');
    cy.contains('Model Polytechnic').should('be.visible');

    // Verify logo was uploaded and is displayed
    cy.get('img[alt*="Model Polytechnic"], img[src*="institution/"]').should('be.visible');

    // Logout so next test can login fresh
    cy.get('form[action="/logout/"]').submit();
    cy.url().should('eq', Cypress.config().baseUrl + '/');

    cy.log('Registration completed successfully! Data persists for subsequent tests.');
  });
});
