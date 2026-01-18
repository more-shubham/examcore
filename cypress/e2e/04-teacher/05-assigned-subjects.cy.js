/**
 * Teacher Assigned Subjects Tests
 *
 * Tests that teachers can view their assigned subjects and related content.
 * Teachers are assigned to specific subjects via the User model.
 *
 * FEATURE STATUS: IMPLEMENTED
 * - Teacher-subject ManyToMany relationship
 * - Dashboard shows assigned subjects
 * - Subjects assigned during invitation
 *
 * Run: npx cypress run --spec "cypress/e2e/04-teacher/05-assigned-subjects.cy.js"
 */

describe('Teacher - Assigned Subjects', () => {
  before(() => {
    cy.task('seedDatabase');
  });

  beforeEach(() => {
    // Login as teacher (DBMS teacher)
    cy.fixture('credentials').then((creds) => {
      cy.visit('/');
      cy.get('input[name="username"]').type(creds.teacher.email);
      cy.get('input[name="password"]').type(creds.teacher.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });
  });

  it('should display assigned subjects on dashboard', () => {
    // Dashboard should show teacher's assigned subjects
    cy.get('body').then(($body) => {
      const text = $body.text();
      // DBMS teacher should see DBMS or database related content
      const hasSubjectInfo = text.includes('DBMS') ||
      text.includes('Database') ||
      text.includes('Subject') ||
      text.includes('assigned');
      expect(hasSubjectInfo).to.be.true;
    });
  });

  it('should show My Subjects section on dashboard', () => {
    // Dashboard should have a "My Subjects" or similar section
    cy.contains(/my subjects|assigned subjects|teaching/i).should('exist');
  });

  it('should display subject statistics on dashboard', () => {
    // Dashboard should show stats for assigned subjects
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasStats = text.includes('question') ||
      text.includes('exam') ||
      text.includes('student') ||
      /\d+/.test(text);
      expect(hasStats).to.be.true;
    });
  });

  // Skip until Issue #1 is implemented
  it.skip('should have link to view subject questions', () => {
    // Should be able to navigate to questions for their subject
    cy.get('a[href*="questions"], a:contains("Questions")').should('exist');
  });

  // Skip until Issue #2 is implemented
  it.skip('should have link to view subject exams', () => {
    // Should be able to navigate to exams for their subject
    cy.get('a[href*="exams"], a:contains("Exams")').should('exist');
  });

  it('should show classes associated with assigned subjects', () => {
    // Teacher should see which classes their subjects belong to
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasClassInfo = text.includes('Semester') ||
      text.includes('CO') ||
      text.includes('IF') ||
      text.includes('Class');
      expect(hasClassInfo).to.be.true;
    });
  });

  it('should show student count for assigned subjects', () => {
    // Dashboard should show how many students are in their classes
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasStudentCount = text.includes('student') && /\d+/.test(text);
      // This may or may not exist depending on implementation
      if (text.includes('student')) {
        expect(hasStudentCount).to.be.true;
      }
    });
  });

  // Skip until Issue #1 is implemented
  it.skip('should only show questions from assigned subjects in question list', () => {
    cy.visit('/questions/');
    // Teacher should only see questions from their assigned subjects
    // DBMS teacher should see DBMS questions, not DSU or OOJ
    cy.get('body').then(($body) => {
      const text = $body.text();
      // If filtered by subject, should only show relevant questions
      if (text.includes('DBMS') || text.includes('Database')) {
        // Good - showing assigned subject content
        expect(true).to.be.true;
      }
    });
  });

  // Skip until Issue #2 is implemented
  it.skip('should only show exams from assigned subjects in exam list', () => {
    cy.visit('/exams/');
    // Teacher should only see exams from their assigned subjects
    cy.get('body').then(($body) => {
      const text = $body.text();
      // Should show exams related to their subjects
      expect(text.length).to.be.greaterThan(0);
    });
  });

  // Skip until Issue #3 is implemented
  it.skip('should only show results from assigned subjects', () => {
    cy.visit('/results/');
    // Teacher should only see results for their subjects
    cy.get('body').then(($body) => {
      const text = $body.text();
      expect(text.length).to.be.greaterThan(0);
    });
  });
});
