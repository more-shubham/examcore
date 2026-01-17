/**
 * Admin Teacher Management Tests
 *
 * Tests inviting and managing teachers.
 * Run after auth tests (admin must exist).
 *
 * Run: npm run cy:run:admin
 */

describe('Admin - Teacher Management', () => {
  const admin = {
    email: 'admin@examcore.local',
    password: 'Admin@123',
  };

  const teacher = {
    email: 'teacher@examcore.local',
    firstName: 'Jane',
    lastName: 'Teacher',
    phone: '+91-9876543212',
    password: 'Teacher@123',
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

  it('should navigate to teachers page', () => {
    cy.visit('/teachers/');
    cy.url().should('include', '/teachers');
    cy.contains(/teacher/i).should('be.visible');
  });

  it('should invite a teacher', () => {
    cy.visit('/teachers/');

    // Click invite button
    cy.contains('button', 'Invite Teacher').click();

    // Fill form in modal
    cy.get('input[name="email"]').type(teacher.email);
    cy.get('input[name="first_name"]').type(teacher.firstName);
    cy.get('input[name="last_name"]').type(teacher.lastName);
    cy.get('input[name="phone"]').type(teacher.phone);

    // Submit - button says "Send Invite"
    cy.contains('button', 'Send Invite').click();

    // Should show success or the teacher in the list
    cy.contains(teacher.email).should('be.visible');
  });

  it('should show pending invitation in list', () => {
    cy.visit('/teachers/');

    // The invited teacher should appear
    cy.contains(teacher.email).should('be.visible');
  });
});

describe('Teacher - Accept Invitation', () => {
  const teacher = {
    email: 'teacher@examcore.local',
    password: 'Teacher@123',
  };

  it('should accept invitation via email link', () => {
    // Get invitation email from Mailpit
    cy.waitForEmail(teacher.email).then((message) => {
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
          cy.get('input[name="password"]').type(teacher.password);
          cy.get('input[name="confirm_password"]').type(teacher.password);
          cy.get('button[type="submit"]').click();

          // Should redirect to login or dashboard
          cy.url().should('satisfy', (url) => {
            return url.includes('dashboard') || url === Cypress.config().baseUrl + '/';
          });
        }
      });
    });
  });

  it('should login as teacher', () => {
    cy.visit('/');
    cy.get('input[name="username"]').type(teacher.email);
    cy.get('input[name="password"]').type(teacher.password);
    cy.get('button[type="submit"]').click();

    cy.url().should('include', '/dashboard');
  });
});
