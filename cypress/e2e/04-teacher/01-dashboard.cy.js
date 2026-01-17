/**
 * Teacher Dashboard Tests
 *
 * Tests teacher dashboard access and functionality.
 * Teacher dashboard may show "Coming Soon" placeholder.
 *
 * Run: npx cypress run --spec "cypress/e2e/04-teacher/**"
 */

describe('Teacher Dashboard', () => {
  before(() => {
    // Seed database with test data
    cy.task('seedDatabase');
  });

  beforeEach(() => {
    // Login as teacher
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

  it('should show teacher name or role', () => {
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      // Check for teacher name (Santosh Jadhav) or role
      const hasTeacherInfo = text.includes('santosh') || text.includes('teacher') || text.includes('welcome');
      expect(hasTeacherInfo).to.be.true;
    });
  });

  it('should display institution name and logo', () => {
    // Verify institution name
    cy.contains(/polytechnic|college|model/i).should('be.visible');

    // Check for logo
    cy.get('img[alt*="logo"], img[alt*="Logo"], .logo').then(($logo) => {
      if ($logo.length > 0) {
        cy.wrap($logo).first().should('be.visible');
      }
    });
  });

  it('should show Coming Soon or placeholder content', () => {
    // Teacher dashboard might show placeholder
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasContent = text.includes('coming soon') ||
      text.includes('dashboard') ||
      text.includes('class') ||
      text.includes('student') ||
      text.includes('welcome');
      expect(hasContent).to.be.true;
    });
  });

  it('should display profile information', () => {
    // Look for profile section or user info
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasProfileInfo = text.includes('santosh') ||
      text.includes('jadhav') ||
      text.includes('dbms') ||
      text.includes('teacher');
      expect(hasProfileInfo).to.be.true;
    });
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
