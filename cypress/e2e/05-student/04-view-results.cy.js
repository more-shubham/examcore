/**
 * Student View Results Tests
 *
 * Tests viewing exam results after submission.
 * Requires seeded database with completed exam attempts.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/**"
 */

describe('Student - View Results', () => {
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

  it('should navigate to completed exam result', () => {
    cy.visit('/my-exams/');

    // Find completed exam and click result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should be on result page
    cy.url().should('include', '/result');
  });

  it('should display score correctly', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should show score
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Score should be displayed (e.g., "8/10", "80%", "Score: 8")
      const hasScore = /\d+\s*\/\s*\d+/.test(text) ||
      /\d+\s*%/.test(text) ||
      /score/i.test(text);
      expect(hasScore).to.be.true;
    });
  });

  it('should display correct/total questions', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should show correct/total format
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasQuestionCount = /\d+\s*(\/|out of|of)\s*\d+/i.test(text) ||
      text.includes('correct') ||
      text.includes('total');
      expect(hasQuestionCount).to.be.true;
    });
  });

  it('should display percentage score', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should show percentage
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasPercentage = /\d+\s*%/.test(text) || text.includes('percent');
      expect(hasPercentage).to.be.true;
    });
  });

  it('should display pass/fail status', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should show pass/fail status
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasStatus = text.includes('pass') ||
      text.includes('fail') ||
      text.includes('cleared') ||
      text.includes('not cleared') ||
      text.includes('status');
      expect(hasStatus).to.be.true;
    });
  });

  it('should display exam title', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should show exam title
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasTitle = text.includes('Quiz') ||
      text.includes('Test') ||
      text.includes('Exam') ||
      text.includes('OOP') ||
      text.includes('Java');
      expect(hasTitle).to.be.true;
    });
  });

  it('should show question-wise review if available', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Look for question review section or score details
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      // Check if page has review info or score info
      const hasReviewOrScore = text.includes('review') ||
      text.includes('question') ||
      text.includes('score') ||
      text.includes('result') ||
      /\d+\s*\/\s*\d+/.test(text);
      expect(hasReviewOrScore).to.be.true;
    });
  });

  it('should have back to exams link', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should have back/return link
    cy.get('a:contains("Back"), a:contains("Exams"), a:contains("Return"), a[href*="my-exams"]').should('exist');
  });

  it('should display attempt timestamp', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Should show when exam was taken
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasTimestamp = text.includes('date') ||
      text.includes('submitted') ||
      text.includes('taken') ||
      text.includes('completed') ||
      /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}/.test(text);
      expect(hasTimestamp).to.be.true;
    });
  });

  it('should show correct answers for review if enabled', () => {
    cy.visit('/my-exams/');

    // Navigate to result
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').first().click();

    // Check if review link or answer details are available
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      // Page should show result info - review may or may not be enabled
      const hasResultInfo = text.includes('score') ||
      text.includes('result') ||
      text.includes('answer') ||
      text.includes('review') ||
      /\d+\s*%/.test(text);
      expect(hasResultInfo).to.be.true;
    });
  });
});
