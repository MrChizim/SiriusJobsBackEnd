import { Router } from 'express';
import * as adminController from '../controllers/admin.controller';
import { authenticate, authorize } from '../middleware/auth.middleware';

const router = Router();

// Public admin login (password-only, no user account needed)
router.post('/login', adminController.adminLogin);

// All other admin routes require the admin JWT
router.use(authenticate, authorize('admin'));

router.get('/stats', adminController.getStats);
router.get('/users', adminController.getUsers);
router.post('/users/:userId/suspend', adminController.suspendUser);
router.post('/users/:userId/unsuspend', adminController.unsuspendUser);
router.get('/sessions', adminController.getSessions);
router.get('/professionals/pending', adminController.getPendingVerifications);
router.post('/professionals/:profileId/verify', adminController.verifyProfessional);
router.post('/professionals/:profileId/unverify', adminController.unverifyProfessional);

export default router;
