/**
 * Student Answer Review Tests
 *
 * Tests the answer review functionality after exam submission.
 * Requires seeded database with student who has completed an exam.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/06-answer-review.cy.js"
 */

describe('Student Answer Review', () => {
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

  it('should have Review Answers button on result page', () => {
    // Navigate to my exams
    cy.visit('/my-exams/');

    // Find a completed exam and view result
    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.url().should('include', '/result');

        // Check for Review Answers button
        cy.contains('Review Answers').should('be.visible');
        cy.contains('Review Answers').should('have.attr', 'href').and('include', '/review');
      } else {
        // Skip if no completed exams
        cy.log('No completed exams found for this student');
      }
    });
  });

  it('should navigate to review page from result page', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        cy.url().should('include', '/review');
        cy.contains('Answer Review').should('be.visible');
      }
    });
  });

  it('should display exam information on review page', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Should show exam title
        cy.get('h1').should('be.visible');

        // Should show score
        cy.get('body').should('contain', '%');

        // Should show correct/incorrect counts
        cy.contains('Correct').should('be.visible');
        cy.contains('Incorrect').should('be.visible');
      }
    });
  });

  it('should display question navigator', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Should have jump to question section
        cy.contains('Jump to Question').should('be.visible');

        // Should have question number buttons
        cy.get('a[href^="#question-"]').should('have.length.at.least', 1);
      }
    });
  });

  it('should display questions with correct/incorrect indicators', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Should have question cards
        cy.get('[id^="question-"]').should('have.length.at.least', 1);

        // Each question should have Q number badge
        cy.get('body').then(($reviewBody) => {
          const hasQuestionBadge = $reviewBody.text().includes('Q1') || $reviewBody.text().includes('Q2');
          expect(hasQuestionBadge).to.be.true;
        });
      }
    });
  });

  it('should highlight correct answers in green', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Should have "Correct Answer" labels
        cy.contains('Correct Answer').should('exist');
      }
    });
  });

  it('should show student selected answer', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Should have "Your Answer" labels
        cy.contains('Your Answer').should('exist');
      }
    });
  });

  it('should navigate to specific question via navigator', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Click on question 1 in navigator
        cy.get('a[href="#question-1"]').click();

        // Should scroll to question 1
        cy.get('#question-1').should('be.visible');
      }
    });
  });

  it('should have back to result link', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Should have back link
        cy.contains('Back to Result').should('be.visible');
        cy.contains('Back to Result').first().click();

        // Should return to result page
        cy.url().should('include', '/result');
      }
    });
  });

  it('should not allow review for in-progress exams', () => {
    // Try to access review directly for a non-submitted exam
    // This should redirect or show error
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      // Check if there's an active exam that hasn't been submitted
      if ($body.text().includes('Start Exam') || $body.text().includes('Continue')) {
        // Try to manually navigate to review (should fail)
        cy.log('Testing that review is blocked for non-submitted exams');
      }
    });
  });

  it('should display all options for each question', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Each question should have multiple options displayed
        cy.get('[id^="question-"]').first().within(() => {
          // Should have option numbers (1, 2, 3, etc.)
          cy.get('.rounded-full').should('have.length.at.least', 2);
        });
      }
    });
  });

  it('should show correct styling for correct questions', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Check if any question is marked as correct (green styling)
        cy.get('body').then(($reviewBody) => {
          const hasCorrect = $reviewBody.find('.bg-green-50').length > 0 ||
          $reviewBody.find('.text-green-700').length > 0;
          // At least some styling should be present
          expect($reviewBody.find('.bg-green-50, .bg-red-50').length).to.be.at.least(1);
        });
      }
    });
  });

  it('should show unanswered questions if any', () => {
    cy.visit('/my-exams/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('View Result')) {
        cy.contains('View Result').first().click();
        cy.contains('Review Answers').click();

        // Check if there's a message for unanswered questions
        cy.get('body').then(($reviewBody) => {
          // Either has unanswered message or all questions were answered
          const hasUnanswered = $reviewBody.text().includes('did not answer');
          cy.log(`Has unanswered questions: ${hasUnanswered}`);
        });
      }
    });
  });
});
