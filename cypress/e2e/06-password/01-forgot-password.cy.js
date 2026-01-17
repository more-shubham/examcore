/**
 * Forgot Password Flow Test
 *
 * Tests password reset functionality using OTP from Mailpit.
 * Runs AFTER registration test (uses existing admin user).
 *
 * Run: npm run cy:run:forgot-password
 */

describe('Forgot Password Flow', () => {
  const testData = {
    admin: {
      email: 'admin@examcore.local',
      oldPassword: 'Admin@123',
      newPassword: 'NewAdmin@456',
    },
  };

  before(() => {
    // Clear Mailpit before test (but don't reset database)
    cy.task('clearMailpit');
  });

  it('should request password reset and receive OTP', () => {
    cy.visit('/forgot-password/');

    // Should see forgot password form
    cy.get('input[name="email"]').should('be.visible');

    // Enter email
    cy.get('input[name="email"]').type(testData.admin.email);
    cy.get('button[type="submit"]').click();

    // Should show success message or OTP input
    cy.contains(/sent|otp|verify|check your email/i).should('be.visible');
  });

  it('should reset password with OTP from Mailpit', () => {
    cy.visit('/forgot-password/');

    // Request password reset
    cy.get('input[name="email"]').type(testData.admin.email);
    cy.get('button[type="submit"]').click();

    // Wait for OTP screen or redirect to reset page
    cy.url().then((url) => {
      if (url.includes('reset-password')) {
        // Already on reset password page
        cy.getOTPFromMailpit(testData.admin.email).then((otp) => {
          cy.get('input[name="otp"]').type(otp);
          cy.get('input[name="password"], input[name="new_password"]').type(testData.admin.newPassword);
          cy.get('input[name="confirm_password"], input[name="new_password_confirm"]').type(testData.admin.newPassword);
          cy.get('button[type="submit"]').click();
        });
      } else {
        // Need to navigate to reset password page
        cy.visit('/reset-password/');
        cy.getOTPFromMailpit(testData.admin.email).then((otp) => {
          cy.get('input[name="email"]').type(testData.admin.email);
          cy.get('input[name="otp"]').type(otp);
          cy.get('input[name="password"], input[name="new_password"]').type(testData.admin.newPassword);
          cy.get('input[name="confirm_password"], input[name="new_password_confirm"]').type(testData.admin.newPassword);
          cy.get('button[type="submit"]').click();
        });
      }
    });

    // Should show success or redirect to login
    cy.url().should('satisfy', (url) => {
      return url === Cypress.config().baseUrl + '/' || url.includes('login') || url.includes('success');
    });
  });

  it('should login with new password', () => {
    cy.visit('/');

    cy.get('input[name="username"]').type(testData.admin.email);
    cy.get('input[name="password"]').type(testData.admin.newPassword);
    cy.get('button[type="submit"]').click();

    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
  });

  it('should reject old password after reset', () => {
    // First logout if logged in
    cy.visit('/');
    cy.url().then((url) => {
      if (url.includes('dashboard')) {
        cy.get('form[action="/logout/"]').submit();
      }
    });

    cy.visit('/');
    cy.get('input[name="username"]').type(testData.admin.email);
    cy.get('input[name="password"]').type(testData.admin.oldPassword);
    cy.get('button[type="submit"]').click();

    // Should show error - old password no longer works
    cy.contains(/invalid|incorrect|error/i).should('be.visible');
  });
});
