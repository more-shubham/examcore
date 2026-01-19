/**
 * Student Notification Preferences Tests
 *
 * Tests the notification preferences page and settings.
 * Requires seeded database with student user.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/09-notifications.cy.js"
 */

describe('Student Notification Preferences', () => {
  before(() => {
    // Seed database with test data
    cy.task('seedDatabase');
  });

  beforeEach(() => {
    // Login as student
    cy.fixture('credentials').then((creds) => {
      cy.visit('/');
      cy.get('input[name="username"]').type(creds.student.email);
      cy.get('input[name="password"]').type(creds.student.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });
  });

  it('should have Notification Preferences link on profile page', () => {
    cy.visit('/profile/');
    cy.contains('Notification Preferences').should('be.visible');
  });

  it('should navigate to notification preferences from profile', () => {
    cy.visit('/profile/');
    cy.contains('Notification Preferences').click();
    cy.url().should('include', '/profile/notifications');
  });

  it('should display notification preferences page header', () => {
    cy.visit('/profile/notifications/');

    cy.contains('Notification Preferences').should('be.visible');
    cy.contains('Manage your email notification settings').should('be.visible');
  });

  it('should display user email in info box', () => {
    cy.visit('/profile/notifications/');

    cy.fixture('credentials').then((creds) => {
      cy.contains(creds.student.email).should('be.visible');
    });
  });

  it('should have back to profile link', () => {
    cy.visit('/profile/notifications/');

    cy.contains('Back to Profile').should('be.visible');
    cy.contains('Back to Profile').should('have.attr', 'href', '/profile/');
  });

  it('should navigate back to profile page', () => {
    cy.visit('/profile/notifications/');

    cy.contains('Back to Profile').click();
    cy.url().should('include', '/profile');
    cy.url().should('not.include', '/notifications');
  });

  it('should display all notification options', () => {
    cy.visit('/profile/notifications/');

    // Check for all three notification types
    cy.contains('New Exam Notifications').should('be.visible');
    cy.contains('Exam Reminders').should('be.visible');
    cy.contains('Result Notifications').should('be.visible');
  });

  it('should display help text for each notification option', () => {
    cy.visit('/profile/notifications/');

    cy.contains('email when a new exam is published').should('be.visible');
    cy.contains('reminder email 24 hours before').should('be.visible');
    cy.contains('email when your exam result is available').should('be.visible');
  });

  it('should have checkboxes for each notification type', () => {
    cy.visit('/profile/notifications/');

    cy.get('input[name="exam_published"]').should('exist');
    cy.get('input[name="exam_reminder"]').should('exist');
    cy.get('input[name="result_available"]').should('exist');
  });

  it('should have all notifications enabled by default', () => {
    cy.visit('/profile/notifications/');

    // Default should be all enabled
    cy.get('input[name="exam_published"]').should('be.checked');
    cy.get('input[name="exam_reminder"]').should('be.checked');
    cy.get('input[name="result_available"]').should('be.checked');
  });

  it('should toggle notification preferences', () => {
    cy.visit('/profile/notifications/');

    // Uncheck exam_published
    cy.get('input[name="exam_published"]').uncheck();
    cy.get('input[name="exam_published"]').should('not.be.checked');

    // Uncheck exam_reminder
    cy.get('input[name="exam_reminder"]').uncheck();
    cy.get('input[name="exam_reminder"]').should('not.be.checked');
  });

  it('should save notification preferences', () => {
    cy.visit('/profile/notifications/');

    // Uncheck one option
    cy.get('input[name="exam_published"]').uncheck();

    // Submit form
    cy.contains('Save Preferences').click();

    // Should show success message
    cy.contains(/updated|success/i).should('be.visible');
  });

  it('should persist saved preferences after reload', () => {
    cy.visit('/profile/notifications/');

    // Uncheck exam_reminder
    cy.get('input[name="exam_reminder"]').uncheck();

    // Submit form
    cy.contains('Save Preferences').click();

    // Wait for success
    cy.contains(/updated|success/i).should('be.visible');

    // Reload page
    cy.reload();

    // Check that preference was saved
    cy.get('input[name="exam_reminder"]').should('not.be.checked');
  });

  it('should have cancel button', () => {
    cy.visit('/profile/notifications/');

    cy.contains('Cancel').should('be.visible');
  });

  it('should cancel changes and return to profile', () => {
    cy.visit('/profile/notifications/');

    // Make changes
    cy.get('input[name="exam_published"]').uncheck();

    // Click cancel
    cy.contains('Cancel').click();

    // Should go to profile
    cy.url().should('include', '/profile');
    cy.url().should('not.include', '/notifications');
  });

  it('should enable all notifications when previously disabled', () => {
    cy.visit('/profile/notifications/');

    // First disable all
    cy.get('input[name="exam_published"]').uncheck();
    cy.get('input[name="exam_reminder"]').uncheck();
    cy.get('input[name="result_available"]').uncheck();

    // Save
    cy.contains('Save Preferences').click();
    cy.contains(/updated|success/i).should('be.visible');

    // Now enable all
    cy.get('input[name="exam_published"]').check();
    cy.get('input[name="exam_reminder"]').check();
    cy.get('input[name="result_available"]').check();

    // Save again
    cy.contains('Save Preferences').click();
    cy.contains(/updated|success/i).should('be.visible');

    // Verify all are enabled
    cy.reload();
    cy.get('input[name="exam_published"]').should('be.checked');
    cy.get('input[name="exam_reminder"]').should('be.checked');
    cy.get('input[name="result_available"]').should('be.checked');
  });

  it('should be accessible via direct URL', () => {
    cy.visit('/profile/notifications/');
    cy.contains('Notification Preferences').should('be.visible');
  });

  it('should require authentication', () => {
    // Logout first using form submission
    cy.get('body').then(($body) => {
      const $form = $body.find('form[action="/logout/"]');
      if ($form.length > 0) {
        cy.wrap($form).submit();
      } else {
        const $logout = $body.find('button:contains("Logout"), a:contains("Logout")');
        if ($logout.length > 0) {
          cy.wrap($logout).first().click();
        }
      }
    });

    // Try to access notification preferences
    cy.visit('/profile/notifications/');

    // Should redirect to login - check that pathname is login page (not /profile/notifications)
    cy.location('pathname').should('not.eq', '/profile/notifications/');
  });
});
