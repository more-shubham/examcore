const { defineConfig } = require('cypress');
const { execSync } = require('child_process');
const path = require('path');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.js',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    taskTimeout: 120000,
    // Stop on first error - no retries
    retries: 0,
    // Environment variables
    env: {
      // Mailpit API URL for fetching OTP emails
      MAILPIT_URL: 'http://localhost:8025',
    },
    setupNodeEvents(on, config) {
      on('task', {
        // Reset database - flush all data
        resetDatabase() {
          const projectRoot = path.resolve(__dirname);
          const pythonPath = process.env.CI ? 'python' : path.join(projectRoot, '.venv', 'bin', 'python');
          const managePy = path.join(projectRoot, 'manage.py');

          try {
            execSync(`${pythonPath} ${managePy} flush --no-input`, {
              cwd: projectRoot,
              stdio: 'pipe',
            });
            return null;
          } catch (error) {
            throw error;
          }
        },

        // Setup admin user and institution for tests (programmatic, no UI)
        setupAdminUser({ email, password }) {
          const projectRoot = path.resolve(__dirname);
          const pythonPath = process.env.CI ? 'python' : path.join(projectRoot, '.venv', 'bin', 'python');
          const managePy = path.join(projectRoot, 'manage.py');
          const fs = require('fs');

          // Ensure media/institution directory exists and copy logo
          const mediaDir = path.join(projectRoot, 'media', 'institution');
          const logoSrc = path.join(projectRoot, 'cypress', 'fixtures', 'logo.png');
          const logoDest = path.join(mediaDir, 'logo.png');

          try {
            if (!fs.existsSync(mediaDir)) {
              fs.mkdirSync(mediaDir, { recursive: true });
            }
            fs.copyFileSync(logoSrc, logoDest);
          } catch (err) {
            // Logo copy failed, continue anyway
          }

          // Python script to create admin and institution with logo
          const pythonScript = `
import django
django.setup()
from django.contrib.auth import get_user_model
from apps.institution.models import Institution

User = get_user_model()

# Create or update institution with logo
if Institution.objects.exists():
    inst = Institution.objects.first()
    inst.name = 'Model Polytechnic College, Mumbai'
    inst.email = 'principal@modelpolytechnic.edu.in'
    inst.phone = '+91-22-26543210'
    inst.address = 'Plot No. 5, Sector-10, Vashi, Navi Mumbai - 400703, Maharashtra'
    inst.logo = 'institution/logo.png'
    inst.save()
    print('Institution updated with logo')
else:
    Institution.objects.create(
        name='Model Polytechnic College, Mumbai',
        email='principal@modelpolytechnic.edu.in',
        phone='+91-22-26543210',
        address='Plot No. 5, Sector-10, Vashi, Navi Mumbai - 400703, Maharashtra',
        logo='institution/logo.png'
    )
    print('Institution created with logo')

# Create admin if not exists
if not User.objects.filter(email='${email}').exists():
    # Extract username from email (before @)
    username = '${email}'.split('@')[0].replace('.', '_')
    user = User.objects.create_user(
        username=username,
        email='${email}',
        password='${password}',
        role='admin',
        is_staff=True,
        is_superuser=True
    )
    print(f'Admin user created: {user.email}')
else:
    # Update password if user exists
    user = User.objects.get(email='${email}')
    user.set_password('${password}')
    user.save()
    print(f'Admin password updated: {user.email}')
`;

          try {
            execSync(`${pythonPath} ${managePy} shell -c "${pythonScript}"`, {
              cwd: projectRoot,
              stdio: 'pipe',
            });
            return null;
          } catch (error) {
            throw error;
          }
        },

        // Seed database with test data using seed_cypress command
        seedDatabase() {
          const projectRoot = path.resolve(__dirname);
          const pythonPath = process.env.CI ? 'python' : path.join(projectRoot, '.venv', 'bin', 'python');
          const managePy = path.join(projectRoot, 'manage.py');
          const fs = require('fs');

          // Copy logo first (so seed data has it available)
          const mediaDir = path.join(projectRoot, 'media', 'institution');
          const logoSrc = path.join(projectRoot, 'cypress', 'fixtures', 'logo.png');
          const logoDest = path.join(mediaDir, 'logo.png');

          try {
            if (!fs.existsSync(mediaDir)) {
              fs.mkdirSync(mediaDir, { recursive: true });
            }
            fs.copyFileSync(logoSrc, logoDest);
          } catch (err) {
            // Logo copy failed, continue anyway
          }

          try {
            execSync(`${pythonPath} ${managePy} seed_cypress`, {
              cwd: projectRoot,
              stdio: 'pipe',
            });
            return null;
          } catch (error) {
            throw error;
          }
        },

        // Clear Mailpit inbox
        clearMailpit() {
          const mailpitUrl = config.env.MAILPIT_URL || 'http://localhost:8025';
          try {
            execSync(`curl -X DELETE ${mailpitUrl}/api/v1/messages`, {
              stdio: 'pipe',
            });
            return null;
          } catch (error) {
            return null; // Don't fail if Mailpit is not running
          }
        },
      });

      return config;
    },
  },
});
