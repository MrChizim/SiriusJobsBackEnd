/**
 * Admin Controller
 * Handle all admin-related requests
 */

import { Response } from 'express';
import { User } from '../models/User.model';
import { ProfessionalProfile } from '../models/ProfessionalProfile.model';
import { ConsultationSession } from '../models/ConsultationSession.model';
import { sendSuccess, sendError, sendNotFound } from '../utils/response.util';
import { asyncHandler } from '../middleware/error.middleware';
import { generateAccessToken } from '../utils/jwt.util';

/**
 * Admin login — password-only, no database user required
 * POST /api/admin/login
 */
export const adminLogin = asyncHandler(async (req: any, res: Response) => {
  const { password } = req.body;
  const adminPassword = process.env.ADMIN_PASSWORD;

  if (!adminPassword) {
    return sendError(res, 'Admin access not configured', 503);
  }

  if (!password || password !== adminPassword) {
    return sendError(res, 'Invalid credentials', 401);
  }

  const token = generateAccessToken({
    userId: 'admin',
    email: 'admin@siriusjobs.internal',
    accountType: 'admin' as any,
  });

  return sendSuccess(res, { token }, 'Admin access granted');
});

/**
 * Get platform stats
 * GET /api/admin/stats
 */
export const getStats = asyncHandler(async (req: any, res: Response) => {
  const [totalUsers, workerCount, employerCount, professionalCount, merchantCount,
         totalSessions, activeSessions, pendingSessions] = await Promise.all([
    User.countDocuments({}),
    User.countDocuments({ accountType: 'worker' }),
    User.countDocuments({ accountType: 'employer' }),
    User.countDocuments({ accountType: 'professional' }),
    User.countDocuments({ accountType: 'merchant' }),
    ConsultationSession.countDocuments({}),
    ConsultationSession.countDocuments({ status: 'active' }),
    ConsultationSession.countDocuments({ status: 'pending', paymentStatus: 'completed' }),
  ]);

  // Total revenue from completed consultation payments
  const revenueResult = await ConsultationSession.aggregate([
    { $match: { paymentStatus: 'completed' } },
    { $group: { _id: null, total: { $sum: '$paymentAmount' } } }
  ]);
  const revenueTotal = revenueResult[0]?.total || 0;

  return sendSuccess(res, {
    users: { total: totalUsers, workers: workerCount, employers: employerCount, professionals: professionalCount, merchants: merchantCount },
    sessions: { total: totalSessions, active: activeSessions, pending: pendingSessions },
    revenue: { total: revenueTotal, totalNaira: revenueTotal / 100 },
  });
});

/**
 * Get all users with pagination and filtering
 * GET /api/admin/users?page=1&limit=20&type=&search=
 */
export const getUsers = asyncHandler(async (req: any, res: Response) => {
  const page = parseInt(req.query.page as string) || 1;
  const limit = Math.min(parseInt(req.query.limit as string) || 20, 100);
  const skip = (page - 1) * limit;
  const { type, search } = req.query;

  const filter: any = {};
  if (type) filter.accountType = type;
  if (search) {
    filter.$or = [
      { name: { $regex: search, $options: 'i' } },
      { email: { $regex: search, $options: 'i' } },
    ];
  }

  const [users, total] = await Promise.all([
    User.find(filter).select('-password -refreshToken').sort({ createdAt: -1 }).skip(skip).limit(limit).lean(),
    User.countDocuments(filter),
  ]);

  return sendSuccess(res, { users, total, page, pages: Math.ceil(total / limit) });
});

/**
 * Suspend a user
 * POST /api/admin/users/:userId/suspend
 */
export const suspendUser = asyncHandler(async (req: any, res: Response) => {
  const { userId } = req.params;
  const user = await User.findByIdAndUpdate(userId, { isActive: false }, { new: true }).select('-password -refreshToken');
  if (!user) return sendNotFound(res, 'User not found');
  return sendSuccess(res, { user }, 'User suspended');
});

/**
 * Unsuspend a user
 * POST /api/admin/users/:userId/unsuspend
 */
export const unsuspendUser = asyncHandler(async (req: any, res: Response) => {
  const { userId } = req.params;
  const user = await User.findByIdAndUpdate(userId, { isActive: true }, { new: true }).select('-password -refreshToken');
  if (!user) return sendNotFound(res, 'User not found');
  return sendSuccess(res, { user }, 'User unsuspended');
});

/**
 * Get consultation sessions with pagination and filtering
 * GET /api/admin/sessions?page=1&limit=20&status=
 */
export const getSessions = asyncHandler(async (req: any, res: Response) => {
  const page = parseInt(req.query.page as string) || 1;
  const limit = Math.min(parseInt(req.query.limit as string) || 20, 100);
  const skip = (page - 1) * limit;
  const { status } = req.query;

  const filter: any = { paymentStatus: 'completed' };
  if (status) filter.status = status;

  const [sessions, total] = await Promise.all([
    ConsultationSession.find(filter).sort({ createdAt: -1 }).skip(skip).limit(limit).lean(),
    ConsultationSession.countDocuments(filter),
  ]);

  return sendSuccess(res, { sessions, total, page, pages: Math.ceil(total / limit) });
});

/**
 * Get professionals pending verification
 * GET /api/admin/professionals/pending
 */
export const getPendingVerifications = asyncHandler(async (req: any, res: Response) => {
  const profiles = await ProfessionalProfile.find({ isVerified: false })
    .sort({ createdAt: -1 })
    .limit(50)
    .lean();

  // Fetch user details for each
  const userIds = profiles.map(p => p.userId);
  const users = await User.find({ _id: { $in: userIds } }).select('name email createdAt').lean();
  const userMap: Record<string, any> = {};
  users.forEach(u => { userMap[u._id.toString()] = u; });

  const result = profiles.map(p => ({
    ...p,
    user: userMap[p.userId] || null,
  }));

  return sendSuccess(res, { profiles: result });
});

/**
 * Verify a professional profile
 * POST /api/admin/professionals/:profileId/verify
 */
export const verifyProfessional = asyncHandler(async (req: any, res: Response) => {
  const { profileId } = req.params;
  const profile = await ProfessionalProfile.findByIdAndUpdate(
    profileId,
    { isVerified: true },
    { new: true }
  );
  if (!profile) return sendNotFound(res, 'Profile not found');
  return sendSuccess(res, { profile }, 'Professional verified');
});

/**
 * Remove professional verification
 * POST /api/admin/professionals/:profileId/unverify
 */
export const unverifyProfessional = asyncHandler(async (req: any, res: Response) => {
  const { profileId } = req.params;
  const profile = await ProfessionalProfile.findByIdAndUpdate(
    profileId,
    { isVerified: false },
    { new: true }
  );
  if (!profile) return sendNotFound(res, 'Profile not found');
  return sendSuccess(res, { profile }, 'Professional verification removed');
});
