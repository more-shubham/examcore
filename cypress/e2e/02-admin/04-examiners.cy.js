/**
 * Admin Examiner Management Tests
 *
 * Tests inviting and managing examiners.
 * Automatically sets up admin user if not exists.
 *
 * Run: npm run cy:run:admin
 */

describe('Admin - Examiner Management', () => {
  const admin = {
    email: 'admin@examcore.local',
    password: 'Admin@123',
  };

  const examiner = {
    email: 'examiner@examcore.local',
    firstName: 'John',
    lastName: 'Examiner',
    phone: '+91-9876543211',
    password: 'Examiner@123',
  };

  before(() => {
    // NO setupAdminUser - uses data from registration test
    // Clear Mailpit before sending invitations
    cy.task('clearMailpit');
  });

  beforeEach(() => {
    // Login once and cache the session for all tests
    cy.loginAsAdmin();
  });

  it('should navigate to examiners page', () => {
    cy.visit('/examiners/');
    cy.url().should('include', '/examiners');
    cy.contains(/examiner/i).should('be.visible');
  });

  it('should invite an examiner', () => {
    cy.visit('/examiners/');

    // Click invite button
    cy.contains('button', 'Invite Examiner').click();

    // Fill form in modal
    cy.get('input[name="email"]').type(examiner.email);
    cy.get('input[name="first_name"]').type(examiner.firstName);
    cy.get('input[name="last_name"]').type(examiner.lastName);
    cy.get('input[name="phone"]').type(examiner.phone);

    // Submit - button says "Send Invite"
    cy.contains('button', 'Send Invite').click();

    // Should show success or the examiner in the list
    cy.contains(examiner.email).should('be.visible');
  });

  it('should show pending invitation in list', () => {
    cy.visit('/examiners/');

    // The invited examiner should appear
    cy.contains(examiner.email).should('be.visible');
  });
});

describe('Examiner - Accept Invitation', () => {
  const examiner = {
    email: 'examiner@examcore.local',
    password: 'Examiner@123',
  };

  it('should accept invitation via email link', () => {
    // Get invitation email from Mailpit
    cy.waitForEmail(examiner.email).then((message) => {
      const mailpitUrl = Cypress.env('MAILPIT_URL') || 'http://localhost:8025';

      cy.request({
        method: 'GET',
        url: `${mailpitUrl}/api/v1/message/${message.ID}`,
        headers: { 'Accept': 'application/json' },
      }).then((response) => {
        const body = response.body.Text || response.body.HTML || '';

        // Extract invitation link
        const linkMatch = body.match(/http[s]?:\/\/[^\s<>"]+/);

        if (linkMatch) {
          // Visit invitation link (extract path only)
          const fullUrl = linkMatch[0];
          const url = new URL(fullUrl);
          cy.visit(url.pathname + url.search);

          // Set password
          cy.get('input[name="password"]').type(examiner.password);
          cy.get('input[name="confirm_password"]').type(examiner.password);
          cy.get('button[type="submit"]').click();

          // Should redirect to login or dashboard
          cy.url().should('satisfy', (url) => {
            return url.includes('dashboard') || url === Cypress.config().baseUrl + '/';
          });
        }
      });
    });
  });

  it('should login as examiner', () => {
    cy.visit('/');
    cy.get('input[name="username"]').type(examiner.email);
    cy.get('input[name="password"]').type(examiner.password);
    cy.get('button[type="submit"]').click();

    cy.url().should('include', '/dashboard');
  });
});
