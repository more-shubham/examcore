/**
 * Teacher View Questions Tests
 *
 * Tests read-only access to question bank for teachers.
 * Teachers should be able to view questions but NOT create, edit, or delete.
 *
 * FEATURE STATUS: IMPLEMENTED
 * Teachers can view questions from their assigned subjects.
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

  it('should have Questions link on dashboard', () => {
    // Teacher should see Questions link in Quick Actions
    cy.get('a[href*="questions"]').should('exist');
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
    cy.get('.card').should('have.length.at.least', 1);
    // Should show question text somewhere on page
    cy.get('.card p.text-gray-900').should('exist');
  });

  it('should show subject and class for each question', () => {
    cy.visit('/questions/');
    // Questions show subject badge - DBMS teacher sees DBMS questions
    cy.get('.card').first().should('exist');
    // At least one question should have subject displayed somewhere (DBMS for this teacher)
    cy.contains(/DBMS|DMS/i).should('exist');
  });
});
