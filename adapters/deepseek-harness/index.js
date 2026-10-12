/** DSH/Cordis adapter: registers the unchanged research workflow as a runtime Skill.
 * No shell tools, hooks, filesystem writes or background jobs are registered.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

export const name = 'social-science-visualization';
export const inject = ['skills'];

const skillRoot = fileURLToPath(new URL('./skill/', import.meta.url));
const skillFile = join(skillRoot, 'SKILL.md');
const description = 'Reproducible social-science research figures with data and inference checks, existing regression and event-study estimates, policy maps, and publication-oriented outputs for political science, public administration, public policy, and adjacent fields.';

function skillBody(source) {
  const stripped = source.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
  if (stripped === source || !stripped.trim()) {
    throw new Error('Bundled SKILL.md is missing valid frontmatter or an instruction body');
  }
  return stripped;
}

export function apply(ctx) {
  const content = skillBody(readFileSync(skillFile, 'utf8'));
  // DSH owns discovery, model-facing skill invocation, and effect disposal.
  ctx.skills.register({
    name: 'social-science-visualization',
    description,
    source: 'runtime',
    resourceBase: { kind: 'directory', path: skillRoot },
    content,
    metadata: { version: '2.0.0', adapterVersion: '0.1.0', language: 'zh-CN' },
    invocation: { modelInvocable: true, userInvocable: true },
  });
}
