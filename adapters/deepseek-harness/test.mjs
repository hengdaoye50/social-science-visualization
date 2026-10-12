import assert from 'node:assert/strict';
import { test } from 'node:test';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { apply, inject, name } from './index.js';

test('Cordis adapter registers one skill with proper resourceBase and no extra tools', () => {
 const calls = [];
 const ctx = { skills: { register: (definition) => calls.push(definition) },
   tools: { register: () => { throw Error('must not register model tools'); } } };
 apply(ctx);
 assert.equal(name, 'social-science-visualization');
 assert.deepEqual(inject, ['skills']);
 assert.equal(calls.length, 1);
 const entry = calls[0];
 assert.equal(entry.name, name);
 assert.equal(entry.source, 'runtime');
 assert.equal(entry.resourceBase.kind, 'directory');
 assert.ok(existsSync(join(entry.resourceBase.path, 'scripts/render_figure.py')));
 assert.ok(existsSync(join(entry.resourceBase.path, 'references/causal-inference.md')));
 assert.match(entry.content, /不可妥协的六条原则/);
 assert.doesNotMatch(entry.content, /^---/);
 assert.equal(entry.invocation.modelInvocable, true);
 assert.equal(entry.invocation.userInvocable, true);
});

test('bundle manifest, patch, and copy agree on identity', () => {
 const dir = fileURLToPath(new URL('.', import.meta.url));
 const pkg=JSON.parse(readFileSync(join(dir, 'package.json'), 'utf8'));
 const patch=readFileSync(join(dir,'cordis.patch.yml'),'utf8');
 assert.equal(pkg.dsh.bundle.patch, './cordis.patch.yml');
 assert.equal(pkg.main, './index.js');
 assert.match(patch, /name: dsh-social-science-visualization/);
 assert.ok(pkg.files.includes('skill/'));
});
