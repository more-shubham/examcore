/**
 * Teacher Dashboard Tests
 *
 * Tests teacher dashboard access and functionality.
 * Teacher dashboard shows assigned subjects and statistics.
 *
 * Run: npx cypress run --spec "cypress/e2e/04-teacher/**"
 */

describe('Teacher Dashboard', () => {
  before(() => {
    // Seed database with test data
    cy.task('seedDatabase');
  });

  beforeEach(() => {
    // Login as teacher (DBMS teacher - Santosh Jadhav)
    cy.fixture('credentials').then((creds) => {
      cy.visit('/');
      cy.get('input[name="username"]').type(creds.teacher.email);
      cy.get('input[name="password"]').type(creds.teacher.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });
  });

  it('should display teacher dashboard', () => {
    cy.url().should('include', '/dashboard');
    cy.contains(/dashboard|welcome/i).should('be.visible');
  });

  it('should show teacher name', () => {
    // DBMS teacher is Santosh Jadhav
    cy.contains('Santosh').should('be.visible');
  });

  it('should display institution name and logo', () => {
    // Verify institution name
    cy.contains(/polytechnic|college|model/i).should('be.visible');

    // Check for logo (may or may not be visible depending on if logo file exists)
    cy.get('img').then(($imgs) => {
      if ($imgs.length > 0) {
        cy.wrap($imgs).first().should('be.visible');
      }
    });
  });

  it('should display My Subjects section', () => {
    // Teacher dashboard should show assigned subjects
    cy.contains('My Subjects').should('be.visible');
  });

  it('should show assigned subjects', () => {
    // DBMS teacher has DBMS subjects assigned
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasSubjects = text.includes('DBMS') || text.includes('Database');
      expect(hasSubjects).to.be.true;
    });
  });

  it('should display statistics cards', () => {
    // Dashboard should show statistics
    cy.contains('Subjects').should('be.visible');
    cy.contains('Questions').should('be.visible');
    cy.contains('Exams').should('be.visible');
  });

  it('should display profile information', () => {
    // Look for profile section
    cy.contains('Your Profile').should('be.visible');
    cy.contains(/Santosh/i).should('be.visible');
    cy.contains(/teacher/i).should('be.visible');
  });

  it('should have navigation menu', () => {
    // Check for navigation elements
    cy.get('nav, [role="navigation"], .sidebar, .menu').should('exist');
  });

  it('should have logout functionality', () => {
    cy.get('form[action="/logout/"], button:contains("Logout"), a:contains("Logout")').first().then(($logout) => {
      if ($logout.is('form')) {
        cy.wrap($logout).submit();
      } else {
        cy.wrap($logout).click();
      }
    });
    cy.url().should('not.include', '/dashboard');
  });
});
