/**
 * Examiner Question Management Tests
 *
 * Tests CRUD operations for questions by examiners.
 * Requires seeded database with subjects.
 *
 * Run: npx cypress run --spec "cypress/e2e/03-examiner/**"
 */

describe('Examiner - Question Management', () => {
  const testQuestion = {
    text: 'What is the time complexity of inserting at the end of a singly linked list without tail pointer?',
    optionA: 'O(1)',
    optionB: 'O(n)',
    optionC: 'O(log n)',
    optionD: 'O(n²)',
    correctOption: 'b',
  };

  before(() => {
    // Seed database with test data
    cy.task('seedDatabase');
  });

  beforeEach(() => {
    // Login as examiner
    cy.fixture('credentials').then((creds) => {
      cy.visit('/');
      cy.get('input[name="username"]').type(creds.examiner.email);
      cy.get('input[name="password"]').type(creds.examiner.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });
  });

  it('should navigate to question bank', () => {
    cy.visit('/questions/');
    cy.url().should('include', '/questions');
    cy.contains(/question/i).should('be.visible');
  });

  it('should display existing questions from seed data', () => {
    cy.visit('/questions/');

    // Should show questions from seed data
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Look for any of the seeded questions
      const hasQuestions = text.includes('LIFO') || text.includes('binary search') || text.includes('SQL');
      expect(hasQuestions).to.be.true;
    });
  });

  it('should create new MCQ question', () => {
    cy.visit('/questions/add/');

    // Fill question text
    cy.get('textarea[name="question_text"], textarea[name="text"]').type(testQuestion.text);

    // Select subject (DSU - Data Structures)
    cy.get('select[name="subject"]').select(/DSU|Data Structures/i);

    // Fill options
    cy.get('input[name="option_a"], input[name="option_1"]').type(testQuestion.optionA);
    cy.get('input[name="option_b"], input[name="option_2"]').type(testQuestion.optionB);
    cy.get('input[name="option_c"], input[name="option_3"]').type(testQuestion.optionC);
    cy.get('input[name="option_d"], input[name="option_4"]').type(testQuestion.optionD);

    // Select correct answer
    cy.get(`input[name="correct_option"][value="${testQuestion.correctOption}"], input[name="correct_answer"][value="b"], input[name="correct_option"][value="2"]`).check();

    // Submit form
    cy.get('button[type="submit"]').click();

    // Verify redirect or success message
    cy.url().should('include', '/questions');
    cy.contains(/linked list|time complexity/i).should('be.visible');
  });

  it('should verify question appears in list', () => {
    cy.visit('/questions/');

    // Search or scroll to find our question
    cy.contains(/linked list/i).should('be.visible');
  });

  it('should edit question text', () => {
    cy.visit('/questions/');

    // Find and click edit for a question
    cy.contains(/linked list/i)
      .parents('tr, [data-testid="question-row"], .question-item')
      .find('a:contains("Edit"), button:contains("Edit"), [href*="edit"]')
      .first()
      .click();

    // Update question text
    cy.get('textarea[name="question_text"], textarea[name="text"]')
      .clear()
      .type('What is the time complexity of insertion at the end of a linked list (without tail)?');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Verify update
    cy.contains(/insertion at the end/i).should('be.visible');
  });

  it('should filter questions by subject', () => {
    cy.visit('/questions/');

    // Look for filter/select dropdown
    cy.get('select[name="subject"], select[name="filter"], [data-testid="subject-filter"]').then(($filter) => {
      if ($filter.length > 0) {
        cy.wrap($filter).select(/DSU|Data Structures/i);

        // Should only show DSU questions
        cy.get('body').then(($body) => {
          const text = $body.text();
          const hasDSUQuestions = text.includes('LIFO') || text.includes('linked list') || text.includes('stack');
          expect(hasDSUQuestions).to.be.true;
        });
      }
    });
  });

  it('should delete question', () => {
    cy.visit('/questions/');

    // Count questions before delete
    cy.get('tr, [data-testid="question-row"], .question-item').then(($rows) => {
      const initialCount = $rows.length;

      // Find and click delete for the test question
      cy.contains(/linked list/i)
        .parents('tr, [data-testid="question-row"], .question-item')
        .find('button:contains("Delete"), a:contains("Delete"), [data-action="delete"]')
        .first()
        .click();

      // Confirm deletion if dialog appears
      cy.get('body').then(($body) => {
        if ($body.find('button:contains("Confirm"), button:contains("Yes")').length > 0) {
          cy.contains('button', /confirm|yes/i).click();
        }
      });

      // Verify question is removed
      cy.contains(/linked list/i).should('not.exist');
    });
  });

  it('should show validation error for incomplete question', () => {
    cy.visit('/questions/add/');

    // Submit without filling required fields
    cy.get('button[type="submit"]').click();

    // Should show validation error or stay on page
    cy.url().should('include', '/questions');
    cy.get('input:invalid, textarea:invalid, .error, .invalid-feedback').should('exist');
  });
});
