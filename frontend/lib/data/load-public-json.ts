import "server-only";

import { readFile } from "node:fs/promises";
import path from "node:path";

export async function loadPublicJson<T>(publicPath: `/data/${string}.json`): Promise<T> {
  const filePath = path.join(process.cwd(), "public", publicPath);

  try {
    return JSON.parse(await readFile(filePath, "utf-8")) as T;
  } catch (error) {
    throw new Error(
      `Unable to load ${publicPath}. Run "python scripts/frontend/sync_frontend_data.py" from the project root.`,
      { cause: error },
    );
  }
}
