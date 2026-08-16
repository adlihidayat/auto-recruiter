import React from "react";
import SignInView from "@/features/auth/components/SignInView";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sign In | Auto-Recruiter",
  description: "Login to access the Auto-Recruiter HR dashboard",
};

export default function SignInPage() {
  return <SignInView />;
}
