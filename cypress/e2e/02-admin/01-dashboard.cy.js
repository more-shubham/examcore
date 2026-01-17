/**
 * Admin Dashboard Tests
 *
 * Tests admin dashboard access, navigation, and verification.
 * Uses data created by registration test (01-registration.cy.js).
 *
 * Run: npm run cy:run:admin
 */

describe('Admin Dashboard', () => {
  const admin = {
    email: 'admin@examcore.local',
    password: 'Admin@123',
  };

  // NO setupAdminUser - uses data from registration test

  beforeEach(() => {
    // Login once and cache the session for all tests
    cy.loginAsAdmin();
    cy.visit('/dashboard/');
  });

  it('should display admin dashboard with welcome message', () => {
    cy.url().should('include', '/dashboard');
    cy.contains(/dashboard|welcome/i).should('be.visible');
  });

  it('should display institution name and logo', () => {
    // Verify institution name appears (from registration)
    cy.contains(/polytechnic|college|institution/i).should('be.visible');

    // Verify institution logo is displayed (uploaded during registration)
    cy.get('img[alt*="Model Polytechnic"], img[alt*="Polytechnic"], img[src*="institution/"]')
      .should('be.visible')
      .and('have.attr', 'src')
      .and('include', 'institution/');
  });

  it('should display dashboard statistics', () => {
    // Look for common stat labels in the dashboard
    cy.get('body').then(($body) => {
      const statsText = $body.text().toLowerCase();
      // At least one of these should be present
      const hasStats = ['class', 'student', 'teacher', 'examiner', 'exam', 'question']
        .some(stat => statsText.includes(stat));
      expect(hasStats).to.be.true;
    });
  });

  it('should have navigation to Classes', () => {
    cy.contains(/classes|semester/i).should('be.visible');
    cy.contains(/classes|semester/i).click();
    cy.url().should('include', '/classes');
  });

  it('should have navigation to Examiners', () => {
    cy.contains(/examiner/i).should('be.visible');
    cy.contains(/examiner/i).click();
    cy.url().should('include', '/examiners');
  });

  it('should have navigation to Teachers', () => {
    cy.contains(/teacher/i).should('be.visible');
    cy.contains(/teacher/i).click();
    cy.url().should('include', '/teachers');
  });

  it('should display quick action links', () => {
    // Look for quick action buttons/links
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasQuickActions = ['add', 'create', 'manage', 'view']
        .some(action => text.includes(action));
      expect(hasQuickActions).to.be.true;
    });
  });

  it('should show profile/user information', () => {
    // Look for admin name or email
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasUserInfo = text.includes('admin') || text.includes('rajesh');
      expect(hasUserInfo).to.be.true;
    });
  });

  it('should have logout functionality', () => {
    // Find and click logout
    cy.get('form[action="/logout/"], button:contains("Logout"), a:contains("Logout")').first().then(($logout) => {
      if ($logout.is('form')) {
        cy.wrap($logout).submit();
      } else {
        cy.wrap($logout).click();
      }
    });

    // Should be redirected to login page
    cy.url().should('not.include', '/dashboard');
  });
});
