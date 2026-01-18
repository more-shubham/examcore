/**
 * Teacher View Exams Tests
 *
 * Tests read-only access to exams for teachers.
 * Teachers should be able to view exams but NOT create, edit, or delete.
 *
 * FEATURE STATUS: IMPLEMENTED
 * Teachers can view exams from their assigned subjects.
 *
 * Run: npx cypress run --spec "cypress/e2e/04-teacher/03-view-exams.cy.js"
 */

describe('Teacher - View Exams (Read-Only)', () => {
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

  it('should have Exams link on dashboard', () => {
    // Teacher should see Exams link in Quick Actions
    cy.get('a[href*="exams"]').should('exist');
  });

  it('should access exams list page', () => {
    cy.visit('/exams/');
    cy.url().should('include', '/exams');
    // Should not redirect to dashboard (access denied)
    cy.url().should('not.include', '/dashboard');
  });

  it('should display exam list', () => {
    cy.visit('/exams/');
    // Should show exams
    cy.get('.card, .exam-item, [data-testid="exam"], table tbody tr').should('have.length.at.least', 1);
  });

  it('should NOT show Create Exam button', () => {
    cy.visit('/exams/');
    // Teachers cannot create exams
    cy.get('a:contains("Create Exam"), a:contains("Add Exam"), button:contains("Create")').should('not.exist');
  });

  it('should NOT show Edit button on exams', () => {
    cy.visit('/exams/');
    // Teachers cannot edit exams
    cy.get('a:contains("Edit"), button:contains("Edit")').should('not.exist');
  });

  it('should NOT show Delete button on exams', () => {
    cy.visit('/exams/');
    // Teachers cannot delete exams
    cy.get('a:contains("Delete"), button:contains("Delete")').should('not.exist');
  });

  it('should NOT access create exam page', () => {
    cy.visit('/exams/add/');
    // Should redirect to exams list or show access denied
    cy.url().should('not.include', '/add');
  });

  it('should view exam details', () => {
    cy.visit('/exams/');
    // Click on first exam View button
    cy.get('.card a.btn-ghost').first().click();
    // Should show exam detail page
    cy.url().should('match', /\/exams\/\d+/);
  });

  it('should display exam information', () => {
    cy.visit('/exams/');
    // Exams should show title, subject, dates
    cy.get('.card').first().should('exist');
    // The card should contain exam title (as link)
    cy.get('.card a.text-lg.font-medium').should('exist');
  });

  it('should show exam status (draft/published/completed)', () => {
    cy.visit('/exams/');
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasStatus = text.includes('draft') ||
      text.includes('published') ||
      text.includes('completed') ||
      text.includes('active') ||
      text.includes('status');
      expect(hasStatus).to.be.true;
    });
  });

  it('should filter exams by subject', () => {
    cy.visit('/exams/');
    // If filter exists, use it
    cy.get('select[name="subject"]').then(($select) => {
      if ($select.length > 0) {
        cy.wrap($select).select(1);
        cy.url().should('include', 'subject=');
      }
    });
  });

  it('should display question count for each exam', () => {
    cy.visit('/exams/');
    // Exams should show number of questions
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasQuestionCount = /\d+\s*question/i.test(text) || text.includes('questions');
      expect(hasQuestionCount).to.be.true;
    });
  });
});
