/**
 * Student Result PDF Export Tests
 *
 * Tests the PDF download functionality on exam result pages.
 * Requires seeded database with student who has completed exams.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/10-result-pdf.cy.js"
 */

describe('Student Result PDF Export', () => {
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

  it('should have Download PDF button on result page', () => {
    // Navigate to exam history to find a completed exam
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        // Click View Result on first completed exam
        cy.contains('View Result').first().click();
        cy.url().should('include', '/result');

        // Check for Download PDF button
        cy.contains('Download PDF').should('be.visible');
      }
    });
  });

  it('should have Download PDF button with correct link', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').first().click();
        cy.url().should('include', '/result');

        // Check that Download PDF link points to PDF endpoint
        cy.contains('Download PDF')
          .should('have.attr', 'href')
          .and('include', '/result/pdf/');
      }
    });
  });

  it('should have both Review Answers and Download PDF buttons', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').first().click();

        // Both buttons should be visible
        cy.contains('Review Answers').should('be.visible');
        cy.contains('Download PDF').should('be.visible');
      }
    });
  });

  it('should trigger PDF download when clicking Download PDF', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').first().click();

        // Get the PDF URL
        cy.contains('Download PDF')
          .should('have.attr', 'href')
          .then((href) => {
            // Make a request to the PDF endpoint
            cy.request({
              url: href,
              encoding: 'binary',
            }).then((response) => {
              // Check that the response is a PDF
              expect(response.status).to.eq(200);
              expect(response.headers['content-type']).to.include('application/pdf');
              expect(response.headers['content-disposition']).to.include('attachment');
              expect(response.headers['content-disposition']).to.include('.pdf');
            });
          });
      }
    });
  });

  it('should include filename in PDF download', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').first().click();

        cy.contains('Download PDF')
          .should('have.attr', 'href')
          .then((href) => {
            cy.request({
              url: href,
              encoding: 'binary',
            }).then((response) => {
              // Check that filename contains 'result'
              expect(response.headers['content-disposition']).to.include('result');
            });
          });
      }
    });
  });

  it('should have proper PDF structure', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').first().click();

        cy.contains('Download PDF')
          .should('have.attr', 'href')
          .then((href) => {
            cy.request({
              url: href,
              encoding: 'binary',
            }).then((response) => {
              // Check PDF magic bytes (PDF files start with %PDF)
              const pdfHeader = response.body.substring(0, 4);
              expect(pdfHeader).to.eq('%PDF');
            });
          });
      }
    });
  });

  it('should require authentication for PDF download', () => {
    // Logout first
    cy.visit('/logout/', { method: 'POST', form: true });

    // Try to access PDF directly
    cy.request({
      url: '/my-exams/1/result/pdf/',
      failOnStatusCode: false,
    }).then((response) => {
      // Should redirect to login (302) or return forbidden (403)
      expect(response.status).to.be.oneOf([302, 403]);
    });
  });

  it('should return 404 for non-existent exam PDF', () => {
    // Try to access PDF for non-existent exam
    cy.request({
      url: '/my-exams/99999/result/pdf/',
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(404);
    });
  });

  it('should display download icon on PDF button', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        cy.contains('View Result').first().click();

        // Check that the Download PDF button has an SVG icon
        cy.contains('Download PDF')
          .find('svg')
          .should('exist');
      }
    });
  });

  it('should be accessible from result page after exam completion', () => {
    cy.visit('/my-exams/history/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History') && !$body.text().includes('No Results Found')) {
        // Navigate to result page
        cy.contains('View Result').first().click();
        cy.url().should('include', '/result');

        // Verify result page elements
        cy.contains('Exam Completed').should('be.visible');
        cy.contains('Score').should('be.visible');
        cy.contains('Download PDF').should('be.visible');
      }
    });
  });
});
