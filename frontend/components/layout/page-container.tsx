import type { ReactNode } from "react";

type PageContainerProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  children: ReactNode;
};

export function PageContainer({ eyebrow, title, description, children }: PageContainerProps) {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
      <header className="mb-10 max-w-3xl">
        {eyebrow && <p className="mb-3 text-xs font-bold uppercase tracking-[0.18em] text-primary">{eyebrow}</p>}
        <h1 className="text-3xl font-bold tracking-tight sm:text-5xl">{title}</h1>
        {description && <p className="mt-4 text-base leading-7 text-muted-foreground sm:text-lg">{description}</p>}
      </header>
      <div className="space-y-6">{children}</div>
    </div>
  );
}
