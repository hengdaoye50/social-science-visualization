# DeepSeek Harness adapter for Social Science Visualization

Adapter **0.1.0** for the canonical root Skill **v2.0.0**. This is the **Cordis bundle source**; during `npm pack`, `scripts/stage.mjs` copies the root `SKILL.md`, `references/`, `scripts/`, `assets/`, and `examples/` into a self-contained `skill/` folder. The generated folder is ignored by Git, preventing two maintained copies of the same research rules.

## Install the bundle

From the repository root:

```bash
cd adapters/deepseek-harness
npm test
npm pack
dsh plugin --profile research add ./dsh-social-science-visualization-0.1.0.tgz
dsh --profile research --dump-config
```

Replace `research` with an existing DSH profile. The tarball name assumes package version 0.1.0; inspect the actual `npm pack` output if you update the version. `npm pack` executes the `prepack` script; only install packages whose contents and host-code permissions you trust. Node.js 20+ and a supported DSH CLI are required. Plugin installation does **not** install Python libraries.

### Alternative: native DSH Skill

If you do not need the plugin registry, copy the complete repository Skill resources to `.dsh/skills/social-science-visualization/` in your DSH project. Keep all relative subdirectories and choose **one** installation route to avoid duplicate skill names.

## Design and trust boundary

- The `package.json` `dsh.bundle.patch` references `cordis.patch.yml`, which mounts `index.js`.
- `index.js` requests only the `skills` service and calls `ctx.skills.register()` with a directory `resourceBase`.
- It does not register a model-facing shell tool, run Python on load, or bypass DSH sandbox or approval controls.
- The bundled `skill/` is generated from the root source at packaging time. `npm test` stages it before testing its registration shape.
- Runtime validation in a real DSH profile and compatibility with future DSH API changes remain necessary. The adapter is an independently authored community project, not an official DeepSeek package.

**Official context:** [DSH Skill registry](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md) · [Plugin publishing guide](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish).
