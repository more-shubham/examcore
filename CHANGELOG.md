# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-15

### Added

- Initial project setup with Django 5.0
- Single-page authentication system (login/register/OTP verification)
- School setup wizard for first-time registration
- Role-based user management (Admin, Examiner, Teacher, Student)
- Invite-based user creation with email notifications
- Password reset with OTP verification
- Class management with drag-drop reordering
- Student management within classes
- Examiner and Teacher management pages
- Role-specific dashboards
- Tailwind CSS integration via django-tailwind
- PostgreSQL database support
- Docker Compose setup with Mailpit for email testing

### Security

- CSRF protection on all forms
- Session-based authentication
- Secure token generation for invitations (7-day expiry)
- OTP expiration (10 minutes)
- Password minimum length enforcement (8 characters)

[Unreleased]: https://github.com/more-shubham/examcore/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/more-shubham/examcore/releases/tag/v0.1.0
