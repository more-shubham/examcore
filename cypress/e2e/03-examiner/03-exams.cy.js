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
    duration: 60,
    passingPercentage: 40,
    questionCount: 5,
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
    cy.contains(/exam/i).should('be.visible');
  });

  it('should display existing exams from seed data', () => {
    cy.visit('/exams/');

    // Should show exams from seed data
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasExams = text.includes('Unit Test') || text.includes('Mid-Term') || text.includes('Quiz');
      expect(hasExams).to.be.true;
    });
  });

  it('should create new exam with random question selection', () => {
    cy.visit('/exams/add/');

    // Fill exam details
    cy.get('input[name="title"]').type(testExam.title);
    cy.get('textarea[name="description"]').type(testExam.description);

    // Select subject (DSU - Data Structures)
    cy.get('select[name="subject"]').select(/DSU|Data Structures/i);

    // Set duration
    cy.get('input[name="duration"]').clear().type(testExam.duration.toString());

    // Set passing percentage if field exists
    cy.get('input[name="passing_percentage"], input[name="pass_percentage"]').then(($input) => {
      if ($input.length > 0) {
        cy.wrap($input).clear().type(testExam.passingPercentage.toString());
      }
    });

    // Set start and end time (use datetime-local or separate fields)
    const now = new Date();
    const startTime = new Date(now.getTime() + 24 * 60 * 60 * 1000); // Tomorrow
    const endTime = new Date(startTime.getTime() + 2 * 60 * 60 * 1000); // +2 hours

    cy.get('input[name="start_time"], input[name="start_datetime"]').then(($input) => {
      if ($input.attr('type') === 'datetime-local') {
        cy.wrap($input).type(startTime.toISOString().slice(0, 16));
      }
    });

    cy.get('input[name="end_time"], input[name="end_datetime"]').then(($input) => {
      if ($input.attr('type') === 'datetime-local') {
        cy.wrap($input).type(endTime.toISOString().slice(0, 16));
      }
    });

    // Enable random questions
    cy.get('input[name="use_random_questions"], input[type="checkbox"][name*="random"]').then(($checkbox) => {
      if ($checkbox.length > 0) {
        cy.wrap($checkbox).check();
        cy.get('input[name="random_question_count"], input[name="question_count"]').clear().type(testExam.questionCount.toString());
      }
    });

    // Submit form
    cy.get('button[type="submit"]').click();

    // Verify redirect or success
    cy.url().should('include', '/exams');
    cy.contains(testExam.title).should('be.visible');
  });

  it('should view exam details', () => {
    cy.visit('/exams/');

    // Click on the test exam
    cy.contains(testExam.title).click();

    // Should show exam details
    cy.contains(testExam.title).should('be.visible');
    cy.contains(/description|detail/i).should('be.visible');
  });

  it('should add questions manually to exam', () => {
    cy.visit('/exams/');

    // Find the exam and go to questions management
    cy.contains(testExam.title)
      .parents('tr, [data-testid="exam-row"], .exam-item')
      .find('a:contains("Questions"), a[href*="questions"], button:contains("Questions")')
      .first()
      .click();

    // Should be on exam questions page
    cy.url().should('include', '/questions');

    // Look for add/select button
    cy.get('button:contains("Add"), button:contains("Select"), a:contains("Add")').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();

        // Select some questions
        cy.get('input[type="checkbox"]').then(($checkboxes) => {
          // Select first 5 questions
          for (let i = 0; i < Math.min(5, $checkboxes.length); i++) {
            cy.wrap($checkboxes[i]).check();
          }
        });

        // Confirm selection
        cy.get('button[type="submit"], button:contains("Save"), button:contains("Add")').click();
      }
    });
  });

  it('should edit exam details', () => {
    cy.visit('/exams/');

    // Find and click edit for the exam
    cy.contains(testExam.title)
      .parents('tr, [data-testid="exam-row"], .exam-item')
      .find('a:contains("Edit"), button:contains("Edit"), [href*="edit"]')
      .first()
      .click();

    // Update title
    cy.get('input[name="title"]').clear().type('DSU Weekly Quiz (Updated)');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Verify update
    cy.contains('Updated').should('be.visible');
  });

  it('should publish exam', () => {
    cy.visit('/exams/');

    // Find the exam
    cy.contains(/Weekly Quiz/i)
      .parents('tr, [data-testid="exam-row"], .exam-item')
      .within(() => {
        // Look for publish button or status toggle
        cy.get('button:contains("Publish"), a:contains("Publish"), select[name="status"], [data-action="publish"]').then(($publish) => {
          if ($publish.is('select')) {
            cy.wrap($publish).select('published');
          } else {
            cy.wrap($publish).click();
          }
        });
      });

    // Verify status change
    cy.contains(/published|active/i).should('be.visible');
  });

  it('should show exam questions list', () => {
    cy.visit('/exams/');

    // Navigate to exam questions
    cy.contains(/Weekly Quiz/i)
      .parents('tr, [data-testid="exam-row"], .exam-item')
      .find('a:contains("Questions"), a[href*="questions"]')
      .first()
      .click();

    // Should show questions assigned to exam
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasQuestions = text.includes('question') || text.includes('Q1') || text.includes('#1');
      expect(hasQuestions).to.be.true;
    });
  });

  it('should show validation error for invalid exam data', () => {
    cy.visit('/exams/add/');

    // Submit without required fields
    cy.get('button[type="submit"]').click();

    // Should show validation errors
    cy.get('input:invalid, .error, .invalid-feedback').should('exist');
  });
});
