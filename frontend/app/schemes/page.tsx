import { ExternalLink, Landmark } from "lucide-react";
import { getSchemes, type SchemeMatch } from "@/lib/api";
import { Card, CardContent } from "@/components/ui";

export default async function SchemesPage() {
  let schemes: SchemeMatch[] = [];
  try {
    schemes = (await getSchemes()).schemes ?? [];
  } catch {
    schemes = [];
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight">Browse schemes</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">Schemes added from official sources will appear here in simple language.</p>
      </div>

      {schemes.length === 0 ? (
        <Card className="rounded-2xl">
          <CardContent className="p-8 text-center">
            <span className="mx-auto grid size-14 place-items-center rounded-full bg-primary/10 text-primary">
              <Landmark aria-hidden="true" />
            </span>
            <h2 className="mt-4 text-xl font-bold">No schemes added yet</h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted-foreground">
              Once official scheme pages are added in the backend, they will show up here.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {schemes.map((scheme) => (
            <Card key={scheme.id} className="rounded-2xl">
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  <span className="grid size-12 place-items-center rounded-xl bg-primary/10 text-primary">
                    <Landmark aria-hidden="true" />
                  </span>
                  <div className="min-w-0">
                    <h2 className="text-lg font-bold">{scheme.name}</h2>
                    <p className="mt-1 text-sm text-muted-foreground">{scheme.state}</p>
                    {scheme.source_url ? (
                      <a className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary" href={scheme.source_url} target="_blank" rel="noreferrer">
                        Official website
                        <ExternalLink aria-hidden="true" />
                      </a>
                    ) : null}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
