"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Eye, EyeOff, ArrowRight, Loader2, Check } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Logo } from "@/components/logo";
import { useAuthStore } from "@/lib/stores";

const signupSchema = z.object({
  fullName: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number"),
});

type SignupFormData = z.infer<typeof signupSchema>;

const passwordRequirements = [
  { label: "At least 8 characters", regex: /.{8,}/ },
  { label: "One uppercase letter", regex: /[A-Z]/ },
  { label: "One lowercase letter", regex: /[a-z]/ },
  { label: "One number", regex: /[0-9]/ },
];

export default function SignupPage() {
  const router = useRouter();
  const { signup, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      fullName: "",
      email: "",
      password: "",
    },
  });

  const password = form.watch("password");

  const onSubmit = async (data: SignupFormData) => {
    try {
      await signup(data.email, data.password, data.fullName);
      toast.success("Account created successfully!");
      router.push("/dashboard");
    } catch {
      toast.error("Failed to create account. Please try again.");
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left: Visual Panel */}
      <div className="hidden lg:flex lg:w-1/2 lg:flex-col lg:items-center lg:justify-center bg-gradient-to-br from-chart-2/5 via-primary/5 to-chart-4/5 relative overflow-hidden">
        {/* Abstract shapes */}
        <div className="absolute top-32 right-20 h-80 w-80 rounded-full bg-chart-2/10 blur-3xl" />
        <div className="absolute bottom-32 left-20 h-72 w-72 rounded-full bg-primary/10 blur-3xl" />

        <div className="relative z-10 max-w-lg text-center px-8">
          <div className="mb-10 space-y-6">
            {[
              { icon: "📱", text: "Create TikTok & Reels in minutes" },
              { icon: "🤖", text: "AI-powered script generation" },
              { icon: "🎙️", text: "Natural text-to-speech voices" },
              { icon: "✨", text: "Auto-captions & styling" },
            ].map((feature, i) => (
              <div
                key={i}
                className="flex items-center gap-4 rounded-2xl bg-card/50 p-4 backdrop-blur-sm border border-border/50 shadow-sm"
              >
                <span className="text-2xl">{feature.icon}</span>
                <span className="font-medium">{feature.text}</span>
              </div>
            ))}
          </div>

          <p className="text-sm text-muted-foreground">
            Join thousands of creators automating their content workflow
          </p>
        </div>
      </div>

      {/* Right: Form Panel */}
      <div className="flex w-full flex-col justify-center px-6 lg:w-1/2 lg:px-16 xl:px-24">
        <div className="mx-auto w-full max-w-md">
          <Logo className="mb-12" />

          <div className="mb-8">
            <h1 className="text-3xl font-semibold tracking-tight">
              Create your account
            </h1>
            <p className="mt-2 text-muted-foreground">
              Start creating viral videos in minutes
            </p>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
              <FormField
                control={form.control}
                name="fullName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      Full name
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="John Doe"
                        className="h-12 bg-secondary/50 border-0 focus-visible:ring-2"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">Email</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="you@example.com"
                        className="h-12 bg-secondary/50 border-0 focus-visible:ring-2"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      Password
                    </FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input
                          type={showPassword ? "text" : "password"}
                          placeholder="Create a strong password"
                          className="h-12 bg-secondary/50 border-0 pr-12 focus-visible:ring-2"
                          {...field}
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                        >
                          {showPassword ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Password requirements */}
              {password && (
                <div className="space-y-2">
                  {passwordRequirements.map((req, i) => (
                    <div
                      key={i}
                      className={`flex items-center gap-2 text-sm transition-colors ${
                        req.regex.test(password)
                          ? "text-chart-2"
                          : "text-muted-foreground"
                      }`}
                    >
                      <Check
                        className={`h-3.5 w-3.5 ${
                          req.regex.test(password) ? "opacity-100" : "opacity-30"
                        }`}
                      />
                      {req.label}
                    </div>
                  ))}
                </div>
              )}

              <Button
                type="submit"
                className="h-12 w-full text-base font-medium"
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <>
                    Create account
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          </Form>

          <p className="mt-8 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-primary hover:underline"
            >
              Sign in
            </Link>
          </p>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            By creating an account, you agree to our{" "}
            <Link href="/terms" className="underline hover:text-foreground">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="/privacy" className="underline hover:text-foreground">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
