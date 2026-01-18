/**
 * Teacher View Student Results Tests
 *
 * Tests teacher access to student exam results.
 * Teachers should be able to view results for exams in their assigned subjects.
 *
 * FEATURE STATUS: IMPLEMENTED
 * Teachers can view results from their assigned subjects.
 *
 * Run: npx cypress run --spec "cypress/e2e/04-teacher/04-view-results.cy.js"
 */

describe('Teacher - View Student Results', () => {
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

  it('should have Results link on dashboard', () => {
    // Teacher should see Results link in Quick Actions
    cy.get('a[href*="results"]').should('exist');
  });

  it('should access results page', () => {
    cy.visit('/results/');
    cy.url().should('include', '/results');
    // Should not redirect away
    cy.url().should('not.include', '/dashboard');
  });

  it('should display list of exam attempts', () => {
    cy.visit('/results/');
    // Should show student attempts in table
    cy.get('table tbody tr').should('have.length.at.least', 1);
  });

  it('should show student name for each attempt', () => {
    cy.visit('/results/');
    // Each result should show student name
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Check for known student names from seed data (DBMS exam students)
      const hasStudentName = text.includes('Anita') ||
      text.includes('Sachin') ||
      text.includes('Deepa') ||
      text.includes('Rohit') ||
      text.includes('Kadam') ||
      text.includes('Pawar');
      expect(hasStudentName).to.be.true;
    });
  });

  it('should show exam title for each attempt', () => {
    cy.visit('/results/');
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasExamTitle = text.includes('Quiz') ||
      text.includes('Test') ||
      text.includes('Exam');
      expect(hasExamTitle).to.be.true;
    });
  });

  it('should show score for each attempt', () => {
    cy.visit('/results/');
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Should show scores like "8/10" or "80%"
      const hasScore = /\d+\s*\/\s*\d+/.test(text) || /\d+\s*%/.test(text);
      expect(hasScore).to.be.true;
    });
  });

  it('should show pass/fail status', () => {
    cy.visit('/results/');
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasStatus = text.includes('pass') ||
      text.includes('fail') ||
      text.includes('cleared');
      expect(hasStatus).to.be.true;
    });
  });

  it('should filter results by exam', () => {
    cy.visit('/results/');
    cy.get('select[name="exam"]').then(($select) => {
      if ($select.length > 0) {
        cy.wrap($select).select(1);
        cy.url().should('include', 'exam=');
      }
    });
  });

  it('should filter results by class', () => {
    cy.visit('/results/');
    cy.get('select[name="class"]').then(($select) => {
      if ($select.length > 0) {
        cy.wrap($select).select(1);
        cy.url().should('include', 'class=');
      }
    });
  });

  it('should view detailed result for a student', () => {
    cy.visit('/results/');
    // Click to view detailed result
    cy.contains('a', 'View Details').first().click();
    // Should show detailed view
    cy.url().should('match', /\/results\/\d+/);
  });

  it('should show question-wise breakdown in detail view', () => {
    cy.visit('/results/');
    cy.contains('a', 'View Details').first().click();
    // Should show each question and student's answer
    cy.contains('Question-wise Breakdown').should('exist');
  });

  it('should NOT allow editing results', () => {
    cy.visit('/results/');
    // Teachers can view but not modify
    cy.get('button:contains("Edit"), a:contains("Edit Score")').should('not.exist');
  });

  it('should show submission timestamp', () => {
    cy.visit('/results/');
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasTimestamp = text.includes('submitted') ||
      text.includes('date') ||
      text.includes('completed') ||
      /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}/.test(text);
      expect(hasTimestamp).to.be.true;
    });
  });
});
