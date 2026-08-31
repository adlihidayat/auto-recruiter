/**
 * What: Create Workspace / Create Account feature view component.
 * Why: Renders create account interface with password visibility toggle & team size dropdown.
 * Boundaries: Rendered on /create-account route.
 */

"use client";

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
} from "lucide-react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function CreateAccountView() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [country, setCountry] = useState("Indonesia");
  const [companySize, setCompanySize] = useState("11-50");
  const [email, setEmail] = useState("");
  const [step, setStep] = useState<"workspace" | "credentials">("workspace");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (step === "workspace") {
      setStep("credentials");
    } else {
      router.push("/");
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
            <p className="text-sm text-gray-600 font-medium mb-8">
              {step === "workspace"
                ? "Set up your organization and preferred team settings."
                : "Enter your work email to finish registration."}
            </p>

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
                    onChange={(e) => setUsername(e.target.value)}
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

                {/* Country & Company Size Grid (Replaced Currency with Company Size) */}
                <div className="grid grid-cols-2 gap-3 mb-10">
                  <div>
                    <label className="text-sm font-semibold text-[#191919] mb-1.5 block">
                      Country
                    </label>
                    <div className="relative">
                      <select
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md px-3.5 py-2 text-xs font-semibold text-[#191919] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow appearance-none cursor-pointer pr-8"
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
                      Company Size
                    </label>
                    <div className="relative">
                      <select
                        value={companySize}
                        onChange={(e) => setCompanySize(e.target.value)}
                        className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md px-3.5 py-2 text-xs font-semibold text-[#191919] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow appearance-none cursor-pointer pr-8"
                      >
                        <option value="1-10">1-10 employees</option>
                        <option value="11-50">11-50 employees</option>
                        <option value="51-200">51-200 employees</option>
                        <option value="200+">200+ employees</option>
                      </select>
                      <ChevronDown className="w-3.5 h-3.5 text-[#646464] absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
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
                  className="w-full bg-[#191919] hover:bg-black text-white text-sm font-semibold py-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2 mt-4"
                >
                  <span>Continue</span>
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
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="alex@acedesign.io"
                      className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md pl-10 pr-4 py-2 text-sm font-medium text-[#191919] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <button
                    type="button"
                    onClick={() => setStep("workspace")}
                    className="text-gray-600 hover:text-gray-900 font-semibold cursor-pointer"
                  >
                    ← Back to workspace setup
                  </button>
                </div>

                <button
                  type="submit"
                  className="w-full bg-[#191919] hover:bg-black text-white text-sm font-semibold py-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2 mt-4"
                >
                  <span>Create Account</span>
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
