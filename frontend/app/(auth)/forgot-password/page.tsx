"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { ArrowLeft, Loader2, Mail, CheckCircle } from "lucide-react";

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
import { authApi } from "@/lib/api";

const resetSchema = z.object({
  email: z.string().email("Please enter a valid email"),
});

type ResetFormData = z.infer<typeof resetSchema>;

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [isEmailSent, setIsEmailSent] = useState(false);

  const form = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data: ResetFormData) => {
    setIsLoading(true);
    try {
      await authApi.requestPasswordReset(data.email);
      setIsEmailSent(true);
      toast.success("Password reset email sent!");
    } catch {
      toast.error("Failed to send reset email. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md">
        <Logo className="mb-12 justify-center" />

        {!isEmailSent ? (
          <>
            <div className="mb-8 text-center">
              <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Mail className="h-8 w-8 text-primary" />
              </div>
              <h1 className="text-2xl font-semibold tracking-tight">
                Reset your password
              </h1>
              <p className="mt-2 text-muted-foreground">
                Enter your email and we&apos;ll send you a reset link
              </p>
            </div>

            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-5"
              >
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">
                        Email address
                      </FormLabel>
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

                <Button
                  type="submit"
                  className="h-12 w-full text-base font-medium"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    "Send reset link"
                  )}
                </Button>
              </form>
            </Form>
          </>
        ) : (
          <div className="text-center">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-chart-2/10">
              <CheckCircle className="h-8 w-8 text-chart-2" />
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">
              Check your email
            </h1>
            <p className="mt-2 text-muted-foreground">
              We&apos;ve sent a password reset link to{" "}
              <span className="font-medium text-foreground">
                {form.getValues("email")}
              </span>
            </p>

            <Button
              variant="outline"
              className="mt-8 h-12 w-full"
              onClick={() => setIsEmailSent(false)}
            >
              Try a different email
            </Button>
          </div>
        )}

        <Link
          href="/login"
          className="mt-8 flex items-center justify-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to sign in
        </Link>
      </div>
    </div>
  );
}
