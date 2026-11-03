import { STAGES, stageIndex } from "@/lib/stages";
import type { ActualStage } from "@/lib/types";
import { cn } from "@/lib/utils";

type StageTrackProps = {
  stage: ActualStage;
  labels: Record<ActualStage, string>;
  showLabel?: boolean;
  className?: string;
};

/** Seven dots, filled up to the stage a team actually reached. */
export function StageTrack({ stage, labels, showLabel = true, className }: StageTrackProps) {
  const reached = stageIndex(stage);
  const champion = stage === "champion";

  return (
    <span className={cn("flex items-center gap-1.5", className)}>
      <span role="img" aria-label={labels[stage]} className="flex items-center gap-1.5">
        {STAGES.map((item, index) => (
          <span
            key={item}
            title={labels[item]}
            className={cn(
              "box-border rounded-full",
              index === STAGES.length - 1 ? "size-3.5" : "size-2.5",
              index <= reached ? (champion ? "bg-accent" : "bg-ink") : "border border-hollow",
            )}
          />
        ))}
      </span>
      {showLabel && <span className="ml-2 text-[13px] text-ink-2">{labels[stage]}</span>}
    </span>
  );
}
