/**
 * Admin Student Management Tests
 *
 * Tests inviting and managing students within classes.
 * Run after classes test (classes must exist).
 *
 * Run: npm run cy:run:admin
 */

describe('Admin - Student Management', () => {
  const admin = {
    email: 'admin@examcore.local',
    password: 'Admin@123',
  };

  const student = {
    email: 'student@examcore.local',
    firstName: 'Rahul',
    lastName: 'Sharma',
    phone: '+91-9876543213',
    password: 'Student@123',
  };

  // Use semester created by classes test
  const className = 'CO - 3rd Semester';

  before(() => {
    // NO setupAdminUser - uses data from registration test
    // Clear Mailpit before sending invitations
    cy.task('clearMailpit');
  });

  beforeEach(() => {
    // Login once and cache the session for all tests
    cy.loginAsAdmin();
  });

  it('should navigate to students page for CO 3rd Semester', () => {
    cy.visit('/classes/');
    // Find class row and click the Students link within it
    cy.contains('.class-item', className).find('a').contains('Students').click();
    cy.url().should('include', '/students');
  });

  it('should invite a student to CO 3rd Semester', () => {
    // Navigate to class students
    cy.visit('/classes/');
    cy.contains('.class-item', className).find('a').contains('Students').click();

    // Click invite button
    cy.contains('button', 'Invite Student').click();

    // Fill form in modal
    cy.get('input[name="email"]').type(student.email);
    cy.get('input[name="first_name"]').type(student.firstName);
    cy.get('input[name="last_name"]').type(student.lastName);
    cy.get('input[name="phone"]').type(student.phone);

    // Submit - button says "Send Invite"
    cy.contains('button', 'Send Invite').click();

    // Should show success or the student in the list
    cy.contains(student.email).should('be.visible');
  });

  it('should show pending student in list', () => {
    cy.visit('/classes/');
    cy.contains('.class-item', className).find('a').contains('Students').click();

    // The invited student should appear in pending invitations
    cy.contains(student.email).should('be.visible');
  });
});

describe('Student - Accept Invitation', () => {
  const student = {
    email: 'student@examcore.local',
    password: 'Student@123',
  };

  const className = 'CO - 3rd Semester';

  it('should accept invitation via email link', () => {
    // Get invitation email from Mailpit
    cy.waitForEmail(student.email).then((message) => {
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
          cy.get('input[name="password"]').type(student.password);
          cy.get('input[name="confirm_password"]').type(student.password);
          cy.get('button[type="submit"]').click();

          // Should redirect to login or dashboard
          cy.url().should('satisfy', (url) => {
            return url.includes('dashboard') || url === Cypress.config().baseUrl + '/';
          });
        }
      });
    });
  });

  it('should login as student', () => {
    cy.visit('/');
    cy.get('input[name="username"]').type(student.email);
    cy.get('input[name="password"]').type(student.password);
    cy.get('button[type="submit"]').click();

    cy.url().should('include', '/dashboard');
  });

  it('should see assigned class on dashboard', () => {
    cy.visit('/');
    cy.get('input[name="username"]').type(student.email);
    cy.get('input[name="password"]').type(student.password);
    cy.get('button[type="submit"]').click();

    // Student should see their semester
    cy.contains(/CO.*3rd|semester/i).should('be.visible');
  });
});
