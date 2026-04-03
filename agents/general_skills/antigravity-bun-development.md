---
name: bun-development
description: "Fast, modern JavaScript/TypeScript development with the Bun runtime."
---

# Bun Development

Bun is an all-in-one JS/TS runtime that replaces Node.js, npm, Jest, and Webpack. It runs TypeScript natively, installs packages 10-100x faster, and starts in ~25ms. Use when building new JS/TS projects or migrating from Node.js.

## Key Patterns

- **Native TypeScript**: No transpiler needed -- `bun run index.ts` just works
- **Package management**: `bun install` / `bun add <pkg>` / `bun remove <pkg>` -- binary lockfile (`bun.lockb`) for speed
- **Watch mode**: `bun --watch run file.ts` (restart) or `bun --hot run file.ts` (HMR)
- **Env files**: `.env` loaded automatically; access via `Bun.env.KEY` or `process.env.KEY`
- **Built-in APIs**: `Bun.file()` for fast I/O, `Bun.serve()` for HTTP (4-10x faster than Express), `Bun.password.hash()` for hashing
- **SQLite built-in**: `import { Database } from "bun:sqlite"` -- no external driver needed
- **Testing**: `bun test` with Jest-compatible API (`describe`, `it`, `expect`, `mock`, `spyOn`)
- **Bundling**: `bun build ./src/index.ts --outdir ./dist --minify --sourcemap`
- **Compile to binary**: `bun build ./cli.ts --compile --outfile myapp`
- **Node.js compat**: Most Node APIs work; replace `require()` with `import`, `process.hrtime()` with `Bun.nanoseconds()`

## Quick Reference

| Task | Command |
|:-----|:--------|
| Init project | `bun init` |
| Create from template | `bun create react my-app` |
| Install deps | `bun install` |
| Add package | `bun add <pkg>` |
| Dev dependency | `bun add -d <pkg>` |
| Remove package | `bun remove <pkg>` |
| Update all | `bun update` |
| Run file | `bun run file.ts` |
| Run script | `bun run dev` |
| Watch mode | `bun --watch run file.ts` |
| Hot reload | `bun --hot run server.ts` |
| Run tests | `bun test` |
| Test coverage | `bun test --coverage` |
| Test pattern | `bun test --grep "pattern"` |
| Build | `bun build ./src/index.ts --outdir ./dist` |
| Build minified | `bun build ./src/index.ts --outdir ./dist --minify --sourcemap` |
| Compile binary | `bun build ./cli.ts --compile --outfile myapp` |
| Cross-compile | `bun build ./cli.ts --compile --target=bun-linux-x64 --outfile myapp` |
| Execute pkg | `bunx <pkg>` |
| Frozen install | `bun install --frozen-lockfile` |
| Custom env file | `bun --env-file=.env.prod run index.ts` |

### Bun vs Node.js

| Feature | Bun | Node.js |
|:--------|:----|:--------|
| Startup time | ~25ms | ~100ms+ |
| Package install | 10-100x faster | Baseline |
| TypeScript | Native | Requires transpiler |
| JSX | Native | Requires transpiler |
| Test runner | Built-in | External (Jest, Vitest) |
| Bundler | Built-in | External (Webpack, esbuild) |
| SQLite | Built-in | External package |

### Essential Code Snippets

```typescript
// HTTP server (Bun.serve)
Bun.serve({
  port: 3000,
  fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/api") return Response.json({ ok: true });
    return new Response("Not Found", { status: 404 });
  },
});

// File I/O
const data = await Bun.file("./data.json").json();
await Bun.write("./out.txt", "Hello, Bun!");

// SQLite
import { Database } from "bun:sqlite";
const db = new Database("mydb.sqlite");
db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)");
const user = db.prepare("SELECT * FROM users WHERE id = ?").get(1);

// Password hashing
const hash = await Bun.password.hash("secret");
const valid = await Bun.password.verify("secret", hash);

// Testing
import { describe, it, expect, mock } from "bun:test";
describe("math", () => {
  it("adds", () => expect(1 + 1).toBe(2));
});
```

### Migration from Node.js

```bash
# 1. Install Bun
curl -fsSL https://bun.sh/install | bash

# 2. Replace package manager
rm -rf node_modules package-lock.json && bun install

# 3. Update scripts: "node index.js" -> "bun run index.ts"

# 4. Add Bun types
bun add -d @types/bun
```

```typescript
// Node.js -> Bun equivalents
// require("pkg")        -> import pkg from "pkg"
// require.resolve("pkg") -> import.meta.resolve("pkg")
// process.hrtime()      -> Bun.nanoseconds()
// setImmediate()        -> queueMicrotask()
// fs.readFile(path)     -> Bun.file(path).text()
```

## When to Use

- Starting a new JS/TS project where speed matters
- Migrating a Node.js project to faster runtime
- Need built-in test runner, bundler, or SQLite without extra dependencies
- Building HTTP servers or WebSocket services (use `Bun.serve()` or Elysia framework)
- Creating standalone CLI executables from TypeScript

## Resources

- [Bun Documentation](https://bun.sh/docs)
- [Bun GitHub](https://github.com/oven-sh/bun)
- [Elysia Framework](https://elysiajs.com/)
