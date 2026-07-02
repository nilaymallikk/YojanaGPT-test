"use client";

import { useState, useTransition } from "react";
import { ArrowRight, Loader2, MessageCircleQuestion } from "lucide-react";
import { askYojana, type ProfileInput } from "@/lib/api";
import { Button, Card, CardContent, Field, Input, Label, Select, Textarea } from "@/components/ui";

const defaultProfile: ProfileInput = {
  age: 24,
  gender: "Female",
  state: "West Bengal",
  annual_income: 200000,
  category: "OBC",
  student: true,
  disability: false,
  education_level: "Undergraduate"
};

export default function ChatPage() {
  const [profile, setProfile] = useState(defaultProfile);
  const [question, setQuestion] = useState("Which scholarship can I apply for?");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  function submit() {
    setError("");
    startTransition(async () => {
      try {
        const result = await askYojana(question, profile);
        setAnswer(result.answer);
      } catch {
        setError("We could not answer right now. Please try again.");
      }
    });
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[360px_1fr] lg:px-8">
      <Card className="rounded-2xl">
        <CardContent className="p-6">
          <h1 className="text-2xl font-extrabold">Ask YojanaGPT</h1>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">Share a few details so the answer can be more useful.</p>

          <div className="mt-6 flex flex-col gap-4">
            <Field>
              <Label htmlFor="state">State</Label>
              <Input id="state" value={profile.state} onChange={(event) => setProfile({ ...profile, state: event.target.value })} />
            </Field>
            <Field>
              <Label htmlFor="income">Annual family income</Label>
              <Input id="income" type="number" value={profile.annual_income} onChange={(event) => setProfile({ ...profile, annual_income: Number(event.target.value) })} />
            </Field>
            <Field>
              <Label htmlFor="student">Student</Label>
              <Select id="student" value={profile.student ? "Yes" : "No"} onChange={(event) => setProfile({ ...profile, student: event.target.value === "Yes" })}>
                <option>Yes</option>
                <option>No</option>
              </Select>
            </Field>
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-2xl">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <span className="grid size-12 place-items-center rounded-xl bg-primary/10 text-primary">
              <MessageCircleQuestion aria-hidden="true" />
            </span>
            <div>
              <h2 className="text-2xl font-extrabold">Ask a question</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">Example: “Can I get help for college fees?”</p>
            </div>
          </div>

          <div className="mt-6 flex flex-col gap-4">
            <Textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
            <Button className="h-12 w-full rounded-xl sm:w-fit" onClick={submit} disabled={isPending}>
              {isPending ? <Loader2 data-icon="inline-start" className="animate-spin" aria-hidden="true" /> : null}
              Ask
              <ArrowRight data-icon="inline-end" aria-hidden="true" />
            </Button>
            {answer ? <div className="whitespace-pre-wrap rounded-xl border border-border bg-background p-4 text-sm leading-6">{answer}</div> : null}
            {error ? <p className="rounded-xl border border-warning/30 bg-warning/10 p-4 text-sm">{error}</p> : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
