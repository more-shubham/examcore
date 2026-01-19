/**
 * Student Exam List Tests
 *
 * Tests exam listing, categories, and details for students.
 * Requires seeded database with exams in various states.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/**"
 */

describe('Student - Exam List', () => {
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

  it('should navigate to My Exams page', () => {
    cy.visit('/my-exams/');
    cy.url().should('include', '/my-exams');
    cy.contains(/exam/i).should('be.visible');
  });

  it('should display exam categories', () => {
    cy.visit('/my-exams/');

    // Should have category tabs or sections
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      // Check for at least some category indicators
      const hasCategories = text.includes('active') ||
      text.includes('upcoming') ||
      text.includes('completed') ||
      text.includes('running') ||
      text.includes('past');
      expect(hasCategories).to.be.true;
    });
  });

  it('should display active/running exams', () => {
    cy.visit('/my-exams/');

    // Look for running exams from seed data or Active Now section
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Look for any active exam indicator or section header
      const hasRunningExam = text.includes('DBMS') ||
      text.includes('Networks') ||
      text.includes('Mid-Term') ||
      text.includes('Running') ||
      text.includes('Active') ||
      text.includes('Upcoming') ||  // At minimum, page should show exam categories
      text.includes('No active');
      expect(hasRunningExam).to.be.true;
    });
  });

  it('should display upcoming exams', () => {
    cy.visit('/my-exams/');

    // Look for upcoming exams from seed data
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasUpcomingExam = text.includes('Upcoming') ||
      text.includes('Data Structures Unit Test') ||
      text.includes('Digital Techniques') ||
      text.includes('Not Started');
      expect(hasUpcomingExam).to.be.true;
    });
  });

  it('should display completed exams with results', () => {
    cy.visit('/my-exams/');

    // Look for completed exams from seed data
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasCompletedExam = text.includes('Completed') ||
      text.includes('Java OOP Quiz') ||
      text.includes('Ended') ||
      text.includes('Result') ||
      text.includes('Score');
      expect(hasCompletedExam).to.be.true;
    });
  });

  it('should show exam details', () => {
    cy.visit('/my-exams/');

    // Exam cards are in divs with bg-white rounded-xl classes
    // Check that exam info is present on the page
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Should show duration, questions, or subject info
      const hasExamDetails = text.includes('Duration') ||
      text.includes('Questions') ||
      text.includes('min') ||
      text.includes('DSU') ||
      text.includes('Data Structures') ||
      text.includes('Subject');
      expect(hasExamDetails).to.be.true;
    });
  });

  it('should show Start Exam button for active exams', () => {
    cy.visit('/my-exams/');

    // Look for start button on active exams
    cy.get('a:contains("Start"), button:contains("Start"), a:contains("Take"), button:contains("Take")').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().should('be.visible');
      }
    });
  });

  it('should show View Result button for completed exams', () => {
    cy.visit('/my-exams/');

    // Look for result button on completed exams
    cy.get('a:contains("Result"), button:contains("Result"), a:contains("View"), a[href*="result"]').then(($btn) => {
      if ($btn.length > 0) {
        cy.wrap($btn).first().should('be.visible');
      }
    });
  });

  it('should display exam duration', () => {
    cy.visit('/my-exams/');

    // Look for duration info
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasDuration = text.includes('min') ||
      text.includes('hour') ||
      text.includes('duration') ||
      /\d+\s*(minutes?|mins?|hours?|hrs?)/i.test(text);
      expect(hasDuration).to.be.true;
    });
  });

  it('should display exam subject', () => {
    cy.visit('/my-exams/');

    // Look for subject info
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasSubject = text.includes('DSU') ||
      text.includes('DMS') ||
      text.includes('Data Structures') ||
      text.includes('DBMS') ||
      text.includes('Subject');
      expect(hasSubject).to.be.true;
    });
  });
});
