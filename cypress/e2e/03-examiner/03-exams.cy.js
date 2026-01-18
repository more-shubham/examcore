/**
 * Examiner Exam Management Tests
 *
 * Tests exam creation, question assignment, and publishing.
 * Requires seeded database with subjects and questions.
 *
 * Run: npx cypress run --spec "cypress/e2e/03-examiner/**"
 */

describe('Examiner - Exam Management', () => {
  const testExam = {
    title: 'Data Structures Weekly Quiz',
    description: 'Weekly assessment covering stacks and queues',
    questionCount: 5,
  };

  // Helper to format datetime for datetime-local input
  const formatDateTime = (date) => {
    return date.toISOString().slice(0, 16);
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

  it('should navigate to exams page', () => {
    cy.visit('/exams/');
    cy.url().should('include', '/exams');
    cy.contains('Exams').should('be.visible');
  });

  it('should display existing exams from seed data', () => {
    cy.visit('/exams/');

    // Should show exam count
    cy.contains(/\d+ exam/).should('be.visible');

    // Should show exams in cards
    cy.get('.card').should('have.length.at.least', 1);

    // Should show some seeded exams
    cy.contains(/Unit Test|Mid-Term|Quiz/).should('be.visible');
  });

  it('should create new exam with random question selection', () => {
    cy.visit('/exams/add/');

    // Fill exam details
    cy.get('input[name="title"]').type(testExam.title);
    cy.get('textarea[name="description"]').type(testExam.description);

    // Select subject (Data Structures - DSU)
    cy.get('select[name="subject"]').select(1); // First available subject

    // Set start and end time
    const now = new Date();
    const startTime = new Date(now.getTime() + 24 * 60 * 60 * 1000); // Tomorrow
    const endTime = new Date(startTime.getTime() + 2 * 60 * 60 * 1000); // +2 hours

    cy.get('input[name="start_time"]').type(formatDateTime(startTime));
    cy.get('input[name="end_time"]').type(formatDateTime(endTime));

    // Enable random questions (should be checkbox)
    cy.get('input[name="use_random_questions"]').check();

    // Set number of random questions
    cy.get('input[name="random_question_count"]').clear().type(testExam.questionCount.toString());

    // Set status to draft
    cy.get('select[name="status"]').select('draft');

    // Submit form (click "Create Exam" button)
    cy.contains('button', 'Create Exam').click();

    // Verify redirect to exam list
    cy.url().should('include', '/exams');
    cy.url().should('not.include', '/add');

    // Verify exam appears in list
    cy.contains(testExam.title).should('be.visible');
  });

  it('should view exam details', () => {
    cy.visit('/exams/');

    // Click on the test exam title to view details
    cy.contains(testExam.title).click();

    // Should show exam details page
    cy.url().should('match', /\/exams\/\d+\/?$/);
    cy.contains(testExam.title).should('be.visible');
    cy.contains('Exam Details').should('be.visible');
    cy.contains('Start Time').should('be.visible');
    cy.contains('End Time').should('be.visible');
    cy.contains('Duration').should('be.visible');
    cy.contains('Questions').should('be.visible');
  });

  it('should show random selection info on exam detail', () => {
    cy.visit('/exams/');

    // Go to our test exam
    cy.contains(testExam.title).click();

    // Should show random selection badge
    cy.contains('Random Selection').should('be.visible');
    cy.contains(`${testExam.questionCount} questions will be randomly selected`).should('be.visible');
  });

  it('should edit exam details', () => {
    cy.visit('/exams/');

    // Find and click edit for the exam (using the card's Edit link)
    cy.contains(testExam.title)
      .parents('.card')
      .find('a:contains("Edit")')
      .click();

    // Verify we're on edit page
    cy.url().should('include', '/edit');

    // Update title
    cy.get('input[name="title"]').clear().type('DSU Weekly Quiz (Updated)');

    // Submit form (click "Update Exam" button)
    cy.contains('button', 'Update Exam').click();

    // Verify redirect and updated title
    cy.url().should('include', '/exams');
    cy.contains('DSU Weekly Quiz (Updated)').should('be.visible');
  });

  it('should filter exams by status', () => {
    cy.visit('/exams/');

    // Filter by draft status
    cy.get('select[name="status"]').select('draft');

    // URL should have status parameter
    cy.url().should('include', 'status=draft');

    // Should show draft exams
    cy.contains('Draft').should('be.visible');
  });

  it('should filter exams by subject', () => {
    cy.visit('/exams/');

    // Select first subject from filter
    cy.get('select[name="subject"]').select(1);

    // URL should have subject parameter
    cy.url().should('include', 'subject=');

    // Should still show exams
    cy.get('.card').should('have.length.at.least', 1);
  });

  it('should clear filters', () => {
    cy.visit('/exams/?subject=1&status=draft');

    // Click clear filters
    cy.contains('Clear Filters').click();

    // URL should be clean
    cy.url().should('eq', Cypress.config().baseUrl + '/exams/');
  });

  it('should navigate to edit from exam detail page', () => {
    cy.visit('/exams/');

    // Go to exam detail
    cy.contains('DSU Weekly Quiz (Updated)').click();

    // Click Edit button
    cy.get('a:contains("Edit")').first().click();

    // Should be on edit page
    cy.url().should('include', '/edit');
    cy.get('input[name="title"]').should('have.value', 'DSU Weekly Quiz (Updated)');
  });

  it('should delete exam', () => {
    cy.visit('/exams/');

    // Find our test exam and click delete
    cy.contains('DSU Weekly Quiz (Updated)')
      .parents('.card')
      .find('a:contains("Delete")')
      .click();

    // Confirm deletion on delete page
    cy.url().should('include', '/delete');
    cy.contains('button', 'Delete Exam').click();

    // Verify redirect to list
    cy.url().should('include', '/exams');
    cy.url().should('not.include', '/delete');

    // Verify exam is removed
    cy.contains('DSU Weekly Quiz (Updated)').should('not.exist');
  });

  it('should show validation error for invalid exam data', () => {
    cy.visit('/exams/add/');

    // Submit without required fields
    cy.contains('button', 'Create Exam').click();

    // Should stay on the add page
    cy.url().should('include', '/exams/add');

    // Required field validation should trigger (browser validation or Django errors)
    cy.get(':invalid, .field-error').should('exist');
  });

  it('should show Create Exam button in list view', () => {
    cy.visit('/exams/');

    // Verify Create Exam button exists
    cy.contains('Create Exam').should('be.visible');
    cy.contains('Create Exam').should('have.attr', 'href').and('include', '/exams/add');
  });

  it('should create exam with manual question selection', () => {
    cy.visit('/exams/add/');

    // Fill exam details
    cy.get('input[name="title"]').type('Manual Selection Test Exam');
    cy.get('textarea[name="description"]').type('Testing manual question selection');

    // Select subject
    cy.get('select[name="subject"]').select(1);

    // Set times
    const now = new Date();
    const startTime = new Date(now.getTime() + 48 * 60 * 60 * 1000); // Day after tomorrow
    const endTime = new Date(startTime.getTime() + 1 * 60 * 60 * 1000); // +1 hour

    cy.get('input[name="start_time"]').type(formatDateTime(startTime));
    cy.get('input[name="end_time"]').type(formatDateTime(endTime));

    // Uncheck random questions (it's checked by default) for manual selection
    cy.get('input[name="use_random_questions"]').uncheck();

    // Set status to draft
    cy.get('select[name="status"]').select('draft');

    // Submit form (click "Create Exam" button)
    cy.contains('button', 'Create Exam').click();

    // Verify redirect and exam created
    cy.url().should('include', '/exams');
    cy.contains('Manual Selection Test Exam').should('be.visible');
  });

  it('should show Manage Questions button for manual selection exams', () => {
    cy.visit('/exams/');

    // Go to the manual selection exam
    cy.contains('Manual Selection Test Exam').click();

    // Should show Manual Selection badge
    cy.contains('Manual Selection').should('be.visible');

    // Should show Manage Questions button
    cy.contains('Manage Questions').should('be.visible');
  });

  it('should cleanup test exams', () => {
    cy.visit('/exams/');

    // Delete the manual selection test exam
    cy.contains('Manual Selection Test Exam')
      .parents('.card')
      .find('a:contains("Delete")')
      .click();

    cy.contains('button', 'Delete Exam').click();

    // Verify deleted
    cy.contains('Manual Selection Test Exam').should('not.exist');
  });
});
