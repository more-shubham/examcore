// ***********************************************
// Custom Cypress commands for ExamCore E2E tests
// ***********************************************

// ============================================
// Mailpit Integration Commands
// ============================================

/**
 * Fetch the latest OTP from Mailpit for a given email address
 * Mailpit API: http://localhost:8025/api/v1/messages
 * @param {string} email - The email address to find OTP for
 * @param {number} maxRetries - Maximum number of retries (default: 10)
 */
Cypress.Commands.add('getOTPFromMailpit', (email, maxRetries = 10) => {
  const mailpitUrl = Cypress.env('MAILPIT_URL') || 'http://localhost:8025';

  const fetchOTP = (attempt = 1) => {
    return cy.request({
      method: 'GET',
      url: `${mailpitUrl}/api/v1/messages`,
      headers: { 'Accept': 'application/json' },
      failOnStatusCode: false,
    }).then((response) => {
      if (response.status !== 200) {
        if (attempt < maxRetries) {
          cy.wait(1000);
          return fetchOTP(attempt + 1);
        }
        throw new Error(`Mailpit API error: ${response.status}`);
      }

      const messages = response.body.messages || [];

      // Find email for the given address (most recent first)
      const message = messages.find(m =>
        m.To && m.To.some(to => to.Address.toLowerCase() === email.toLowerCase())
      );

      if (!message) {
        if (attempt < maxRetries) {
          cy.wait(1000);
          return fetchOTP(attempt + 1);
        }
        throw new Error(`No email found for ${email} after ${maxRetries} attempts`);
      }

      // Fetch full message content
      return cy.request({
        method: 'GET',
        url: `${mailpitUrl}/api/v1/message/${message.ID}`,
        headers: { 'Accept': 'application/json' },
      }).then((msgResponse) => {
        // Extract 6-digit OTP from email body
        const body = msgResponse.body.Text || msgResponse.body.HTML || '';
        const otpMatch = body.match(/\b(\d{6})\b/);

        if (!otpMatch) {
          throw new Error('Could not find 6-digit OTP in email body');
        }

        const otp = otpMatch[1];
        return cy.wrap(otp);
      });
    });
  };

  return fetchOTP();
});

/**
 * Clear all emails from Mailpit (for clean test state)
 */
Cypress.Commands.add('clearMailpit', () => {
  const mailpitUrl = Cypress.env('MAILPIT_URL') || 'http://localhost:8025';
  return cy.request({
    method: 'DELETE',
    url: `${mailpitUrl}/api/v1/messages`,
    failOnStatusCode: false,
  });
});

/**
 * Wait for email to arrive in Mailpit
 * @param {string} email - Email address to wait for
 * @param {number} timeout - Max wait time in ms (default: 30000)
 */
Cypress.Commands.add('waitForEmail', (email, timeout = 30000) => {
  const mailpitUrl = Cypress.env('MAILPIT_URL') || 'http://localhost:8025';
  const startTime = Date.now();

  const checkEmail = () => {
    return cy.request({
      method: 'GET',
      url: `${mailpitUrl}/api/v1/messages`,
      headers: { 'Accept': 'application/json' },
      failOnStatusCode: false,
    }).then((response) => {
      const messages = response.body.messages || [];
      const found = messages.find(m =>
        m.To && m.To.some(to => to.Address.toLowerCase() === email.toLowerCase())
      );

      if (found) {
        return found;
      }

      if (Date.now() - startTime < timeout) {
        cy.wait(500);
        return checkEmail();
      }

      throw new Error(`Email for ${email} not received within ${timeout}ms`);
    });
  };

  return checkEmail();
});

// ============================================
// Authentication Commands
// ============================================

/**
 * Login with session caching - logs in once and reuses session
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {string} sessionName - Unique session name for caching
 */
Cypress.Commands.add('loginWithSession', (email, password, sessionName = null) => {
  const session = sessionName || email;
  cy.session(session, () => {
    cy.visit('/');
    cy.get('input[name="username"]').type(email);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});

/**
 * Login as admin with session caching
 * Uses the admin credentials from registration test
 */
Cypress.Commands.add('loginAsAdmin', () => {
  cy.loginWithSession('admin@examcore.local', 'Admin@123', 'admin-session');
});

/**
 * Login as a specific role using credentials from fixtures
 * @param {string} role - One of: admin, examiner, examiner2, teacher, student
 */
Cypress.Commands.add('login', (role) => {
  cy.fixture('credentials').then((creds) => {
    const user = creds[role];
    if (!user) {
      throw new Error(`Unknown role: ${role}. Available: admin, examiner, examiner2, teacher, student`);
    }

    cy.visit('/');
    cy.get('input[name="username"]').clear().type(user.email);
    cy.get('input[name="password"]').clear().type(user.password);
    cy.get('button[type="submit"]').click();

    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
  });
});

/**
 * Simplified login using role name
 * Alias for cy.login() but more descriptive
 * @param {string} role - Role to login as
 */
Cypress.Commands.add('loginAs', (role) => {
  cy.login(role);
});

/**
 * Login with specific email and password
 * @param {string} email
 * @param {string} password
 */
Cypress.Commands.add('loginWith', (email, password) => {
  cy.visit('/');
  cy.get('input[name="username"]').clear().type(email);
  cy.get('input[name="password"]').clear().type(password);
  cy.get('button[type="submit"]').click();
});

/**
 * Logout the current user
 */
Cypress.Commands.add('logout', () => {
  // Find and click logout button/link
  // The logout form uses POST method
  cy.get('form[action="/logout/"]').submit();
  cy.url().should('eq', Cypress.config().baseUrl + '/');
});

/**
 * Get CSRF token from the page
 */
Cypress.Commands.add('getCsrfToken', () => {
  return cy.get('input[name="csrfmiddlewaretoken"]').invoke('val');
});

// ============================================
// Dashboard Verification Commands
// ============================================

/**
 * Verify dashboard statistics match expected values
 * @param {object} expectedStats - Object with stat names and expected values
 */
Cypress.Commands.add('verifyDashboardStats', (expectedStats) => {
  Object.entries(expectedStats).forEach(([statName, expectedValue]) => {
    cy.get(`[data-stat="${statName}"], .stat-${statName}, [data-testid="${statName}-stat"]`)
      .should('contain', expectedValue);
  });
});

/**
 * Verify institution information is displayed
 * @param {string} name - Expected institution name or partial match
 */
Cypress.Commands.add('verifyInstitutionInfo', (name) => {
  cy.contains(new RegExp(name, 'i')).should('be.visible');
});

// ============================================
// Form Helper Commands
// ============================================

/**
 * Fill a form field by name attribute
 * @param {string} name - Form field name
 * @param {string} value - Value to enter
 */
Cypress.Commands.add('fillField', (name, value) => {
  cy.get(`[name="${name}"]`).clear().type(value);
});

/**
 * Select an option from a dropdown by name and value
 * @param {string} name - Select field name
 * @param {string} value - Option value to select
 */
Cypress.Commands.add('selectOption', (name, value) => {
  cy.get(`select[name="${name}"]`).select(value);
});

// ============================================
// Navigation Commands
// ============================================

/**
 * Check if user is on the dashboard
 */
Cypress.Commands.add('shouldBeOnDashboard', () => {
  cy.url().should('include', '/dashboard');
});

/**
 * Check if user is on the login page (root)
 */
Cypress.Commands.add('shouldBeOnLoginPage', () => {
  cy.url().should('eq', Cypress.config().baseUrl + '/');
});

/**
 * Navigate to a specific URL and wait for page load
 * @param {string} path - URL path
 */
Cypress.Commands.add('navigateTo', (path) => {
  cy.visit(path);
  cy.url().should('include', path);
});

/**
 * Check if currently on a specific page
 * @param {string} urlPart - Part of URL to check
 */
Cypress.Commands.add('shouldBeOnPage', (urlPart) => {
  cy.url().should('include', urlPart);
});

// ============================================
// Message/Alert Commands
// ============================================

/**
 * Check for a success message on the page
 * @param {string} message - Expected message text (partial match)
 */
Cypress.Commands.add('shouldShowSuccess', (message) => {
  cy.contains(message).should('be.visible');
});

/**
 * Check for an error message on the page
 * @param {string} message - Expected error text (partial match)
 */
Cypress.Commands.add('shouldShowError', (message) => {
  cy.contains(message).should('be.visible');
});

/**
 * Wait for page to fully load
 */
Cypress.Commands.add('waitForPageLoad', () => {
  cy.document().its('readyState').should('eq', 'complete');
});

// ============================================
// UI Interaction Commands
// ============================================

/**
 * Click a button containing specific text
 * @param {string} text - Button text
 */
Cypress.Commands.add('clickButton', (text) => {
  cy.contains('button', text).click();
});

/**
 * Click a link containing specific text
 * @param {string} text - Link text
 */
Cypress.Commands.add('clickLink', (text) => {
  cy.contains('a', text).click();
});

// ============================================
// Table Commands
// ============================================

/**
 * Verify table has specific number of rows (excluding header)
 * @param {number} count - Expected row count
 */
Cypress.Commands.add('tableRowCount', (count) => {
  cy.get('tbody tr').should('have.length', count);
});

/**
 * Get table row containing specific text
 * @param {string} text - Text to search for in the row
 */
Cypress.Commands.add('getTableRowWith', (text) => {
  return cy.contains('tr', text);
});

// ============================================
// Registration and Setup Commands
// ============================================

/**
 * Complete full admin registration flow with OTP from Mailpit
 * Use this on a fresh database
 */
Cypress.Commands.add('registerAdmin', () => {
  cy.fixture('test-data').then((data) => {
    cy.clearMailpit();
    cy.visit('/');

    // Step 1: Registration form
    cy.get('input[name="email"]').type(data.admin.email);
    cy.get('input[name="password"]').type(data.admin.password);
    cy.get('input[name="confirm_password"]').type(data.admin.password);
    cy.contains('button', 'Continue').click();

    // Step 2: OTP verification
    cy.contains('Verify Your Email').should('be.visible');
    cy.getOTPFromMailpit(data.admin.email).then((otp) => {
      cy.get('input[name="otp"]').type(otp);
      cy.contains('button', 'Verify').click();
    });

    // Step 3: Institution setup
    cy.contains('Setup', { timeout: 10000 }).should('be.visible');
    cy.get('input[name="name"]').type(data.institution.name);
    cy.get('input[name="email"]').type(data.institution.email);
    cy.get('input[name="phone"]').type(data.institution.phone);
    cy.get('textarea[name="address"]').type(data.institution.address);

    // Upload logo if field exists
    cy.get('input[name="logo"], input[type="file"]').then(($input) => {
      if ($input.length > 0) {
        cy.wrap($input).selectFile('cypress/fixtures/logo.png', { force: true });
      }
    });

    cy.contains('button', /complete|setup|submit/i).click();

    // Should be on dashboard
    cy.url().should('include', '/dashboard');
  });
});

// ============================================
// Admin Management Commands
// ============================================

/**
 * Create a class/semester via the UI
 * @param {string} name - Class name
 * @param {string} description - Class description
 */
Cypress.Commands.add('createClass', (name, description) => {
  cy.visit('/classes/');
  cy.contains(/add|create|new/i).click();
  cy.get('input[name="name"]').type(name);
  cy.get('textarea[name="description"], input[name="description"]').then(($desc) => {
    if ($desc.length > 0) {
      cy.wrap($desc).type(description);
    }
  });
  cy.get('button[type="submit"]').click();
  cy.contains(name).should('be.visible');
});

/**
 * Create a subject via the UI
 * @param {number} classId - The class ID to add subject to
 * @param {string} subjectName - Subject name
 * @param {string} description - Subject description (optional)
 */
Cypress.Commands.add('createSubject', (classId, subjectName, description = '') => {
  cy.visit(`/classes/${classId}/subjects/`);
  cy.contains(/add|create|new/i).click();
  cy.get('input[name="name"]').type(subjectName);
  if (description) {
    cy.get('textarea[name="description"], input[name="description"]').then(($desc) => {
      if ($desc.length > 0) {
        cy.wrap($desc).type(description);
      }
    });
  }
  cy.get('button[type="submit"]').click();
});

/**
 * Invite a user via the UI
 * @param {string} role - Role type (examiner, teacher, student)
 * @param {string} email - User's email address
 * @param {object} options - Additional options (classId for students, etc.)
 */
Cypress.Commands.add('inviteUser', (role, email, options = {}) => {
  const urlMap = {
    examiner: '/examiners/',
    teacher: '/teachers/',
    student: options.classId ? `/classes/${options.classId}/students/` : '/students/',
  };

  cy.visit(urlMap[role]);
  cy.contains(/invite|add|create/i).click();
  cy.get('input[name="email"]').type(email);
  cy.get('button[type="submit"]').click();
});

// ============================================
// Question Management Commands
// ============================================

/**
 * Create a question via the UI
 * @param {object} questionData - Question data object
 * @param {string} subjectName - Subject to assign question to
 */
Cypress.Commands.add('createQuestion', (questionData, subjectName) => {
  cy.visit('/questions/add/');

  // Fill question text
  cy.get('textarea[name="question_text"], textarea[name="text"]').type(questionData.text);

  // Select subject
  if (subjectName) {
    cy.get('select[name="subject"]').select(subjectName);
  }

  // Fill options
  questionData.options.forEach((option, index) => {
    const optionNum = index + 1;
    const optionLetter = String.fromCharCode(97 + index); // a, b, c, d
    cy.get(`input[name="option_${optionLetter}"], input[name="option_${optionNum}"]`).type(option);
  });

  // Select correct answer
  const correctLetter = String.fromCharCode(97 + questionData.correct); // a, b, c, d
  const correctNum = questionData.correct + 1;
  cy.get(`input[name="correct_option"][value="${correctLetter}"], input[name="correct_option"][value="${correctNum}"]`).check();

  cy.get('button[type="submit"]').click();
});

// ============================================
// Exam Management Commands
// ============================================

/**
 * Create an exam via the UI
 * @param {object} examData - Exam configuration data
 * @param {string} subjectName - Subject for the exam
 */
Cypress.Commands.add('createExam', (examData, subjectName) => {
  cy.visit('/exams/add/');

  cy.get('input[name="title"]').type(examData.title);
  cy.get('textarea[name="description"]').type(examData.description);

  if (subjectName) {
    cy.get('select[name="subject"]').select(subjectName);
  }

  cy.get('input[name="duration"]').clear().type(examData.duration.toString());

  cy.get('input[name="passing_percentage"], input[name="pass_percentage"]').then(($input) => {
    if ($input.length > 0) {
      cy.wrap($input).clear().type(examData.passingPercentage.toString());
    }
  });

  cy.get('button[type="submit"]').click();
});

/**
 * Add questions to an existing exam
 * @param {number} examId - The exam ID
 * @param {number} count - Number of questions to add
 */
Cypress.Commands.add('addQuestionsToExam', (examId, count) => {
  cy.visit(`/exams/${examId}/questions/`);
  cy.contains(/add|select/i).click();
  // Select questions
  cy.get('input[type="checkbox"]').then(($checkboxes) => {
    const toSelect = Math.min(count, $checkboxes.length);
    for (let i = 0; i < toSelect; i++) {
      cy.wrap($checkboxes[i]).check();
    }
  });
  cy.get('button[type="submit"]').click();
});

/**
 * Publish an exam
 * @param {number} examId - The exam ID
 */
Cypress.Commands.add('publishExam', (examId) => {
  cy.visit(`/exams/${examId}/`);
  cy.contains(/publish|start|activate/i).click();
});

// ============================================
// Student Exam Commands
// ============================================

/**
 * Take an exam by answering questions
 * @param {number} examId - The exam ID
 * @param {Array} answers - Array of answer indices (0-based) or 'random' for random answers
 */
Cypress.Commands.add('takeExam', (examId, answers = 'random') => {
  cy.visit(`/my-exams/${examId}/start/`);

  // Click start/begin if needed
  cy.get('button:contains("Start"), button:contains("Begin"), a:contains("Start")').then(($btn) => {
    if ($btn.length > 0) {
      cy.wrap($btn).first().click();
    }
  });

  // Answer questions
  if (answers === 'random') {
    // Select random answers for all questions
    cy.get('.question, [data-question], [data-testid="question"]').each(($question) => {
      const randomIndex = Math.floor(Math.random() * 4);
      cy.wrap($question).find(`input[type="radio"]`).eq(randomIndex).check();
    });
  } else {
    // Use provided answers
    cy.get('.question, [data-question]').each(($question, index) => {
      const answerIndex = answers[index] !== undefined ? answers[index] : 0;
      cy.wrap($question).find(`input[type="radio"]`).eq(answerIndex).check();
    });
  }

  // Submit exam
  cy.contains('button', /submit|finish/i).click();

  // Confirm if dialog appears
  cy.get('body').then(($body) => {
    if ($body.find('button:contains("Confirm"), button:contains("Yes")').length > 0) {
      cy.contains('button', /confirm|yes/i).click();
    }
  });
});

/**
 * For exam-taking: select an answer option by its index (1-based)
 * @param {number} optionIndex - Option number (1, 2, 3, or 4)
 */
Cypress.Commands.add('selectAnswer', (optionIndex) => {
  cy.get(`input[type="radio"][value="${optionIndex}"]`).check();
});

/**
 * Submit an exam
 */
Cypress.Commands.add('submitExam', () => {
  cy.get('button[type="submit"]').contains(/submit/i).click();
});
