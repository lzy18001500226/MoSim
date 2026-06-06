import * as schema from "@achat/database/schema";
import { betterAuth, type BetterAuthOptions } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import {
  admin,
  apiKey,
  captcha,
  emailOTP,
  openAPI,
  organization,
  twoFactor,
  username,
} from "better-auth/plugins";
import { passkey } from "better-auth/plugins/passkey";
import db from "./database";
import { v7 as uuidv7 } from "uuid";

const authConfig = {
  appName: "AChat",
  trustedOrigins: ["http://localhost:5173"],
  plugins: [
    openAPI(),
    username(),
    twoFactor(),
    passkey(),
    admin(),
    apiKey(),
    organization(),
    // emailOTP({
    //   async sendVerificationOTP({ email, otp, type }) {
    //     const inngest = await getTenantInngest(tenantId);
    //     if (type === "sign-in") {
    //       // Send the OTP for sign-in
    //     } else if (type === "email-verification") {
    //       await inngest.send({
    //         name: "auth/email.verified",
    //         data: {
    //           email,
    //           otp,
    //         },
    //       });
    //     } else if (type === "forget-password") {
    //       // Send the OTP for password reset
    //     }
    //   },
    //   otpLength: 6,
    //   expiresIn: 600,
    //   sendVerificationOnSignUp: true,
    // }),
    // env.CF_TURNSTILE_SECRET_KEY &&
    // 	captcha({
    // 		provider: "cloudflare-turnstile",
    // 		secretKey: env.CF_TURNSTILE_SECRET_KEY,
    // 	}),
  ],
  database: drizzleAdapter(db, {
    provider: "pg",
    schema: {
      user: schema.user,
      session: schema.session,
      account: schema.account,
      verification: schema.verification,
    },
  }),
  // account: {
  //   accountLinking: {
  //     enabled: true,
  //     trustedProviders: ["google", "github"],
  //     allowDifferentEmails: true,
  //   },
  // },

  // databaseHooks: {
  // session: {
  //   create: {
  //     before: async (session) => {
  //       const organization = await getActiveOrganization(session.userId);
  //       return {
  //         data: {
  //           ...session,
  //           activeOrganizationId: organization.id,
  //         },
  //       };
  //     },
  //   },
  // },
  // },
  advanced: {
    database: {
      generateId: () => uuidv7(),
    },
  },
  emailVerification: {
    sendVerificationEmail: async ({ user, url, token }) => {
      // Send verification email to user
    },
    sendOnSignUp: false,
    autoSignInAfterVerification: true,
    expiresIn: 10 * 60, // 10 minutes
  },
  emailAndPassword: {
    enabled: true,
    // Not check here, but after signin/signup will check verification status
    // If not verified, will trigger otp verification in server and client will turn to otp verification page
    // requireEmailVerification: false,
    minPasswordLength: 8,
    maxPasswordLength: 128,
    autoSignIn: true,
    sendResetPassword: async ({ user, url, token }) => {
      // Send reset password email
    },
    resetPasswordTokenExpiresIn: 3600, // 1 hour
  },
  socialProviders: {
    github: {
      enabled: !!(
        process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET
      ),
      clientId: process.env.GITHUB_CLIENT_ID as string,
      clientSecret: process.env.GITHUB_CLIENT_SECRET as string,
    },
    google: {
      enabled: !!(
        process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET
      ),
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    },
  },
} satisfies BetterAuthOptions;
export const auth: ReturnType<typeof betterAuth<typeof authConfig>> =
  betterAuth(authConfig);

export type Auth = typeof auth;
export type AuthSession = Auth["$Infer"]["Session"];
