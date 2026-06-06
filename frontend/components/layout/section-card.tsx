import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type SectionCardProps = {
  title: string;
  description?: string;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function SectionCard({ title, description, icon, children, className }: SectionCardProps) {
  return (
    <section className={cn("rounded-2xl border bg-card p-5 shadow-sm sm:p-6", className)}>
      <header className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 className="font-semibold tracking-tight">{title}</h2>
          {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
        </div>
        {icon && <span className="text-primary">{icon}</span>}
      </header>
      {children}
    </section>
  );
}
