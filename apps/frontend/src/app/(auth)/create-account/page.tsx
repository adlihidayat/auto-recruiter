import React from "react";
import CreateAccountView from "@/features/auth/components/CreateAccountView";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Create Account | Auto-Recruiter",
  description: "Create a new workspace and account on Auto-Recruiter",
};

export default function CreateAccountPage() {
  return <CreateAccountView />;
}
