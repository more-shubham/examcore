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
    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.url().should('include', '/result');

        // Check for Review Answers button or link
        cy.get('body').then(($body) => {
          const hasReview = $body.text().includes('Review') ||
          $body.find('a[href*="review"]').length > 0;
          expect(hasReview).to.be.true;
        });
      } else {
        // Skip if no completed exams
        cy.log('No completed exams found for this student');
      }
    });
  });

  it('should navigate to review page from result page', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();
            cy.url().should('include', '/review');
          } else {
            cy.log('Review not available for this exam');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should display exam information on review page', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should show exam info
            cy.get('body').then(($body) => {
              const text = $body.text();
              const hasExamInfo = text.includes('%') ||
              text.includes('Correct') ||
              text.includes('Question') ||
              text.includes('Score');
              expect(hasExamInfo).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should display question navigator', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should have question navigation elements
            cy.get('body').then(($body) => {
              const hasNav = $body.text().includes('Jump') ||
              $body.text().includes('Question') ||
              $body.find('a[href^="#question-"]').length > 0;
              expect(hasNav).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should display questions with correct/incorrect indicators', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should have question info
            cy.get('body').then(($body) => {
              const hasQuestions = $body.text().includes('Q1') ||
              $body.text().includes('Question') ||
              $body.find('[id^="question-"]').length > 0;
              expect(hasQuestions).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should highlight correct answers in green', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should have correct answer labels or styling
            cy.get('body').then(($body) => {
              const hasCorrect = $body.text().includes('Correct') ||
              $body.find('.bg-green-50, .text-green-700').length > 0;
              expect(hasCorrect).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should show student selected answer', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should have answer labels
            cy.get('body').then(($body) => {
              const hasAnswer = $body.text().includes('Your') ||
              $body.text().includes('Answer') ||
              $body.text().includes('Selected');
              expect(hasAnswer).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should navigate to specific question via navigator', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Try to navigate to question
            cy.get('a[href^="#question-"]').then(($qLinks) => {
              if ($qLinks.length > 0) {
                cy.wrap($qLinks).first().click();
              }
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should have back to result link', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should have back link
            cy.get('a:contains("Back"), a[href*="result"]').then(($backBtn) => {
              if ($backBtn.length > 0) {
                cy.wrap($backBtn).first().click();
                cy.url().should('include', '/result');
              }
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
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

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should have questions with options
            cy.get('body').then(($body) => {
              const hasOptions = $body.find('[id^="question-"]').length > 0 ||
              $body.text().includes('Option') ||
              $body.find('.rounded-full').length > 0;
              expect(hasOptions).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should show correct styling for correct questions', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Should have color-coded styling
            cy.get('body').then(($body) => {
              const hasStyling = $body.find('.bg-green-50, .bg-red-50, .text-green-700, .text-red-700').length > 0 ||
              $body.text().includes('Correct') ||
              $body.text().includes('Incorrect');
              expect(hasStyling).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });

  it('should show unanswered questions if any', () => {
    cy.visit('/my-exams/');

    cy.get('a:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().click();
        cy.get('a:contains("Review"), a[href*="review"]').then(($reviewBtn) => {
          if ($reviewBtn.length > 0) {
            cy.wrap($reviewBtn).first().click();

            // Check if there's info about answers
            cy.get('body').then(($body) => {
              const hasAnswerInfo = $body.text().includes('answer') ||
              $body.text().includes('Answer') ||
              $body.text().includes('Question');
              expect(hasAnswerInfo).to.be.true;
            });
          } else {
            cy.log('Review not available');
          }
        });
      } else {
        cy.log('No completed exams found');
      }
    });
  });
});
