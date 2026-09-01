"use client";

/**
 * What: Create Workspace / Create Account feature view component.
 * Why: Renders create account interface connected to FastAPI backend auth endpoints (/api/auth/check-username and /api/auth/register).
 * Boundaries: Rendered on /create-account route.
 */

import React, { useState } from "react";
import Link from "next/link";
import {
  ChevronDown,
  ArrowRight,
  Check,
  Mail,
  Lock,
  Eye,
  EyeOff,
  AlertCircle,
} from "lucide-react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { checkUsernameApi, registerApi } from "@/lib/api/client";

export default function CreateAccountView() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [country, setCountry] = useState("Indonesia");
  const [bornDate, setBornDate] = useState("");
  const [email, setEmail] = useState("");
  const [step, setStep] = useState<"workspace" | "credentials">("workspace");

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (step === "workspace") {
      setIsSubmitting(true);
      try {
        const checkRes = await checkUsernameApi(username);
        if (!checkRes.available) {
          setErrorMessage("Username is already taken. Please choose another.");
          setIsSubmitting(false);
          return;
        }
        setStep("credentials");
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to verify username";
        setErrorMessage(message);
      } finally {
        setIsSubmitting(false);
      }
    } else {
      setIsSubmitting(true);
      try {
        const res = await registerApi({
          username,
          email,
          password,
          country,
          born_date: bornDate || undefined,
        });

        // Set access_token & last_active_at as session cookies (clear on browser shutdown)
        document.cookie = `access_token=${res.access_token}; path=/; SameSite=Lax`;
        document.cookie = `last_active_at=${Date.now()}; path=/; SameSite=Lax`;

        router.push("/");
        router.refresh();
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to create account";
        setErrorMessage(message);
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#F6F6F6] flex flex-col items-center justify-center p-4 md:p-8 font-sans">
      {/* Main Split Container Card */}
      <div className="bg-white border border-gray-200 rounded-3xl p-6 md:py-6 md:pl-6 md:pr-10 max-w-5xl w-full flex gap-8 items-stretch">
        {/* Left Column: Hero Graphic Section */}
        <div className="w-full flex-1 rounded-3xl p-6 relative overflow-hidden flex flex-col justify-end items-center min-h-[380px]">
          <Image
            src={"/signin-bg.webp"}
            alt=""
            fill
            priority
            className="absolute z-0 top-0 left-0"
          />

          <div className="z-10 flex flex-col items-center space-y-2 pb-5">
            <Image
              src={"/logo-no-bg.svg"}
              alt="logo"
              width={25}
              height={25}
              className="mb-3"
            />
            <span className="text-sm font-semibold mb-2">Auto Recruiter</span>
            <span className="text-xs font-medium text-gray-600 text-center">
              Build your AI recruiting workspace in seconds
            </span>
          </div>
        </div>

        {/* Right Column: Form Section */}
        <div className="py-12 max-w-110 flex-1">
          <div>
            <h1 className="text-xl font-semibold text-gray-900 mt-2 mb-1">
              {step === "workspace" ? "Create workspace" : "Account details"}
            </h1>
            <p className="text-sm text-gray-600 font-medium mb-6">
              {step === "workspace"
                ? "Set up your organization and preferred team settings."
                : "Enter your work email to finish registration."}
            </p>

            {errorMessage && (
              <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
                <span>{errorMessage}</span>
              </div>
            )}

            {step === "workspace" ? (
              <form onSubmit={handleSubmit} className="">
                {/* Username / Company Name */}
                <div className="mb-6">
                  <label className="text-sm font-semibold text-[#191919] mb-1.5 block">
                    Username
                  </label>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => {
                      setUsername(e.target.value);
                      if (errorMessage) setErrorMessage(null);
                    }}
                    placeholder="e.g. alex_recruiter"
                    className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md px-4 py-2 text-sm font-medium text-[#191919] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
                  />
                </div>

                {/* Password Input with Show/Hide Toggle */}
                <div className="mb-6">
                  <label className="text-sm font-semibold text-[#191919] mb-1.5 block">
                    Password
                  </label>
                  <div className="relative flex items-center">
                    <div className="absolute left-3.5 text-[#646464] pointer-events-none">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md pl-10 pr-10 py-2 text-sm font-medium text-[#191919] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 text-[#646464] hover:text-[#191919] p-1 cursor-pointer transition-colors"
                      title={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Country & Born Date Grid */}
                <div className="grid grid-cols-2 gap-3 mb-10">
                  <div>
                    <label className="text-sm font-semibold text-[#191919] mb-1.5 block">
                      Country
                    </label>
                    <div className="relative">
                      <select
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md px-3.5 py-2 text-sm font-medium text-[#191919] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow appearance-none cursor-pointer pr-8"
                      >
                        <option value="Indonesia">🇮🇩 Indonesia</option>
                        <option value="United States">🇺🇸 United States</option>
                        <option value="Singapore">🇸🇬 Singapore</option>
                        <option value="United Kingdom">
                          🇬🇧 United Kingdom
                        </option>
                      </select>
                      <ChevronDown className="w-3.5 h-3.5 text-[#646464] absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-semibold text-[#191919] mb-1.5 block">
                      Born Date
                    </label>
                    <div className="relative flex items-center">
                      <input
                        type="date"
                        required
                        value={bornDate}
                        onChange={(e) => setBornDate(e.target.value)}
                        className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md px-3 py-1.5 text-sm font-medium text-[#191919] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow cursor-pointer"
                      />
                    </div>
                  </div>
                </div>

                <div className="text-center md:text-left text-xs font-medium text-gray-600 mb-6">
                  Already have a workspace?{" "}
                  <Link
                    href="/login"
                    className="font-bold text-gray-900 underline hover:opacity-60"
                  >
                    Log in
                  </Link>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-[#191919] hover:bg-black text-white text-sm font-semibold py-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2 mt-4 disabled:opacity-50"
                >
                  <span>{isSubmitting ? "Checking..." : "Continue"}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </form>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="text-sm font-semibold text-[#191919] mb-1.5 block">
                    Work Email
                  </label>
                  <div className="relative flex items-center">
                    <div className="absolute left-3.5 text-[#646464] pointer-events-none">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        if (errorMessage) setErrorMessage(null);
                      }}
                      placeholder="alex@acedesign.io"
                      className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md pl-10 pr-4 py-2 text-sm font-medium text-[#191919] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setStep("workspace");
                      setErrorMessage(null);
                    }}
                    className="text-gray-600 hover:text-gray-900 font-semibold cursor-pointer"
                  >
                    ← Back to workspace setup
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-[#191919] hover:bg-black text-white text-sm font-semibold py-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2 mt-4 disabled:opacity-50"
                >
                  <span>{isSubmitting ? "Creating..." : "Create Account"}</span>
                  <Check className="w-4 h-4" />
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
