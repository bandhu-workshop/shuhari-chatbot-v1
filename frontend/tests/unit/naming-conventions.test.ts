/**
 * The naming convention in frontend/AGENTS.md, enforced.
 *
 * Counterpart to the backend's tests/unit/test_package_structure.py. These need no
 * application code, which makes them the right first frontend tests: vitest fails a CI
 * job that collects nothing, and a convention enforced only by code review drifts.
 *
 * This is the test that would have caught App.tsx before PR #11 had to rename it.
 */

import { readdirSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

const SRC = join(import.meta.dirname, "..", "..", "src");

/** kebab-case: lowercase alphanumerics, single hyphens between them, nothing else. */
const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;

function walk(dir: string, rel = ""): { files: string[]; dirs: string[] } {
  const files: string[] = [];
  const dirs: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const here = rel ? `${rel}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      dirs.push(here);
      const nested = walk(join(dir, entry.name), here);
      files.push(...nested.files);
      dirs.push(...nested.dirs);
    } else {
      files.push(here);
    }
  }
  return { files, dirs };
}

const { files, dirs } = walk(SRC);

/** `vite-env.d.ts` -> `vite-env`, `message-list.tsx` -> `message-list`. */
const stem = (path: string): string => {
  const base = path.split("/").pop() ?? "";
  return base.split(".")[0] ?? "";
};

describe("src/ naming", () => {
  it("finds files to check", () => {
    // Guards the tests below: a broken walk() would make them vacuously pass.
    expect(files.length).toBeGreaterThan(0);
  });

  it("uses kebab-case filenames", () => {
    const offenders = files.filter((f) => !KEBAB.test(stem(f)));
    expect(
      offenders,
      "rename these to kebab-case (frontend/AGENTS.md -> Naming)",
    ).toEqual([]);
  });

  it("uses kebab-case folder names", () => {
    const offenders = dirs.filter((d) => !KEBAB.test(d.split("/").pop() ?? ""));
    expect(offenders, "rename these folders to kebab-case").toEqual([]);
  });

  it("has no PascalCase component files", () => {
    // The specific mistake the convention exists to prevent: a filename matching its
    // default export. Called out separately because the message should say why.
    const offenders = files.filter((f) => /^[A-Z]/.test(stem(f)));
    expect(
      offenders,
      "filenames are lowercase even when the export is PascalCase: message-list.tsx exports MessageList",
    ).toEqual([]);
  });
});
