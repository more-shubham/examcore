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
    options: ['O(1)', 'O(n)', 'O(log n)', 'O(n²)'],
    correctOptionIndex: 1, // O(n) is correct (0-indexed)
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
    cy.contains('Question Bank').should('be.visible');
  });

  it('should display existing questions from seed data', () => {
    cy.visit('/questions/');

    // Should show question count
    cy.contains(/\d+ question/).should('be.visible');

    // Should show questions in cards
    cy.get('.card').should('have.length.at.least', 1);
  });

  it('should create new MCQ question', () => {
    cy.visit('/questions/add/');

    // Select class first (CO - 3rd Semester has DSU)
    cy.get('select[name="assigned_class"]').select('CO - 3rd Semester');

    // Wait for subject dropdown to populate, then select DSU
    cy.get('select[name="subject"]').should('not.be.disabled');
    cy.wait(500); // Wait for JS to populate subjects
    cy.get('select[name="subject"]').select('Data Structures (DSU)');

    // Fill question text
    cy.get('textarea[name="question_text"]').type(testQuestion.text);

    // Fill the 4 option fields (they start with options-0-text, options-1-text, etc.)
    testQuestion.options.forEach((option, index) => {
      cy.get(`input[name="options-${index}-text"]`).clear().type(option);
    });

    // Select correct answer (radio button with value = index)
    cy.get(`input[name="correct_answer"][value="${testQuestion.correctOptionIndex}"]`).check();

    // Submit form (click the "Add Question" button specifically)
    cy.contains('button', 'Add Question').click();

    // Verify redirect to question list
    cy.url().should('include', '/questions');
    cy.url().should('not.include', '/add');

    // Verify question appears in list
    cy.contains('linked list').should('be.visible');
  });

  it('should verify created question appears in list', () => {
    cy.visit('/questions/');

    // Search for our question
    cy.get('input[name="search"]').type('linked list');
    cy.contains('button', 'Search').click();

    // Verify question is found
    cy.contains('linked list').should('be.visible');
    cy.contains('O(n)').should('be.visible');
  });

  it('should edit question text', () => {
    cy.visit('/questions/');

    // Search for our question
    cy.get('input[name="search"]').type('linked list');
    cy.contains('button', 'Search').click();

    // Click edit on the question
    cy.contains('linked list')
      .parents('.card')
      .find('a:contains("Edit")')
      .click();

    // Verify we're on edit page
    cy.url().should('include', '/edit');

    // Update question text
    cy.get('textarea[name="question_text"]')
      .clear()
      .type('What is the time complexity of insertion at the END of a singly linked list (without tail pointer)?');

    // Submit form (click "Update Question" button)
    cy.contains('button', 'Update Question').click();

    // Verify redirect and updated text
    cy.url().should('include', '/questions');
    cy.contains('END of a singly linked list').should('be.visible');
  });

  it('should filter questions by subject', () => {
    cy.visit('/questions/');

    // Select DSU subject from filter
    cy.get('select[name="subject"]').select(1); // First subject option after "All"

    // Verify filter applied - URL should have subject parameter
    cy.url().should('include', 'subject=');

    // Should still show questions
    cy.get('.card').should('have.length.at.least', 1);
  });

  it('should search questions by text', () => {
    cy.visit('/questions/');

    // Search for specific text
    cy.get('input[name="search"]').type('LIFO');
    cy.contains('button', 'Search').click();

    // Should show matching questions
    cy.contains('LIFO').should('be.visible');
  });

  it('should clear filters', () => {
    cy.visit('/questions/?subject=1&search=test');

    // Click clear filters
    cy.contains('Clear Filters').click();

    // URL should be clean
    cy.url().should('eq', Cypress.config().baseUrl + '/questions/');
  });

  it('should delete question', () => {
    cy.visit('/questions/');

    // Search for our test question
    cy.get('input[name="search"]').type('END of a singly linked list');
    cy.contains('button', 'Search').click();

    // Click delete on the question
    cy.contains('END of a singly linked list')
      .parents('.card')
      .find('a:contains("Delete")')
      .click();

    // Confirm deletion on delete page
    cy.url().should('include', '/delete');
    cy.contains('button', 'Delete Question').click();

    // Verify redirect to list
    cy.url().should('include', '/questions');
    cy.url().should('not.include', '/delete');

    // Verify question is removed
    cy.contains('END of a singly linked list').should('not.exist');
  });

  it('should show validation error for incomplete question', () => {
    cy.visit('/questions/add/');

    // Submit without filling required fields
    cy.contains('button', 'Add Question').click();

    // Should stay on the add page with errors
    cy.url().should('include', '/questions/add');

    // Required field validation should show (browser validation or Django errors)
    cy.get(':invalid, .field-error').should('exist');
  });

  it('should show Add Question button in list view', () => {
    cy.visit('/questions/');

    // Verify Add Question button exists
    cy.contains('Add Question').should('be.visible');
    cy.contains('Add Question').should('have.attr', 'href').and('include', '/questions/add');
  });
});
