// Stage a self-contained plugin bundle from the single authoritative repository Skill.
import { cpSync, mkdirSync, rmSync, existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(here, '..');
const repoRoot = resolve(packageRoot, '..', '..');
const destination = join(packageRoot, 'skill');
const required = ['SKILL.md', 'CHANGELOG.md', 'LICENSE', 'references', 'assets', 'scripts', 'examples'];
for (const item of required) {
  if (!existsSync(join(repoRoot, item))) throw new Error(`Missing repository source: ${item}`);
}
rmSync(destination, { recursive: true, force: true });
mkdirSync(destination, { recursive: true });
for (const item of required) {
  cpSync(join(repoRoot, item), join(destination, item), { recursive: true, filter: (path) => {
    const rel = path.slice(repoRoot.length).replaceAll('\\', '/');
    return !/(^|\/)(__pycache__|v2_output|demo_output|\.pytest_cache)(\/|$)/.test(rel) && !/\.pyc$/.test(rel);
  } });
}
if (!readFileSync(join(destination,'SKILL.md'),'utf8').includes('name: social-science-visualization')) {
  throw new Error('Staged Skill is missing its metadata');
}
console.log('Staged the canonical Social Science Visualization files for DSH packaging.');
