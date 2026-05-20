---
name: typescript-javascript
description: "Advanced TypeScript and modern JavaScript specialist covering type-level programming, ES2023+ patterns, project scaffolding, monorepo configuration, migration strategies, and build tooling. Use when implementing advanced generics, conditional/mapped/template literal types, branded types, discriminated unions, async/await patterns, ESM modules, Node.js APIs, or configuring TypeScript for monorepos, libraries, and tRPC."
license: MIT
metadata:
  domain: language
  triggers: TypeScript, JavaScript, generics, type safety, conditional types, mapped types, template literals, tRPC, tsconfig, type guards, discriminated unions, branded types, async await, ESM, CJS, Node.js, Web Workers, monorepo, Turborepo, Nx, Vitest, Biome
  role: specialist
  scope: implementation
  output-format: code
  related-skills: fullstack-guardian, api-design-pro, react-development
---

# TypeScript / JavaScript

Senior TypeScript and JavaScript specialist with deep expertise in type-level programming, ES2023+ patterns, project architecture, monorepo management, migration strategies, and modern build tooling.

## When to Use This Skill

- Implementing advanced TypeScript type systems (generics, conditional, mapped, template literal types)
- Creating branded types, discriminated unions, and custom type guards
- Configuring TypeScript for libraries, monorepos, or tRPC end-to-end safety
- Writing modern ES2023+ JavaScript with async/await, ESM, browser APIs
- Scaffolding TypeScript projects (Next.js, React+Vite, Node.js API, library)
- Migrating JavaScript to TypeScript, or legacy Redux to modern patterns
- Diagnosing slow type checking, module resolution errors, or build performance
- Setting up Biome, ESLint, Vitest, and monorepo tooling (Turborepo/Nx)

## Core Workflow

1. **Analyze project setup** — Read `package.json`, tsconfig, detect monorepo, confirm module system and Node/browser target
2. **Design type architecture** — Plan branded types, generics, discriminated unions, utility types
3. **Implement** — Write type-safe code; run `tsc --noEmit` to catch errors before proceeding
4. **Validate build** — Run `npm run typecheck` then linter; confirm zero errors and 85%+ test coverage
5. **Test types** — Use `vitest expectTypeOf` or `tsd` for library APIs and complex generics

## Project Setup Detection
```bash
node -e "const p=require('./package.json');console.log(Object.keys({...p.devDependencies,...p.dependencies}||{}).join('\n'))" | grep -E 'biome|eslint|vitest|jest|turborepo|nx'
(test -f pnpm-workspace.yaml || test -f turbo.json || test -f nx.json) && echo "Monorepo detected"
npm run -s typecheck || npx tsc --noEmit
npm run -s test || npx vitest run --reporter=basic --no-watch
```
Adapt to match existing import style, `baseUrl/paths` config, and project scripts. In monorepos, consider project references before broad tsconfig changes.

## Advanced Type System

### Branded Types (Domain Modeling)
```typescript
type Brand<T, B extends string> = T & { readonly __brand: B };
type UserId  = Brand<string, 'UserId'>;
type OrderId = Brand<number, 'OrderId'>;

const toUserId  = (id: string): UserId  => id as UserId;
const toOrderId = (id: number): OrderId => id as OrderId;

// Prevents accidental primitive mix-ups at compile time
function getOrder(userId: UserId, orderId: OrderId) { /* ... */ }
```
Use for: critical domain primitives, API boundaries, currency/units.

### Discriminated Unions & Exhaustive Handling
```typescript
type LoadingState = { status: 'loading' };
type SuccessState = { status: 'success'; data: string[] };
type ErrorState   = { status: 'error';   error: Error };
type RequestState = LoadingState | SuccessState | ErrorState;

function isSuccess(state: RequestState): state is SuccessState {
  return state.status === 'success';
}

function renderState(state: RequestState): string {
  switch (state.status) {
    case 'loading': return 'Loading…';
    case 'success': return state.data.join(', ');
    case 'error':   return state.error.message;
    default: {
      const _exhaustive: never = state;
      throw new Error(`Unhandled state: ${_exhaustive}`);
    }
  }
}
```

### Advanced Conditional & Mapped Types
```typescript
// Deep readonly
type DeepReadonly<T> = T extends (...args: any[]) => any ? T
  : T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } : T;

// Template literal — type-safe event names
type PropEventSource<T> = {
  on<K extends string & keyof T>(eventName: `${K}Changed`, cb: (v: T[K]) => void): void;
};

// Require exactly one key
type RequireExactlyOne<T, Keys extends keyof T = keyof T> =
  Pick<T, Exclude<keyof T, Keys>> &
  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Record<Exclude<Keys, K>, never>> }[Keys];
```

### satisfies Operator (TS 5.0+) and Type Testing
```typescript
// Preserves literal types while validating against constraint
const config = { api: 'https://api.example.com', timeout: 5000 } satisfies Record<string, string | number>;

// Type testing with Vitest (avatar.test-d.ts)
import { expectTypeOf } from 'vitest';
test('Avatar size type', () => {
  expectTypeOf<Avatar['size']>().toEqualTypeOf<'sm' | 'md' | 'lg'>();
});
```

## TypeScript Configuration

### Production tsconfig (Library)
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "isolatedModules": true,
    "declaration": true,
    "declarationMap": true,
    "incremental": true,
    "skipLibCheck": false
  }
}
```

### Next.js / Bundler tsconfig
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "incremental": true,
    "paths": { "@/*": ["./src/*"] }
  }
}
```

### Monorepo Project References
```json
// Root tsconfig.json
{
  "references": [{ "path": "./packages/core" }, { "path": "./packages/ui" }, { "path": "./apps/web" }],
  "compilerOptions": { "composite": true, "declaration": true, "declarationMap": true }
}
```

## Monorepo Tooling

### Turborepo vs Nx Decision

| Factor | Turborepo | Nx |
|--------|-----------|-----|
| Package count | < 20 | 20+ |
| Complexity | Simple pipeline | Complex dep graph |
| Visualization | None | Built-in |
| Performance | Very fast | Faster on large repos |
| Plugins | Minimal | Extensive ecosystem |

```bash
# Turborepo setup
pnpm dlx create-turbo@latest

# Nx setup
npx create-nx-workspace@latest
```

## ES2023+ JavaScript Patterns

### Async/Await Error Handling
```javascript
// Always handle async errors explicitly
async function fetchUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (err) {
    console.error('fetchUser failed:', err);
    return null;
  }
}
```

### Optional Chaining & Nullish Coalescing
```javascript
const city = user?.address?.city ?? 'Unknown';
const value = input ?? defaultValue;  // ?? vs || — only nullish, not falsy
```

### ESM Module Structure
```javascript
// Named exports for libraries (enables tree-shaking)
export const add = (a, b) => a + b;
export const multiply = (a, b) => a * b;

// Dynamic imports for code splitting
const { HeavyComponent } = await import('./HeavyComponent.js');

// CJS interop in ESM
const pkg = (await import('cjs-package')).default;
```

### ES2023+ Features
```javascript
// Immutable array methods — return new array (ES2023)
const sorted = arr.toSorted((a, b) => a - b);
const reversed = arr.toReversed();
const spliced = arr.toSpliced(1, 2, 'new');

// Object.hasOwn (replaces hasOwnProperty)
if (Object.hasOwn(obj, 'key')) { ... }

// using declarations (ES2025 — resource management)
using file = openFile('data.txt');  // auto-closes on scope exit
```

### Web Workers, Browser APIs, Node.js
```javascript
// Offload CPU work to Worker
const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
worker.onmessage = ({ data }) => setResult(data.result);

// IntersectionObserver for lazy loading
new IntersectionObserver(entries => entries.forEach(e => e.isIntersecting && load(e.target)), { threshold: 0.1 }).observe(el);

// Node.js async I/O and custom error class
import { readFile } from 'node:fs/promises';
class DomainError extends Error {
  constructor(msg, code, statusCode) {
    super(msg); this.name = 'DomainError'; this.code = code; this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}
```

## Project Scaffolding

### TypeScript Library Package
```json
{
  "name": "@scope/lib", "type": "module",
  "main": "./dist/index.js", "types": "./dist/index.d.ts",
  "exports": { ".": { "import": "./dist/index.js", "types": "./dist/index.d.ts" } },
  "files": ["dist"],
  "scripts": { "build": "tsc -p tsconfig.build.json", "test": "vitest", "typecheck": "tsc --noEmit", "prepublishOnly": "pnpm build" }
}
```

### Node.js API (ESM) — `.js` extensions required in ESM relative imports
```typescript
import express from 'express';
import { userRouter } from './routes/users.js';
import { errorHandler } from './middleware/error.js';
export function createApp() {
  const app = express();
  app.use(express.json()).use('/api/users', userRouter).use(errorHandler);
  return app;
}
```

## Migration Strategies

### JavaScript → TypeScript (Incremental)
```bash
# 1. Enable allowJs/checkJs in existing tsconfig
# 2. Rename .js → .ts file by file
# 3. Add types incrementally using AI assistance
# 4. Enable strict mode flags one at a time

npx ts-migrate migrate . --sources 'src/**/*.js'  # automated migration
npx typesync                                        # install missing @types packages
```

### Legacy Redux → RTK and CJS → ESM
```typescript
// RTK: Immer-powered "mutations" in reducers
const todosSlice = createSlice({ name: 'todos', initialState: [] as Todo[],
  reducers: { addTodo: (state, action: PayloadAction<string>) => { state.push({ text: action.payload, completed: false }); } }
});
```
**CJS → ESM:** Add `"type": "module"` to package.json. Replace `require()` with `import`. Add `.js` extensions to all relative imports. Handle `__dirname`: `const __dirname = fileURLToPath(new URL('.', import.meta.url))`. Use `await import()` for dynamic requires.

## Tooling Decisions

### Biome vs ESLint

| Use Biome When | Use ESLint When |
|----------------|-----------------|
| Speed is critical | Need type-aware linting |
| Single tool for lint + format | Complex custom rules |
| TypeScript-first project | Vue/Angular framework |
| Less configuration desired | Need specific plugins |

### Build Performance Diagnostics
```bash
npx tsc --extendedDiagnostics --incremental false | grep -E "Check time|Files:|Lines:"
npx tsc --traceResolution > resolution.log 2>&1
npx tsc --generateTrace trace --incremental false && npx @typescript/analyze-trace trace
```
**Fixes:** `incremental: true` + `.tsbuildinfo` cache; split large unions (> 100 members); `interface extends` instead of `&` for performance; `skipLibCheck: true` (use carefully — masks app type issues); configure `include`/`exclude` precisely.

## Common Error Patterns

| Error | Root Cause | Fix Priority |
|-------|-----------|-------------|
| "The inferred type cannot be named" | Missing type export or circular dep | Export type explicitly; use `ReturnType<typeof fn>` |
| "Excessive stack depth" | Circular/deeply recursive types | Limit recursion; use `interface extends` instead of `&` |
| "Cannot find module" | `moduleResolution` mismatch | Check setting matches bundler; verify `baseUrl`/`paths` |
| "Type instantiation is excessively deep" | Complex generic constraints | Simplify; break recursion with conditional types |

### Missing Type Declarations
```typescript
// types/ambient.d.ts — Quick fix for untyped packages
declare module 'some-untyped-package' {
  const value: unknown;
  export default value;
}
```

## Code Review Checklist

**Type Safety:** No implicit `any`, strict null checks handled, `as` assertions justified, generics constrained, return types explicit on public APIs, branded types for domain primitives.

**Module System:** No circular dependencies, barrel exports used judiciously, `.js` extensions on ESM relative imports, ESM/CJS compatibility handled.

**JavaScript:** `const`/`let` (never `var`), `async`/`await` throughout, error handling at every boundary, no synchronous I/O in Node.js, no mutated parameters.

## Constraints

### MUST DO (TypeScript)
- Enable `strict` mode with all compiler flags
- Use type-first API design
- Implement branded types for domain modeling
- Use `satisfies` operator for constraint validation
- Create discriminated unions for state machines
- Generate declaration files for libraries
- Prefer `interface` extends over type intersection for performance

### MUST NOT DO (TypeScript)
- Use explicit `any` without `// eslint-disable-next-line` justification
- Disable strict null checks
- Skip declaration file generation for libraries
- Use enums (prefer `as const` objects)
- Mix type-only and value imports in the same statement

### MUST DO (JavaScript)
- ES2023+ features exclusively
- `async`/`await` for all async operations
- ESM (`import`/`export`) for new projects
- JSDoc comments for public functions in JS files
- Functional principles — no mutation of parameters

### MUST NOT DO (JavaScript)
- Use `var`
- Use callback-based APIs (prefer Promises)
- Use synchronous I/O in Node.js
- Create blocking operations in the browser
- Skip error handling in async functions
