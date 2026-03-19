/**
 * Email Service
 * Send emails for notifications, verification, etc.
 * NOTE: This is a basic implementation. You can integrate with services like:
 * - SendGrid
 * - Mailgun
 * - AWS SES
 * - Nodemailer with SMTP
 */

import { env } from '../config/environment';

/**
 * Send email (placeholder implementation)
 * TODO: Integrate with your preferred email service
 * @param to - Recipient email
 * @param subject - Email subject
 * @param body - Email body (HTML or text)
 */
export const sendEmail = async (to: string, subject: string, body: string) => {
  // This is a placeholder. Implement actual email sending here.
  console.log('📧 Email to send:');
  console.log(`To: ${to}`);
  console.log(`Subject: ${subject}`);
  console.log(`Body: ${body}`);
  
  // TODO: Implement with your email service
  // Example with Nodemailer:
  /*
  const transporter = nodemailer.createTransport({
    host: env.SMTP_HOST,
    port: env.SMTP_PORT,
    secure: true,
    auth: {
      user: env.SMTP_USER,
      pass: env.SMTP_PASS,
    },
  });
  
  await transporter.sendMail({
    from: env.SMTP_USER,
    to,
    subject,
    html: body,
  });
  */
};

/**
 * Send welcome email to new user
 * @param email - User email
 * @param name - User name
 */
export const sendWelcomeEmail = async (email: string, name: string) => {
  const subject = 'Welcome to Sirius Jobs!';
  const body = `
    <h1>Welcome, ${name}!</h1>
    <p>Thank you for joining Sirius Jobs. We're excited to have you on board.</p>
    <p>Get started by completing your profile.</p>
  `;
  
  await sendEmail(email, subject, body);
};

/**
 * Send email verification
 * @param email - User email
 * @param verificationLink - Verification link
 */
export const sendVerificationEmail = async (email: string, verificationLink: string) => {
  const subject = 'Verify your email address';
  const body = `
    <h1>Verify Your Email</h1>
    <p>Click the link below to verify your email address:</p>
    <a href="${verificationLink}">${verificationLink}</a>
    <p>This link will expire in 24 hours.</p>
  `;
  
  await sendEmail(email, subject, body);
};

/**
 * Send password reset email
 * @param email - User email
 * @param resetLink - Password reset link
 */
export const sendPasswordResetEmail = async (email: string, resetLink: string) => {
  const subject = 'Reset your password';
  const body = `
    <h1>Reset Your Password</h1>
    <p>Click the link below to reset your password:</p>
    <a href="${resetLink}">${resetLink}</a>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request this, please ignore this email.</p>
  `;
  
  await sendEmail(email, subject, body);
};

/**
 * Send subscription expiry reminder
 * @param email - User email
 * @param name - User name
 * @param daysRemaining - Days until expiry
 */
export const sendSubscriptionExpiryReminder = async (
  email: string,
  name: string,
  daysRemaining: number
) => {
  const subject = 'Your subscription is expiring soon';
  const body = `
    <h1>Hi ${name},</h1>
    <p>Your subscription will expire in ${daysRemaining} days.</p>
    <p>Renew now to continue enjoying uninterrupted service.</p>
    <a href="${env.FRONTEND_URL}/renew">Renew Subscription</a>
  `;
  
  await sendEmail(email, subject, body);
};

/**
 * Send consultation session details to client
 * @param email - Client email
 * @param sessionToken - Session token
 * @param professionalName - Professional name
 */
export const sendConsultationSessionEmail = async (
  email: string,
  sessionToken: string,
  professionalName: string,
  sessionId?: string
) => {
  const subject = 'Your Consultation Session is Ready';
  // Link goes to the session page with the sessionId; token is stored in localStorage on the verify page
  const sessionLink = sessionId
    ? `${env.FRONTEND_URL}/consultation-session.html?sessionId=${sessionId}`
    : `${env.FRONTEND_URL}/consultation-session.html`;

  const body = `
    <h1>Your Consultation is Ready!</h1>
    <p>Your paid consultation session with ${professionalName} is now active.</p>
    <p><strong>Click the link below to enter your session:</strong></p>
    <p><a href="${sessionLink}">${sessionLink}</a></p>
    <p><strong>Important:</strong> Save this link — it is your private access to this session. The timer starts when you open it.</p>
    <p>Sessions are text-only. You can extend your session by 1-hour blocks from inside the chat.</p>
  `;

  await sendEmail(email, subject, body);
};

/**
 * Send job application notification to employer
 * @param email - Employer email
 * @param jobTitle - Job title
 * @param workerName - Worker name
 */
export const sendJobApplicationNotification = async (
  email: string,
  jobTitle: string,
  workerName: string
) => {
  const subject = 'New Job Application';
  const body = `
    <h1>New Application Received</h1>
    <p>${workerName} has applied to your job posting: <strong>${jobTitle}</strong></p>
    <p>Login to your dashboard to review the application.</p>
    <a href="${env.FRONTEND_URL}/employer/dashboard">View Dashboard</a>
  `;
  
  await sendEmail(email, subject, body);
};

/**
 * Send hire notification to worker
 * @param email - Worker email
 * @param jobTitle - Job title
 * @param employerName - Employer name
 */
export const sendHireNotification = async (
  email: string,
  jobTitle: string,
  employerName: string
) => {
  const subject = 'Congratulations! You got hired';
  const body = `
    <h1>Congratulations!</h1>
    <p>${employerName} has accepted your application for: <strong>${jobTitle}</strong></p>
    <p>Login to your dashboard for more details.</p>
    <a href="${env.FRONTEND_URL}/worker/dashboard">View Dashboard</a>
  `;
  
  await sendEmail(email, subject, body);
};
