/**
 * Admin Subject Management Tests
 *
 * Tests CRUD operations for MSBTE subjects within semesters.
 * Run after classes test (classes must exist).
 *
 * Run: npm run cy:run:admin
 */

describe('Admin - Subject Management', () => {
  const admin = {
    email: 'admin@examcore.local',
    password: 'Admin@123',
  };

  // NO setupAdminUser - uses data from registration test

  const co3Subjects = [
    { name: 'Data Structures (DSU)', description: 'Stacks Queues Trees Graphs' },
    { name: 'Digital Techniques (DTE)', description: 'Logic Gates Combinational Sequential Circuits' },
  ];

  const co4Subjects = [
    { name: 'DBMS (DMS)', description: 'SQL Normalization ER Diagrams' },
    { name: 'Software Engineering (SEN)', description: 'SDLC Models Testing Documentation' },
  ];

  // Helper function to navigate to subjects for a class
  const navigateToSubjects = (className) => {
    cy.visit('/classes/');
    cy.contains('.class-item', className)
      .invoke('attr', 'data-id')
      .then((classId) => {
        cy.visit(`/classes/${classId}/subjects/`);
      });
  };

  beforeEach(() => {
    // Login once and cache the session for all tests
    cy.loginAsAdmin();
  });

  it('should navigate to subjects page for CO 3rd Semester', () => {
    navigateToSubjects('CO - 3rd Semester');
    cy.url().should('include', '/subjects');
    cy.contains(/subject/i).should('be.visible');
  });

  it('should create subjects for CO 3rd Semester', () => {
    navigateToSubjects('CO - 3rd Semester');

    // Create each subject
    co3Subjects.forEach((subject) => {
      // Click add button
      cy.contains('button', 'Add Subject').click();

      // Wait for modal
      cy.get('#addModal').should('be.visible');

      // Fill form in modal
      cy.get('#addModal input[name="name"]').type(subject.name);
      cy.get('#addModal textarea[name="description"]').type(subject.description);

      // Submit modal form
      cy.get('#addModal button[type="submit"]').click();

      // Wait for modal to close and verify subject was created
      cy.contains(subject.name).should('be.visible');
    });
  });

  it('should display all CO 3rd Semester subjects', () => {
    navigateToSubjects('CO - 3rd Semester');

    // All subjects should be visible
    co3Subjects.forEach((subject) => {
      cy.contains(subject.name).should('be.visible');
    });
  });

  it('should create subjects for CO 4th Semester', () => {
    navigateToSubjects('CO - 4th Semester');

    // Create each subject
    co4Subjects.forEach((subject) => {
      // Click add button
      cy.contains('button', 'Add Subject').click();

      // Wait for modal
      cy.get('#addModal').should('be.visible');

      // Fill form in modal
      cy.get('#addModal input[name="name"]').type(subject.name);
      cy.get('#addModal textarea[name="description"]').type(subject.description);

      // Submit modal form
      cy.get('#addModal button[type="submit"]').click();

      // Verify subject was created
      cy.contains(subject.name).should('be.visible');
    });
  });

  it('should toggle subject active/inactive status', () => {
    navigateToSubjects('CO - 3rd Semester');

    // Find Deactivate button and click it
    cy.contains('button', 'Deactivate').first().click();

    // Should show Inactive status
    cy.contains('Inactive').should('be.visible');

    // Reactivate
    cy.contains('button', 'Activate').first().click();
    cy.contains('Active').should('be.visible');
  });

  it('should show subject list per semester correctly', () => {
    // Check CO 3rd Sem subjects
    navigateToSubjects('CO - 3rd Semester');
    co3Subjects.forEach((subject) => {
      cy.contains(subject.name).should('be.visible');
    });

    // Check CO 4th Sem subjects
    navigateToSubjects('CO - 4th Semester');
    co4Subjects.forEach((subject) => {
      cy.contains(subject.name).should('be.visible');
    });

    // Subjects from one semester should not appear in another
    navigateToSubjects('CO - 3rd Semester');
    co4Subjects.forEach((subject) => {
      cy.contains(subject.name).should('not.exist');
    });
  });
});
