/**
 * Student Exam History Tests
 *
 * Tests the exam history page with filtering and sorting.
 * Requires seeded database with student who has completed exams.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/08-exam-history.cy.js"
 */

describe('Student Exam History', () => {
  before(() => {
    // Seed database with test data including completed exam attempts
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

  it('should have History link on exam list page', () => {
    cy.visit('/my-exams/');
    cy.contains('History').should('be.visible');
    cy.contains('History').should('have.attr', 'href').and('include', '/history');
  });

  it('should navigate to history page from exam list', () => {
    cy.visit('/my-exams/');
    cy.contains('History').click();
    cy.url().should('include', '/my-exams/history');
    cy.contains('Exam History').should('be.visible');
  });

  it('should display page header and back button', () => {
    cy.visit('/my-exams/history/');

    cy.contains('Exam History').should('be.visible');
    cy.contains('View all your past exam attempts').should('be.visible');
    cy.contains('Back to Exams').should('be.visible');
  });

  it('should display filter controls', () => {
    cy.visit('/my-exams/history/');

    // Check for filter elements
    cy.get('select[name="subject"]').should('exist');
    cy.get('select[name="status"]').should('exist');
    cy.get('input[name="date_from"]').should('exist');
    cy.get('input[name="date_to"]').should('exist');
    cy.get('select[name="sort"]').should('exist');
    cy.contains('Apply Filters').should('be.visible');
  });

  it('should display sort options', () => {
    cy.visit('/my-exams/history/');

    cy.get('select[name="sort"]').should('contain', 'Date (Newest)');
    cy.get('select[name="sort"]').should('contain', 'Date (Oldest)');
    cy.get('select[name="sort"]').should('contain', 'Score (Highest)');
    cy.get('select[name="sort"]').should('contain', 'Score (Lowest)');
  });

  it('should display status filter options', () => {
    cy.visit('/my-exams/history/');

    cy.get('select[name="status"]').should('contain', 'All Results');
    cy.get('select[name="status"]').should('contain', 'Passed');
    cy.get('select[name="status"]').should('contain', 'Failed');
  });

  it('should show empty state when no history', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('No Exam History')) {
        cy.contains('No Exam History Yet').should('be.visible');
        cy.contains('Complete your first exam').should('be.visible');
      }
    });
  });

  it('should display history table when exams completed', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        // Should show table headers
        cy.get('table').should('exist');
        cy.contains('th', 'Exam').should('be.visible');
        cy.contains('th', 'Subject').should('be.visible');
        cy.contains('th', 'Date').should('be.visible');
        cy.contains('th', 'Score').should('be.visible');
        cy.contains('th', 'Status').should('be.visible');
      }
    });
  });

  it('should have View Result and Review links', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').should('be.visible');
        cy.contains('Review').should('be.visible');
      }
    });
  });

  it('should navigate to result page from history', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').first().click();
        cy.url().should('include', '/result');
      }
    });
  });

  it('should navigate to review page from history', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('Review').first().click();
        cy.url().should('include', '/review');
      }
    });
  });

  it('should filter by subject', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        // Select a subject if available
        cy.get('select[name="subject"]').then(($select) => {
          if ($select.find('option').length > 1) {
            cy.get('select[name="subject"]').select(1);
            cy.contains('Apply Filters').click();
            cy.url().should('include', 'subject=');
          }
        });
      }
    });
  });

  it('should filter by status (pass/fail)', () => {
    cy.visit('/my-exams/history/');

    cy.get('select[name="status"]').select('pass');
    cy.contains('Apply Filters').click();
    cy.url().should('include', 'status=pass');
  });

  it('should sort by date ascending', () => {
    cy.visit('/my-exams/history/');

    cy.get('select[name="sort"]').select('date_asc');
    cy.contains('Apply Filters').click();
    cy.url().should('include', 'sort=date_asc');
  });

  it('should sort by score descending', () => {
    cy.visit('/my-exams/history/');

    cy.get('select[name="sort"]').select('score_desc');
    cy.contains('Apply Filters').click();
    cy.url().should('include', 'sort=score_desc');
  });

  it('should clear filters', () => {
    cy.visit('/my-exams/history/?status=pass&sort=score_desc');

    cy.contains('Clear Filters').click();
    cy.url().should('eq', Cypress.config().baseUrl + '/my-exams/history/');
  });

  it('should show results count', () => {
    cy.visit('/my-exams/history/');

    cy.contains('Showing').should('be.visible');
    cy.contains('results').should('be.visible');
  });

  it('should show pass/fail badges', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        // Should have pass or fail badges
        const hasStatus = $body.text().includes('Pass') || $body.text().includes('Fail');
        expect(hasStatus).to.be.true;
      }
    });
  });

  it('should show color-coded score badges', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        // Should have percentage badges
        cy.get('.rounded-full').should('have.length.at.least', 1);
      }
    });
  });

  it('should navigate back to exams list', () => {
    cy.visit('/my-exams/history/');

    cy.contains('Back to Exams').click();
    cy.url().should('include', '/my-exams');
    cy.url().should('not.include', '/history');
  });

  it('should show timed out indicator if applicable', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      // Check if there are any timed out exams
      if ($body.text().includes('Timed Out')) {
        cy.contains('Timed Out').should('be.visible');
      }
    });
  });

  it('should display date filter inputs', () => {
    cy.visit('/my-exams/history/');

    // Date inputs should be type="date"
    cy.get('input[name="date_from"]').should('have.attr', 'type', 'date');
    cy.get('input[name="date_to"]').should('have.attr', 'type', 'date');
  });

  it('should filter by date range', () => {
    cy.visit('/my-exams/history/');

    // Set a date range
    const today = new Date().toISOString().split('T')[0];
    cy.get('input[name="date_from"]').type('2020-01-01');
    cy.get('input[name="date_to"]').type(today);
    cy.contains('Apply Filters').click();

    cy.url().should('include', 'date_from=2020-01-01');
    cy.url().should('include', 'date_to=');
  });
});
