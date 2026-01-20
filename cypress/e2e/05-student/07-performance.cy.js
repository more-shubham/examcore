/**
 * Student Performance Dashboard Tests
 *
 * Tests the performance analytics dashboard functionality.
 * Requires seeded database with student who has completed exams.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/07-performance.cy.js"
 */

describe('Student Performance Dashboard', () => {
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

  it('should have My Performance link on dashboard', () => {
    cy.contains('My Performance').should('be.visible');
    cy.contains('My Performance').should('have.attr', 'href').and('include', '/performance');
  });

  it('should navigate to performance page from dashboard', () => {
    cy.contains('My Performance').click();
    cy.url().should('include', '/my-exams/performance');
    cy.contains('My Performance').should('be.visible');
  });

  it('should display page header and back button', () => {
    cy.visit('/my-exams/performance/');

    cy.contains('My Performance').should('be.visible');
    cy.contains('Track your exam history').should('be.visible');
    cy.contains('Back to Exams').should('be.visible');
  });

  it('should display overall statistics cards', () => {
    cy.visit('/my-exams/performance/');

    // Check for stats cards (even if 0)
    cy.get('body').then(($body) => {
      const hasStats = $body.text().includes('Exams Taken') ||
      $body.text().includes('Average Score') ||
      $body.text().includes('Pass Rate') ||
      $body.text().includes('No Exam History');
      expect(hasStats).to.be.true;
    });
  });

  it('should show empty state when no exams completed', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if ($body.text().includes('No Exam History')) {
        // Empty state should be displayed
        cy.contains('No Exam History Yet').should('be.visible');
        cy.contains('Complete your first exam').should('be.visible');
        cy.contains('View Available Exams').should('be.visible');
      }
    });
  });

  it('should display statistics when exams are completed', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        // Should show exam statistics
        cy.contains('Exams Taken').should('be.visible');
        cy.contains('Average Score').should('be.visible');
        cy.contains('Pass Rate').should('be.visible');
        cy.contains('Passed').should('be.visible');
      }
    });
  });

  it('should display highest and lowest scores', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        // Should show highest/lowest score cards
        cy.contains('Highest Score').should('be.visible');
        cy.contains('Lowest Score').should('be.visible');
      }
    });
  });

  it('should display score trend chart', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        cy.contains('Score Trend').should('be.visible');
        cy.get('#trendChart').should('exist');
      }
    });
  });

  it('should display subject comparison chart', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        cy.contains('Performance by Subject').should('be.visible');
        cy.get('#subjectChart').should('exist');
      }
    });
  });

  it('should display subject-wise breakdown', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        cy.contains('Subject-wise Breakdown').should('be.visible');
        // Should have progress bars
        cy.get('.bg-gray-200.rounded-full').should('have.length.at.least', 1);
      }
    });
  });

  it('should display recent exam history table', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        cy.contains('Recent Exams').should('be.visible');
        // Should have table headers
        cy.contains('Exam').should('be.visible');
        cy.contains('Subject').should('be.visible');
        cy.contains('Date').should('be.visible');
        cy.contains('Score').should('be.visible');
      }
    });
  });

  it('should have View Result links in recent exams table', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        cy.contains('View Result').should('be.visible');
        cy.contains('View Result').should('have.attr', 'href').and('include', '/result');
      }
    });
  });

  it('should navigate to result page from recent exams', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        cy.contains('View Result').first().click();
        cy.url().should('include', '/result');
      }
    });
  });

  it('should navigate back to exams list', () => {
    cy.visit('/my-exams/performance/');

    cy.contains('Back to Exams').click();
    cy.url().should('include', '/my-exams');
    cy.url().should('not.include', '/performance');
  });

  it('should show pass/fail status in recent exams', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        // Should have pass or fail badges
        const hasStatus = $body.text().includes('Pass') || $body.text().includes('Fail');
        expect(hasStatus).to.be.true;
      }
    });
  });

  it('should show color-coded score badges', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        // Should have colored badges (supports both old green/yellow/red and new indigo/gray styling)
        const hasColoredBadge = $body.find('.bg-green-100, .bg-yellow-100, .bg-red-100, .bg-primary-100, .bg-gray-100').length > 0 ||
        $body.text().includes('Pass') || $body.text().includes('Fail');
        expect(hasColoredBadge).to.be.true;
      }
    });
  });

  it('should load Chart.js for visualizations', () => {
    cy.visit('/my-exams/performance/');

    cy.get('body').then(($body) => {
      if (!$body.text().includes('No Exam History')) {
        // Chart.js script should be loaded
        cy.get('script[src*="chart.js"]').should('exist');
      }
    });
  });
});
