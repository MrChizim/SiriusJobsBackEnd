/**
 * Merchant Profile Model
 * For businesses selling products/services on the marketplace
 */

import mongoose, { Schema, Model, Document } from 'mongoose';
import { IMerchantProfile, MerchantPackage, SubscriptionStatus } from '../types';

interface IMerchantProfileDocument extends Document, IMerchantProfile {
  calculateSubscription(packageType: MerchantPackage): {
    amount: number;
    duration: number;
    maxImages: number;
  };
  isSubscriptionActive(): boolean;
}

const merchantProfileSchema = new Schema<IMerchantProfileDocument>(
  {
    userId: {
      type: String,
      required: true,
      unique: true,
      ref: 'User',
    },

    businessName: {
      type: String,
      required: true,
      trim: true,
      maxlength: [200, 'Business name too long'],
    },

    businessLogo: {
      type: String,
      default: null,
    },

    businessImages: {
      type: [String],
      default: [],
      validate: {
        validator: function(images: string[]) {
          return images.length <= this.subscription.maxImages;
        },
        message: 'Exceeded maximum allowed images for your subscription',
      },
    },

    description: {
      type: String,
      required: false, // Made optional - to be filled in dashboard
      trim: true,
      maxlength: [2000, 'Description too long'],
    },

    category: {
      type: String,
      required: true,
      trim: true,
    },

    location: {
      type: String,
      trim: true,
    },

    whatsapp: {
      type: String,
      trim: true,
    },

    instagram: {
      type: String,
      trim: true,
    },

    email: {
      type: String,
      trim: true,
      lowercase: true,
    },

    website: {
      type: String,
      trim: true,
    },

    subscription: {
      package: {
        type: String,
        enum: ['3months', '6months', '12months'],
        required: false, // Made optional - to be selected in dashboard
      },
      status: {
        type: String,
        enum: ['active', 'expired', 'pending'],
        default: 'pending',
      },
      startDate: Date,
      endDate: Date,
      amount: {
        type: Number,
        required: false, // Made optional - calculated when package is selected
      },
      maxImages: {
        type: Number,
        default: 20, // All packages now get same max images
      },
    },

    // CAC registration for recommended badge
    cacNumber: {
      type: String,
      trim: true,
    },

    hasRecommendedBadge: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  }
);

// Note: userId already has unique index from field definition
merchantProfileSchema.index({ category: 1 });
merchantProfileSchema.index({ 'subscription.status': 1 });

/**
 * Calculate subscription details based on package
 * All packages have same features - only difference is price discount
 */
merchantProfileSchema.methods.calculateSubscription = function(packageType: MerchantPackage) {
  const monthlyRate = 10000; // ₦10,000/month
  const maxImages = 20;

  switch (packageType) {
    case '3months':
      return {
        amount: 30000,  // ₦10,000 × 3
        duration: 3,
        maxImages,
      };
    case '6months':
      return {
        amount: 57000,  // 5% discount off ₦60,000
        duration: 6,
        maxImages,
      };
    case '12months':
      return {
        amount: 108000, // 10% discount off ₦120,000
        duration: 12,
        maxImages,
      };
    default:
      return {
        amount: monthlyRate * 3,
        duration: 3,
        maxImages,
      };
  }
};

/**
 * Check if subscription is active
 */
merchantProfileSchema.methods.isSubscriptionActive = function(): boolean {
  if (this.subscription.status !== 'active') return false;
  if (!this.subscription.endDate) return false;
  return new Date() < this.subscription.endDate;
};

export const MerchantProfile: Model<IMerchantProfileDocument> = mongoose.model<IMerchantProfileDocument>(
  'MerchantProfile',
  merchantProfileSchema
);
