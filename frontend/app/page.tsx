import Link from "next/link";
import {
  ArrowRight,
  Play,
  Sparkles,
  Zap,
  Video,
  FileText,
  Mic,
  Check,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Logo } from "@/components/logo";

const features = [
  {
    icon: FileText,
    title: "Smart Content Scraping",
    description:
      "Automatically extract and summarize content from Reddit, Twitter, StackOverflow, and more.",
  },
  {
    icon: Sparkles,
    title: "AI Script Generation",
    description:
      "Transform raw content into engaging, platform-optimized video scripts using AI.",
  },
  {
    icon: Mic,
    title: "Natural Text-to-Speech",
    description:
      "Generate professional voiceovers with multiple voice styles and tones.",
  },
  {
    icon: Video,
    title: "Automated Video Assembly",
    description:
      "Combine visuals, captions, and audio into polished short-form videos.",
  },
];

const platforms = [
  { name: "TikTok", emoji: "🎵" },
  { name: "YouTube Shorts", emoji: "📺" },
  { name: "Instagram Reels", emoji: "📸" },
  { name: "YouTube", emoji: "▶️" },
];

const pricingTiers = [
  {
    name: "Free",
    price: "$0",
    description: "Perfect for trying out",
    credits: "10 credits/month",
    features: [
      "Basic content scraping",
      "AI script generation",
      "Standard TTS voices",
      "720p video export",
    ],
    cta: "Get Started",
    popular: false,
  },
  {
    name: "Pro",
    price: "$19",
    description: "For content creators",
    credits: "100 credits/month",
    features: [
      "Advanced scraping",
      "Priority AI generation",
      "Premium TTS voices",
      "1080p video export",
      "Custom templates",
      "Priority support",
    ],
    cta: "Start Free Trial",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For teams & agencies",
    credits: "Unlimited credits",
    features: [
      "Everything in Pro",
      "API access",
      "Team collaboration",
      "White-label exports",
      "Dedicated support",
      "Custom integrations",
    ],
    cta: "Contact Sales",
    popular: false,
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Logo />
          <div className="hidden md:flex items-center gap-8">
            <a
              href="#features"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              How it Works
            </a>
            <a
              href="#pricing"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Pricing
            </a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                Sign in
              </Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium mb-8">
            <Zap className="h-4 w-4 text-primary" />
            <span>AI-Powered Video Creation</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
            Turn any content into{" "}
            <span className="text-gradient">viral videos</span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            Transform Reddit threads, tweets, and more into engaging short-form
            videos. Automated scripts, voiceovers, and editing — all powered by
            AI.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link href="/signup">
              <Button size="lg" className="h-14 px-8 text-lg gap-2">
                Start Creating Free
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <Button
              variant="outline"
              size="lg"
              className="h-14 px-8 text-lg gap-2"
            >
              <Play className="h-5 w-5" />
              Watch Demo
            </Button>
          </div>

          {/* Platform badges */}
          <div className="flex flex-wrap items-center justify-center gap-3">
            <span className="text-sm text-muted-foreground">Export to:</span>
            {platforms.map((platform) => (
              <div
                key={platform.name}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted text-sm"
              >
                <span>{platform.emoji}</span>
                <span>{platform.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Hero Visual */}
        <div className="max-w-6xl mx-auto mt-20">
          <div className="relative rounded-2xl overflow-hidden bg-gradient-to-br from-primary/5 via-chart-4/5 to-chart-2/5 p-1">
            <div className="rounded-xl bg-card border overflow-hidden">
              <div className="aspect-[16/9] bg-gradient-to-br from-muted to-muted/50 flex items-center justify-center">
                <div className="text-center">
                  <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                    <Play className="h-10 w-10 text-primary" />
                  </div>
                  <p className="text-muted-foreground">
                    Dashboard Preview Coming Soon
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Everything you need to create viral videos
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              From content scraping to final export, TokSmith handles the entire
              video creation pipeline automatically.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div
                  key={i}
                  className="group p-6 rounded-2xl bg-card border hover:border-primary/50 hover:shadow-lg transition-all"
                >
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Create videos in 3 simple steps
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              No video editing skills required. Just paste a URL and let AI do
              the rest.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Paste Your Source",
                description:
                  "Drop a Reddit thread, Twitter post, or any content URL you want to transform.",
              },
              {
                step: "02",
                title: "Customize & Generate",
                description:
                  "Choose your style, voice, and platform. Our AI generates the script and video.",
              },
              {
                step: "03",
                title: "Export & Share",
                description:
                  "Download your polished video ready to post on TikTok, Reels, or Shorts.",
              },
            ].map((item, i) => (
              <div key={i} className="relative">
                <div className="text-6xl font-bold text-primary/10 mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Simple, transparent pricing
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Start free, upgrade when you&apos;re ready. No hidden fees.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {pricingTiers.map((tier, i) => (
              <div
                key={i}
                className={`relative p-6 rounded-2xl bg-card border ${
                  tier.popular
                    ? "border-primary shadow-lg shadow-primary/10 scale-105"
                    : ""
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                    Most Popular
                  </div>
                )}
                <div className="mb-6">
                  <h3 className="text-xl font-semibold">{tier.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {tier.description}
                  </p>
                </div>
                <div className="mb-6">
                  <span className="text-4xl font-bold">{tier.price}</span>
                  {tier.price !== "Custom" && (
                    <span className="text-muted-foreground">/month</span>
                  )}
                  <p className="text-sm text-muted-foreground mt-1">
                    {tier.credits}
                  </p>
                </div>
                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-primary shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Button
                  className="w-full"
                  variant={tier.popular ? "default" : "outline"}
                >
                  {tier.cta}
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to create your first video?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join thousands of creators automating their content workflow.
          </p>
          <Link href="/signup">
            <Button size="lg" className="h-14 px-8 text-lg gap-2">
              Get Started Free
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <Logo />
            <p className="text-sm text-muted-foreground">
              © 2025 TokSmith. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Privacy
              </a>
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Terms
              </a>
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
