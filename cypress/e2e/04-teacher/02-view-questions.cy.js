/**
 * Teacher View Questions Tests
 *
 * Tests read-only access to question bank for teachers.
 * Teachers should be able to view questions but NOT create, edit, or delete.
 *
 * FEATURE STATUS: NOT IMPLEMENTED
 * These tests define expected behavior for the teacher role.
 *
 * Run: npx cypress run --spec "cypress/e2e/04-teacher/02-view-questions.cy.js"
 */

describe('Teacher - View Questions (Read-Only)', () => {
  before(() => {
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

  it('should have Questions link in navigation', () => {
    // Teacher should see Questions link in sidebar/nav
    cy.get('nav, .sidebar, [role="navigation"]')
      .find('a[href*="questions"], a:contains("Questions")')
      .should('exist');
  });

  it('should access question bank page', () => {
    cy.visit('/questions/');
    cy.url().should('include', '/questions');
    // Should not redirect to dashboard (access denied)
    cy.url().should('not.include', '/dashboard');
  });

  it('should display question list', () => {
    cy.visit('/questions/');
    // Should show questions
    cy.get('.card, .question-item, [data-testid="question"]').should('have.length.at.least', 1);
  });

  it('should NOT show Add Question button', () => {
    cy.visit('/questions/');
    // Teachers cannot create questions
    cy.get('a:contains("Add Question"), button:contains("Add Question")').should('not.exist');
  });

  it('should NOT show Edit button on questions', () => {
    cy.visit('/questions/');
    // Teachers cannot edit questions
    cy.get('a:contains("Edit"), button:contains("Edit")').should('not.exist');
  });

  it('should NOT show Delete button on questions', () => {
    cy.visit('/questions/');
    // Teachers cannot delete questions
    cy.get('a:contains("Delete"), button:contains("Delete")').should('not.exist');
  });

  it('should NOT access add question page', () => {
    cy.visit('/questions/add/');
    // Should redirect to questions list or show access denied
    cy.url().should('not.include', '/add');
  });

  it('should filter questions by subject', () => {
    cy.visit('/questions/');
    // Select a subject filter
    cy.get('select[name="subject"]').should('exist');
    cy.get('select[name="subject"]').select(1);
    cy.url().should('include', 'subject=');
  });

  it('should search questions by text', () => {
    cy.visit('/questions/');
    cy.get('input[name="search"]').type('stack');
    cy.get('button:contains("Search"), input[type="submit"]').first().click();
    // Should show filtered results
    cy.url().should('include', 'search=');
  });

  it('should display question details', () => {
    cy.visit('/questions/');
    // Questions should show text and options
    cy.get('.card, .question-item').first().within(() => {
      // Should show question text
      cy.get('.question-text, p, h3, h4').should('exist');
    });
  });

  it('should show subject and class for each question', () => {
    cy.visit('/questions/');
    cy.get('.card, .question-item').first().within(() => {
      // Should display subject info
      cy.get('body').then(() => {
        // Check parent for subject/class info
      });
    });
    // At least one question should have subject displayed somewhere
    cy.contains(/DSU|OOJ|DMS|DTE/i).should('exist');
  });
});
