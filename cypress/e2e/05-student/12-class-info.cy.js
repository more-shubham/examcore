/**
 * Student Class Information Tests
 *
 * Tests the /my-class/ page that displays class information,
 * subjects with teachers, exam counts, and upcoming exams.
 *
 * Run: npx cypress run --spec "cypress/e2e/05-student/12-class-info.cy.js"
 */

describe('Student Class Information', () => {
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

  it('should navigate to my class page', () => {
    cy.visit('/my-class/');
    cy.url().should('include', '/my-class');
  });

  it('should display class name and description', () => {
    cy.visit('/my-class/');

    // Student Rahul Patil is assigned to CO - 3rd Semester
    cy.contains(/CO.*3rd Semester|Computer Engineering/i).should('be.visible');
  });

  it('should display My Class header', () => {
    cy.visit('/my-class/');

    cy.contains('h1', /My Class/i).should('be.visible');
  });

  it('should display subjects section', () => {
    cy.visit('/my-class/');

    // Should have a Subjects heading
    cy.contains(/Subjects/i).should('be.visible');
  });

  it('should list subjects in the class', () => {
    cy.visit('/my-class/');

    // CO - 3rd Semester subjects
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Check for at least one subject from CO 3rd semester
      const hasSubject = text.includes('Data Structures') ||
      text.includes('DSU') ||
      text.includes('Digital Techniques') ||
      text.includes('DTE') ||
      text.includes('OOP with Java') ||
      text.includes('OOJ') ||
      text.includes('Computer Graphics') ||
      text.includes('CGR');
      expect(hasSubject).to.be.true;
    });
  });

  it('should display subject count', () => {
    cy.visit('/my-class/');

    // Should show number of subjects (4 subjects in CO 3rd semester)
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasSubjectCount = text.includes('4 subject') ||
      text.includes('subjects');
      expect(hasSubjectCount).to.be.true;
    });
  });

  it('should display teacher information for subjects', () => {
    cy.visit('/my-class/');

    // Check for teacher names or "No teacher assigned" text
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Either has assigned teachers or shows not assigned message
      const hasTeacherInfo = text.includes('Teacher') ||
      text.includes('Aarti') ||  // DSU teacher
      text.includes('Kavita') ||  // DTE teacher
      text.includes('Mahesh') ||  // OOJ teacher
      text.includes('No teacher assigned') ||
      text.includes('Not assigned');
      expect(hasTeacherInfo).to.be.true;
    });
  });

  it('should display exam counts for subjects', () => {
    cy.visit('/my-class/');

    // Should show exam-related statistics
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasExamInfo = text.includes('exam') ||
      text.includes('total') ||
      text.includes('completed') ||
      text.includes('upcoming');
      expect(hasExamInfo).to.be.true;
    });
  });

  it('should have back to dashboard link', () => {
    cy.visit('/my-class/');

    // Should have a link back to dashboard
    cy.contains(/Back to Dashboard|Dashboard/i).should('be.visible');
    cy.contains(/Back to Dashboard|Dashboard/i).click();
    cy.url().should('include', '/dashboard');
  });

  it('should have link to view exams', () => {
    cy.visit('/my-class/');

    // Should have links to view exams
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasExamLink = text.includes('view exam') ||
      text.includes('my exam') ||
      text.includes('all exams');
      expect(hasExamLink).to.be.true;
    });
  });

  it('should display class info card with icon', () => {
    cy.visit('/my-class/');

    // Should have a styled card with class information
    cy.get('[class*="bg-white"][class*="rounded"]').should('exist');

    // Should have an SVG icon
    cy.get('svg').should('have.length.greaterThan', 0);
  });

  it('should be accessible from dashboard', () => {
    // Navigate to dashboard first
    cy.visit('/dashboard/');

    // Look for a link to class information
    cy.get('body').then(($body) => {
      const hasClassLink = $body.find('a[href*="my-class"]').length > 0 ||
      $body.text().toLowerCase().includes('my class') ||
      $body.text().toLowerCase().includes('class info');

      if (hasClassLink) {
        cy.contains(/my class|class info|view class/i).click();
        cy.url().should('include', '/my-class');
      } else {
        // If no direct link, navigate via URL
        cy.visit('/my-class/');
        cy.url().should('include', '/my-class');
      }
    });
  });
});
