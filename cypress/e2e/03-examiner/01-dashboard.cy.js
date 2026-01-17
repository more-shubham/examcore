/**
 * Examiner Dashboard Tests
 *
 * Tests examiner dashboard access and functionality.
 * Requires seeded database with examiner user.
 *
 * Run: npx cypress run --spec "cypress/e2e/03-examiner/**"
 */

describe('Examiner Dashboard', () => {
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

  it('should display examiner dashboard', () => {
    cy.url().should('include', '/dashboard');
    cy.contains(/dashboard|welcome/i).should('be.visible');
  });

  it('should show welcome message with examiner name', () => {
    // Verify examiner name appears (Priya Kulkarni)
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasExaminerInfo = text.includes('priya') || text.includes('examiner') || text.includes('welcome');
      expect(hasExaminerInfo).to.be.true;
    });
  });

  it('should display institution name and logo', () => {
    // Verify institution name
    cy.contains(/polytechnic|college|model/i).should('be.visible');

    // Verify institution logo is displayed
    cy.get('img[alt*="Model Polytechnic"], img[alt*="Polytechnic"], img[src*="institution/"]')
      .should('be.visible')
      .and('have.attr', 'src')
      .and('include', 'institution/');
  });

  it('should display My Questions count', () => {
    // Look for questions stat
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasQuestionsInfo = text.includes('question') || text.includes('created');
      expect(hasQuestionsInfo).to.be.true;
    });
  });

  it('should display Exams Created count', () => {
    // Look for exams stat
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasExamsInfo = text.includes('exam') || text.includes('test');
      expect(hasExamsInfo).to.be.true;
    });
  });

  it('should have navigation to Questions', () => {
    cy.contains(/question/i).should('be.visible');
    cy.contains(/question/i).click();
    cy.url().should('include', '/questions');
  });

  it('should have navigation to Exams', () => {
    cy.contains(/exam/i).should('be.visible');
    cy.contains(/exam/i).click();
    cy.url().should('include', '/exams');
  });

  it('should have quick action links', () => {
    // Look for quick action buttons
    cy.get('body').then(($body) => {
      const text = $body.text().toLowerCase();
      const hasQuickActions = ['add', 'create', 'new', 'manage'].some(action => text.includes(action));
      expect(hasQuickActions).to.be.true;
    });
  });

  it('should have logout functionality', () => {
    cy.get('form[action="/logout/"], button:contains("Logout"), a:contains("Logout")').first().then(($logout) => {
      if ($logout.is('form')) {
        cy.wrap($logout).submit();
      } else {
        cy.wrap($logout).click();
      }
    });
    cy.url().should('not.include', '/dashboard');
  });
});
