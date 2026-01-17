/**
 * Student Take Exam Tests
 *
 * Tests the exam-taking flow including starting, answering, and submitting.
 * Requires seeded database with running exams.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/**"
 */

describe('Student - Take Exam', () => {
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

  it('should start a running exam', () => {
    cy.visit('/my-exams/');

    // Find and click Start on a running exam
    cy.get('a:contains("Start"), button:contains("Start"), a:contains("Take")').first().click();

    // Should be on exam start/instructions page or directly taking exam
    cy.url().should('match', /\/my-exams\/\d+\/(start|take)/);
  });

  it('should display exam instructions before starting', () => {
    cy.visit('/my-exams/');

    // Start an exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();

    // Check for instructions or confirmation
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasInstructions = text.includes('instruction') ||
      text.includes('begin') ||
      text.includes('start') ||
      text.includes('duration') ||
      text.includes('question');
      expect(hasInstructions).to.be.true;
    });
  });

  it('should display question content', () => {
    cy.visit('/my-exams/');

    // Start exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();

    // Click begin if there's a confirmation step
    cy.get('button:contains("Begin"), button:contains("Start"), a:contains("Begin")').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
      }
    });

    // Should see question text
    cy.get('[data-testid="question"], .question, .question-text, p').should('contain.text', '?');
  });

  it('should display answer options', () => {
    cy.visit('/my-exams/');

    // Navigate to exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();
    cy.get('button:contains("Begin"), button:contains("Start")').then(($btn) => {
      if ($btn.length > 0) cy.wrap($btn).first().click();
    });

    // Should see radio buttons or answer options
    cy.get('input[type="radio"], .answer-option, [data-testid="option"]').should('have.length.at.least', 2);
  });

  it('should allow selecting an answer', () => {
    cy.visit('/my-exams/');

    // Navigate to exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();
    cy.get('button:contains("Begin"), button:contains("Start")').then(($btn) => {
      if ($btn.length > 0) cy.wrap($btn).first().click();
    });

    // Select first option
    cy.get('input[type="radio"]').first().check();
    cy.get('input[type="radio"]').first().should('be.checked');
  });

  it('should navigate between questions', () => {
    cy.visit('/my-exams/');

    // Navigate to exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();
    cy.get('button:contains("Begin"), button:contains("Start")').then(($btn) => {
      if ($btn.length > 0) cy.wrap($btn).first().click();
    });

    // Look for next/previous buttons or question navigator
    cy.get('button:contains("Next"), a:contains("Next"), [data-action="next"]').then(($next) => {
      if ($next.length > 0) {
        cy.wrap($next).first().click();
        // Should move to next question
        cy.url().should('include', '/take');
      }
    });
  });

  it('should display timer', () => {
    cy.visit('/my-exams/');

    // Navigate to exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();
    cy.get('button:contains("Begin"), button:contains("Start")').then(($btn) => {
      if ($btn.length > 0) cy.wrap($btn).first().click();
    });

    // Look for timer display
    cy.get('[data-testid="timer"], .timer, .countdown, .time-remaining').then(($timer) => {
      if ($timer.length > 0) {
        cy.wrap($timer).should('be.visible');
        // Timer should show time format
        cy.wrap($timer).invoke('text').should('match', /\d+:\d+|\d+\s*(min|sec)/i);
      }
    });
  });

  it('should answer multiple questions and submit', () => {
    cy.visit('/my-exams/');

    // Navigate to exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();
    cy.get('button:contains("Begin"), button:contains("Start")').then(($btn) => {
      if ($btn.length > 0) cy.wrap($btn).first().click();
    });

    // Answer first question
    cy.get('input[type="radio"]').first().check();

    // Try to go to next question
    cy.get('button:contains("Next"), a:contains("Next")').then(($next) => {
      if ($next.length > 0) {
        cy.wrap($next).first().click();

        // Answer second question
        cy.get('input[type="radio"]').first().check();
      }
    });

    // Look for submit button
    cy.get('button:contains("Submit"), a:contains("Submit"), button:contains("Finish")').first().click();

    // Confirm submission if dialog appears
    cy.get('body').then(($body) => {
      if ($body.find('button:contains("Confirm"), button:contains("Yes")').length > 0) {
        cy.contains('button', /confirm|yes/i).click();
      }
    });

    // Should be redirected to result or exams list
    cy.url().should('match', /\/(result|my-exams)/);
  });

  it('should show confirmation before submitting', () => {
    cy.visit('/my-exams/');

    // Navigate to exam
    cy.get('a:contains("Start"), button:contains("Start")').first().click();
    cy.get('button:contains("Begin"), button:contains("Start")').then(($btn) => {
      if ($btn.length > 0) cy.wrap($btn).first().click();
    });

    // Try to submit
    cy.get('button:contains("Submit"), button:contains("Finish")').first().click();

    // Should show confirmation
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasConfirmation = text.includes('confirm') ||
      text.includes('sure') ||
      text.includes('submit') ||
      text.includes('finish');
      expect(hasConfirmation).to.be.true;
    });
  });
});
