"use client";

import { useMemo, useState, useTransition } from "react";
import type { ComponentType } from "react";
import { ArrowRight, CheckCircle2, CircleHelp, FileText, GraduationCap, HeartPulse, Home, IndianRupee, Loader2, MapPin, Search, ShieldCheck } from "lucide-react";
import { askYojana, checkEligibility, type ProfileInput, type SchemeMatch } from "@/lib/api";
import { Button, Card, CardContent, Field, Input, Label, Select, Textarea } from "@/components/ui";

const states = [
  "West Bengal",
  "Maharashtra",
  "Karnataka",
  "Tamil Nadu",
  "Odisha",
  "Uttar Pradesh",
  "Delhi",
  "Bihar",
  "Rajasthan",
  "Gujarat",
  "Kerala",
  "Punjab",
  "Assam",
  "All India"
];

const categories = ["General", "OBC", "SC", "ST", "EWS", "Minority"];

const initialProfile: ProfileInput = {
  age: 21,
  gender: "Female",
  state: "West Bengal",
  district: "",
  annual_income: 180000,
  category: "OBC",
  student: true,
  disability: false,
  occupation: "Student",
  education_level: "Undergraduate"
};

const sampleSchemes = [
  {
    icon: GraduationCap,
    name: "PM Scholarship Scheme",
    ministry: "Education support",
    note: "Financial help for eligible students."
  },
  {
    icon: HeartPulse,
    name: "Ayushman Bharat Yojana",
    ministry: "Health support",
    note: "Health coverage for eligible families."
  },
  {
    icon: Home,
    name: "PM Awas Yojana",
    ministry: "Housing support",
    note: "Support for building or improving a home."
  }
];

export default function HomePage() {
  const [profile, setProfile] = useState<ProfileInput>(initialProfile);
  const [matches, setMatches] = useState<SchemeMatch[]>([]);
  const [searched, setSearched] = useState(false);
  const [question, setQuestion] = useState("I want a scholarship for my daughter");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  const incomeLabel = useMemo(() => new Intl.NumberFormat("en-IN").format(profile.annual_income), [profile.annual_income]);

  function updateProfile<K extends keyof ProfileInput>(key: K, value: ProfileInput[K]) {
    setProfile((current) => ({ ...current, [key]: value }));
  }

  function findSchemes() {
    setError("");
    setSearched(true);
    startTransition(async () => {
      try {
        const result = await checkEligibility(profile);
        setMatches(result.matches ?? []);
      } catch {
        setError("We could not check schemes right now. Please try again in a moment.");
      }
    });
  }

  function askQuestion() {
    setError("");
    startTransition(async () => {
      try {
        const result = await askYojana(question, profile);
        setAnswer(result.answer);
      } catch {
        setError("We could not answer this question right now. Please try again.");
      }
    });
  }

  return (
    <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 pb-24 pt-6 sm:px-6 md:pb-6 lg:px-8">
      <section className="grid gap-6 lg:grid-cols-[0.9fr_1fr]">
        <Card className="overflow-hidden rounded-2xl">
          <CardContent className="p-5 sm:p-8">
            <div className="mb-6 flex items-start gap-4 sm:mb-8">
              <span className="grid size-12 shrink-0 place-items-center rounded-full bg-saffron/10 text-saffron sm:size-14">
                <Search aria-hidden="true" />
              </span>
              <div>
                <h1 className="text-2xl font-extrabold leading-tight tracking-tight text-foreground sm:text-4xl">Find government schemes for you</h1>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground sm:mt-3 sm:text-base sm:leading-7">
                  Answer a few questions. We will show schemes that may fit your profile.
                </p>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 sm:gap-5">
              <Field>
                <Label htmlFor="state">State</Label>
                <div className="relative">
                  <MapPin className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
                  <Select id="state" className="pl-10" value={profile.state} onChange={(event) => updateProfile("state", event.target.value)}>
                    {states.map((state) => (
                      <option key={state}>{state}</option>
                    ))}
                  </Select>
                </div>
              </Field>

              <Field>
                <Label htmlFor="age">Age</Label>
                <Input id="age" type="number" min={1} max={120} value={profile.age} onChange={(event) => updateProfile("age", Number(event.target.value))} />
              </Field>

              <Field className="sm:col-span-2">
                <Label htmlFor="income">Annual family income</Label>
                <div className="relative">
                  <IndianRupee className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
                  <Input
                    id="income"
                    className="pl-10"
                    type="number"
                    min={0}
                    value={profile.annual_income}
                    onChange={(event) => updateProfile("annual_income", Number(event.target.value))}
                  />
                </div>
                <p className="text-xs text-muted-foreground">Current value: Rs. {incomeLabel}</p>
              </Field>

              <Field className="sm:col-span-2">
                <Label htmlFor="category">Category</Label>
                <Select id="category" value={profile.category} onChange={(event) => updateProfile("category", event.target.value)}>
                  {categories.map((category) => (
                    <option key={category}>{category}</option>
                  ))}
                </Select>
              </Field>

              <Field>
                <Label htmlFor="student">Student</Label>
                <Select id="student" value={profile.student ? "Yes" : "No"} onChange={(event) => updateProfile("student", event.target.value === "Yes")}>
                  <option>Yes</option>
                  <option>No</option>
                </Select>
              </Field>

              <Field>
                <Label htmlFor="disability">Disability</Label>
                <Select id="disability" value={profile.disability ? "Yes" : "No"} onChange={(event) => updateProfile("disability", event.target.value === "Yes")}>
                  <option>No</option>
                  <option>Yes</option>
                </Select>
              </Field>
            </div>

            <Button className="mt-6 h-12 w-full rounded-xl text-base font-bold sm:mt-7 sm:h-14" onClick={findSchemes} disabled={isPending}>
              {isPending ? <Loader2 data-icon="inline-start" className="animate-spin" aria-hidden="true" /> : <Search data-icon="inline-start" aria-hidden="true" />}
              Find schemes
            </Button>

            <div className="mt-4 rounded-xl border border-sky/80 bg-sky/60 p-4">
              <div className="flex gap-3">
                <ShieldCheck className="shrink-0 text-primary" aria-hidden="true" />
                <div>
                  <p className="text-sm font-semibold text-foreground">Your information is used only to find relevant schemes.</p>
                  <p className="mt-1 text-sm text-muted-foreground">You can try the finder without creating an account.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex flex-col gap-5">
          <section className="overflow-hidden rounded-2xl border border-primary/10 bg-gradient-to-r from-green-50 via-white to-orange-50">
            <div className="grid gap-4 p-6 sm:p-8 md:grid-cols-[1fr_240px]">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight text-foreground">We are here to help you</h2>
                <p className="mt-3 max-w-md text-base leading-7 text-muted-foreground">
                  Get personalised scheme suggestions in simple steps.
                </p>
                <div className="mt-6 grid gap-3 sm:grid-cols-3">
                  {["Free to use", "Simple words", "Official sources"].map((item) => (
                    <span key={item} className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
                      <CheckCircle2 aria-hidden="true" />
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              <div className="hidden items-end justify-end md:flex">
                <div className="relative h-40 w-56 rounded-2xl bg-white/70 p-4 shadow-sm">
                  <div className="absolute right-4 top-4 h-10 w-16 rounded-sm bg-gradient-to-b from-orange-400 via-white to-green-600" />
                  <div className="absolute bottom-4 left-5 h-20 w-12 rounded-full bg-primary/15" />
                  <div className="absolute bottom-4 left-20 h-28 w-12 rounded-full bg-saffron/20" />
                  <div className="absolute bottom-4 right-10 h-24 w-12 rounded-full bg-sky" />
                </div>
              </div>
            </div>
          </section>

          <Card className="rounded-2xl">
            <CardContent className="p-6">
              <div className="mb-5 flex items-center justify-between gap-3">
                <h2 className="text-xl font-extrabold">May be eligible</h2>
                <a href="/schemes" className="inline-flex items-center gap-1 text-sm font-semibold text-primary">
                  View all schemes <ArrowRight aria-hidden="true" />
                </a>
              </div>

              <div className="divide-y divide-border">
                {searched && matches.length > 0
                  ? matches.map((scheme) => <SchemeRow key={scheme.id} name={scheme.name} ministry={scheme.ministry || scheme.state} note={scheme.reason} />)
                  : sampleSchemes.map((scheme) => <SchemeRow key={scheme.name} name={scheme.name} ministry={scheme.ministry} note={scheme.note} icon={scheme.icon} />)}
              </div>
              {searched && matches.length === 0 ? <p className="mt-4 rounded-xl bg-muted p-4 text-sm text-muted-foreground">No exact matches are indexed yet. You can still ask a question below.</p> : null}
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-3">
            <InfoTile icon={FileText} title="Documents needed" text="Check what papers may be required." />
            <InfoTile icon={CheckCircle2} title="How to apply" text="See online or offline steps." />
            <InfoTile icon={CircleHelp} title="Need help?" text="Ask in simple words." />
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-surface p-5 shadow-panel">
        <div className="grid gap-4 lg:grid-cols-[260px_1fr_auto] lg:items-end">
          <div>
            <h2 className="text-lg font-extrabold">Ask a question</h2>
            <p className="mt-1 text-sm text-muted-foreground">Type your question in simple words.</p>
          </div>
          <Textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="e.g., I want a scholarship for my daughter" />
          <Button className="h-12 rounded-xl px-6" onClick={askQuestion} disabled={isPending}>
            Ask
            <ArrowRight data-icon="inline-end" aria-hidden="true" />
          </Button>
        </div>
        {answer ? <div className="mt-4 whitespace-pre-wrap rounded-xl border border-border bg-background p-4 text-sm leading-6">{answer}</div> : null}
        {error ? <p className="mt-4 rounded-xl border border-warning/30 bg-warning/10 p-4 text-sm text-foreground">{error}</p> : null}
      </section>

      <section className="grid gap-4 rounded-2xl border border-border bg-surface p-5 sm:grid-cols-3">
        <HelpItem title="Find support" text="Scholarships, housing, health, farming, pension, and more." />
        <HelpItem title="Use your language" text="You can ask questions in simple everyday words." />
        <HelpItem title="Check before applying" text="Always confirm final details on the official website." />
      </section>

      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-surface/95 p-4 shadow-2xl backdrop-blur md:hidden">
        <Button className="h-12 w-full rounded-xl text-base font-bold" onClick={findSchemes} disabled={isPending}>
          {isPending ? <Loader2 data-icon="inline-start" className="animate-spin" aria-hidden="true" /> : <Search data-icon="inline-start" aria-hidden="true" />}
          Find schemes
        </Button>
      </div>
    </div>
  );
}

function SchemeRow({
  name,
  ministry,
  note,
  icon: Icon = LandmarkIcon
}: {
  name: string;
  ministry?: string;
  note?: string;
  icon?: ComponentType<{ className?: string; "aria-hidden"?: boolean }>;
}) {
  return (
    <article className="grid gap-3 py-4 sm:grid-cols-[48px_1fr_auto] sm:items-center">
      <span className="grid size-12 place-items-center rounded-xl bg-primary/10 text-primary">
        <Icon aria-hidden={true} />
      </span>
      <div>
        <h3 className="font-bold text-foreground">{name}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{ministry}</p>
      </div>
      <div className="sm:max-w-72">
        <p className="text-sm text-muted-foreground">{note}</p>
        <span className="mt-2 inline-flex rounded-md bg-primary/10 px-3 py-1 text-xs font-bold text-primary">May be eligible</span>
      </div>
    </article>
  );
}

function InfoTile({ icon: Icon, title, text }: { icon: ComponentType<{ className?: string; "aria-hidden"?: boolean }>; title: string; text: string }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-4 shadow-panel">
      <Icon className="text-saffron" aria-hidden={true} />
      <h3 className="mt-3 font-bold">{title}</h3>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">{text}</p>
    </div>
  );
}

function HelpItem({ title, text }: { title: string; text: string }) {
  return (
    <div className="border-border sm:border-r sm:last:border-r-0">
      <h3 className="font-bold">{title}</h3>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">{text}</p>
    </div>
  );
}

function LandmarkIcon(props: { className?: string; "aria-hidden"?: boolean }) {
  return <GraduationCap {...props} />;
}
