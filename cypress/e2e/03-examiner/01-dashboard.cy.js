/**
 * Examiner Dashboard Tests
 *
 * Tests examiner dashboard access and functionality.
 * Requires seeded database with examiner user.
 *
 * Run: npx cypress run --spec "cypress/e2e/03-examiner/**"
 */

describe('Examiner Dashboard', () => {
  before(() => {
    // Seed database with test data
    cy.task('seedDatabase');
  });

  beforeEach(() => {
    // Login as examiner
    cy.fixture('credentials').then((creds) => {
      cy.visit('/');
      cy.get('input[name="username"]').type(creds.examiner.email);
      cy.get('input[name="password"]').type(creds.examiner.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });
  });

  it('should display examiner dashboard', () => {
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome').should('be.visible');
  });

  it('should show welcome message with examiner name', () => {
    // Verify examiner name appears (Priya Kulkarni from seed data)
    cy.contains('Welcome').should('be.visible');
    cy.contains('Priya').should('be.visible');
  });

  it('should display institution name and logo', () => {
    // Verify institution name
    cy.contains('Model Polytechnic College').should('be.visible');

    // Verify institution logo is displayed
    cy.get('img[src*="institution/"]')
      .should('be.visible')
      .and('have.attr', 'src')
      .and('include', 'institution/');
  });

  it('should display My Questions stat card', () => {
    // Look for My Questions stat card
    cy.contains('My Questions').should('be.visible');
    // Should have a number displayed
    cy.contains('My Questions').parent().find('.text-3xl').should('exist');
  });

  it('should display Exams Created stat card', () => {
    // Look for Exams Created stat card
    cy.contains('Exams Created').should('be.visible');
    // Should have a number displayed
    cy.contains('Exams Created').parent().find('.text-3xl').should('exist');
  });

  it('should have navigation to Questions via stat card', () => {
    cy.contains('My Questions').click();
    cy.url().should('include', '/questions');
  });

  it('should have navigation to Exams via stat card', () => {
    cy.contains('Exams Created').click();
    cy.url().should('include', '/exams');
  });

  it('should have Quick Actions section with links', () => {
    // Verify Quick Actions section exists
    cy.contains('Quick Actions').should('be.visible');

    // Verify action links exist
    cy.contains('Add Question').should('be.visible');
    cy.contains('Question Bank').should('be.visible');
    cy.contains('Create Exam').should('be.visible');
  });

  it('should navigate to add question from Quick Actions', () => {
    cy.contains('Add Question').click();
    cy.url().should('include', '/questions/add');
  });

  it('should navigate to create exam from Quick Actions', () => {
    cy.contains('Create Exam').click();
    cy.url().should('include', '/exams/add');
  });

  it('should display user profile information', () => {
    cy.contains('Your Profile').should('be.visible');
    cy.contains('Email:').should('be.visible');
    cy.contains('Role:').should('be.visible');
    cy.contains('examiner').should('be.visible');
  });

  it('should have logout functionality', () => {
    cy.contains('Logout').click();
    cy.url().should('eq', Cypress.config().baseUrl + '/');
  });
});
