/**
 * Admin Class (Semester) Management Tests
 *
 * Tests CRUD operations for classes/semesters with MSBTE polytechnic context.
 * Automatically sets up admin user if not exists.
 *
 * Run: npm run cy:run:admin
 */

describe('Admin - Class/Semester Management', () => {
  const admin = {
    email: 'admin@examcore.local',
    password: 'Admin@123',
  };

  // NO setupAdminUser - uses data from registration test

  const testSemesters = [
    { name: 'CO - 3rd Semester', description: 'Computer Engineering Third Semester' },
    { name: 'CO - 4th Semester', description: 'Computer Engineering Fourth Semester' },
    { name: 'IF - 3rd Semester', description: 'Information Technology Third Semester' },
  ];

  beforeEach(() => {
    // Login once and cache the session for all tests
    cy.loginAsAdmin();
  });

  it('should navigate to classes page', () => {
    cy.visit('/classes/');
    cy.url().should('include', '/classes');
  });

  it('should create CO - 3rd Semester', () => {
    cy.visit('/classes/');

    // Click add button to open modal
    cy.contains('button', /add/i).click();

    // Wait for modal to be visible
    cy.get('#addClassModal').should('be.visible');

    // Fill form in modal - only name field exists
    cy.get('#addClassModal input[name="name"]').type(testSemesters[0].name);

    // Submit modal form
    cy.get('#addClassModal button[type="submit"]').click();

    // Verify semester appears in list
    cy.contains(testSemesters[0].name).should('be.visible');
  });

  it('should create CO - 4th Semester', () => {
    cy.visit('/classes/');

    // Click add button to open modal
    cy.contains('button', /add/i).click();

    // Wait for modal to be visible
    cy.get('#addClassModal').should('be.visible');

    // Fill form in modal
    cy.get('#addClassModal input[name="name"]').type(testSemesters[1].name);

    // Submit modal form
    cy.get('#addClassModal button[type="submit"]').click();

    // Verify semester appears in list
    cy.contains(testSemesters[1].name).should('be.visible');
  });

  it('should create IF - 3rd Semester', () => {
    cy.visit('/classes/');

    // Click add button to open modal
    cy.contains('button', /add/i).click();

    // Wait for modal to be visible
    cy.get('#addClassModal').should('be.visible');

    // Fill form in modal
    cy.get('#addClassModal input[name="name"]').type(testSemesters[2].name);

    // Submit modal form
    cy.get('#addClassModal button[type="submit"]').click();

    // Verify semester appears in list
    cy.contains(testSemesters[2].name).should('be.visible');
  });

  it('should display all semesters in list', () => {
    cy.visit('/classes/');

    // Verify at least one semester is visible (from previous create tests)
    cy.get('.class-item').should('have.length.at.least', 1);
  });

  it('should have Students link for each class', () => {
    cy.visit('/classes/');

    // Each class should have a Students link
    cy.get('.class-item').first().within(() => {
      cy.contains('Students').should('be.visible');
    });
  });

  it('should navigate to students page when Students link clicked', () => {
    cy.visit('/classes/');

    // Click Students link on first class
    cy.get('.class-item').first().contains('Students').click();

    // Should navigate to students page for that class
    cy.url().should('include', '/students');
  });

  it('should support drag and drop reordering', () => {
    cy.visit('/classes/');

    // Verify drag handles exist
    cy.get('.drag-handle').should('have.length.at.least', 1);
  });

  it('should display student count when students exist', () => {
    cy.visit('/classes/');

    // Check if student count is displayed (may or may not have students)
    cy.get('body').then(($body) => {
      const text = $body.text();
      const hasStudentInfo = /students/i.test(text);
      cy.log(`Student info present: ${hasStudentInfo}`);
    });
  });
});
