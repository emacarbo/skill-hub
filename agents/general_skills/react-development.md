---
name: react-development
description: "Senior React and Next.js specialist covering React 19, Server Components, state management, performance, testing, migration, and full-stack Next.js deployment. Use when building React components, implementing hooks or state management, optimizing performance, migrating class components, setting up Next.js 14+ App Router, or working with Server Actions and streaming SSR."
license: MIT
metadata:
  domain: frontend
  triggers: React, JSX, hooks, useState, useEffect, useContext, Server Components, React 19, Suspense, TanStack Query, Redux, Zustand, Jotai, Next.js, App Router, useActionState, useOptimistic, class migration, component, frontend
  role: specialist
  scope: implementation
  output-format: code
  related-skills: fullstack-guardian, testing-qa-suite, typescript-javascript
---

# React Development

Senior React and Next.js specialist with deep expertise in React 19, Server Components, state management patterns, performance optimization, and production-grade application architecture including Next.js 14+ deployment.

## When to Use This Skill

- Building new React components or features (React 18+/19)
- Implementing state management (local, Context, Redux Toolkit, Zustand, Jotai)
- Setting up Next.js 14+ with App Router, Server Components, or Server Actions
- Optimizing React performance (waterfall elimination, bundle size, re-renders)
- Working with forms via React 19 `useActionState` or React Hook Form
- Migrating class components to hooks or Server Components
- Upgrading React versions with codemods and concurrent feature adoption
- Data fetching with TanStack Query, SWR, or `use()`

## Core Workflow

1. **Analyze requirements** — Identify component hierarchy, state needs, data flow, rendering strategy
2. **Choose patterns** — Select state management tier, data fetching approach, Server vs Client boundary
3. **Implement** — Write TypeScript components with proper types; keep Server Components as default
4. **Validate** — Run `tsc --noEmit`; fix all type errors before proceeding
5. **Optimize** — Apply performance rules (waterfall → bundle → re-render priority); ensure accessibility
6. **Test** — Write tests with React Testing Library; fix all failures before submitting

## Reference Guide

| Topic | Load When |
|-------|-----------|
| Server Components | RSC patterns, Next.js App Router boundaries |
| React 19 features | `use()`, `useActionState`, `useOptimistic`, compiler |
| State management | Context, Zustand, Jotai, Redux Toolkit, TanStack Query |
| Hooks patterns | Custom hooks, `useEffect` cleanup, `useCallback`, `useRef` |
| Performance | Waterfall elimination, bundle splitting, memoization, virtualization |
| Testing | React Testing Library, mocking, accessibility assertions |
| Migration | Class-to-hooks, React version upgrades, codemods |

## Component Design

### Component Type Decision Table

| Type | Use When | State |
|------|----------|-------|
| **Server** | Data fetching, static markup, no interactivity | None |
| **Client** | Event handlers, browser APIs, animations | useState, effects |
| **Presentational** | Pure UI display, highly reusable | Props only |
| **Compound** | Shared state between sibling parts (Tabs, Accordion) | Context |

**Rules:** One responsibility per component. Props down, events up. Composition over inheritance. Server Components by default — add `'use client'` only at the leaf boundary requiring interactivity.

### Server Component Pattern (Next.js App Router)
```tsx
// app/users/page.tsx — Server Component, no "use client"
import { db } from '@/lib/db';

export default async function UsersPage() {
  const users = await db.user.findMany(); // runs on server, never ships to client
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### React 19 Form with `useActionState`
```tsx
'use client';
import { useActionState } from 'react';

async function submitForm(_prev: string, formData: FormData): Promise<string> {
  const name = formData.get('name') as string;
  return `Hello, ${name}!`;
}

export function GreetForm() {
  const [message, action, isPending] = useActionState(submitForm, '');
  return (
    <form action={action}>
      <input name="name" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Submitting…' : 'Submit'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
```

### Custom Hook with Cleanup
```tsx
function useWindowWidth(): number {
  const [width, setWidth] = useState(() => window.innerWidth);
  useEffect(() => {
    const handler = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);
  return width;
}
```

## State Management Selection

| Scenario | Solution |
|----------|----------|
| Component-local UI | `useState`, `useReducer` |
| Parent-child lift | Lift state up |
| Feature subtree | Context |
| Small app, simple global | **Zustand** (simplest) |
| Atomic/granular updates | **Jotai** |
| Large app, complex Redux | **Redux Toolkit** |
| Server/async data | **TanStack Query** or SWR |
| URL state | React Router, `nuqs` |
| Form state | React Hook Form + Zod |

### Zustand Store (Recommended Default)
```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export const useStore = create<AppState>()(
  devtools(persist(
    (set) => ({
      user: null,
      theme: 'light' as const,
      setUser: (user) => set({ user }),
      toggleTheme: () => set((s) => ({ theme: s.theme === 'light' ? 'dark' : 'light' })),
    }),
    { name: 'app-storage' }
  ))
);

// Selective subscriptions prevent unnecessary re-renders
export const useUser = () => useStore((s) => s.user);
```

### TanStack Query with Optimistic Updates
```typescript
export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateUser,
    onMutate: async (newUser) => {
      await queryClient.cancelQueries({ queryKey: userKeys.detail(newUser.id) });
      const previousUser = queryClient.getQueryData(userKeys.detail(newUser.id));
      queryClient.setQueryData(userKeys.detail(newUser.id), newUser);
      return { previousUser };
    },
    onError: (_err, newUser, context) => {
      queryClient.setQueryData(userKeys.detail(newUser.id), context?.previousUser);
    },
    onSettled: (_data, _err, variables) => {
      queryClient.invalidateQueries({ queryKey: userKeys.detail(variables.id) });
    },
  });
}
```

## Performance — Priority Order

**1. Eliminate Waterfalls (CRITICAL)**
- Use `Promise.all()` for independent async operations
- Use Suspense boundaries to stream content in parallel
- Start promises early, await late in API routes
- Use `React.cache()` for per-request deduplication on the server

**2. Bundle Size (CRITICAL)**
- Import directly, avoid barrel files (`import { Button } from './Button'`)
- Use `next/dynamic` or `React.lazy` for heavy components
- Load analytics/third-party scripts after hydration
- Avoid heavy deps: `moment` → `date-fns`/`dayjs`, `lodash` → `lodash-es`

**3. Re-render Optimization (MEDIUM)**
- Don't subscribe to state only used in callbacks (`rerender-defer-reads`)
- Use primitive dependencies in effects, not object references
- Use `startTransition` for non-urgent updates
- Profile first — don't memoize blindly

## UI State Patterns

**Loading/Error/Empty Decision:**
```typescript
const { data, loading, error } = useQuery(...);

if (error) return <ErrorState error={error} onRetry={refetch} />;
if (loading && !data) return <Skeleton />;   // skeleton only when no data
if (!data?.items.length) return <EmptyState />;
return <List items={data.items} />;
```

**Rules:** Show loading indicator ONLY when there's no data to display. Always surface errors — never swallow them. Every list/collection MUST have an empty state. Always disable buttons during async operations.

## Next.js 14+ Specifics

### MUST DO
- Use App Router (`app/` directory), never Pages Router
- Use `generateMetadata` for all SEO — never hardcode `<title>` in JSX
- Optimize every image with `next/image`; never use `<img>` for content
- Add `loading.tsx` and `error.tsx` at every async route segment
- Use native `fetch` with explicit `cache`/`next.revalidate` options

### Server Action with Revalidation
```tsx
// app/products/actions.ts
'use server'
import { revalidatePath } from 'next/cache';

export async function createProduct(formData: FormData) {
  const name = formData.get('name') as string;
  await db.product.create({ data: { name } });
  revalidatePath('/products');
}
```

### Dynamic SEO Metadata
```tsx
export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const product = await fetchProduct(params.id);
  return {
    title: product.name,
    description: product.description,
    openGraph: { title: product.name, images: [product.imageUrl] },
  };
}
```

## Migration and Modernization

### Class-to-Hooks Migration Pattern
- Lifecycle → `useEffect` with appropriate dependency arrays
- `this.state` → multiple `useState` or `useReducer`
- `this.props` → function parameters
- Class methods → regular functions or extracted custom hooks
- Use codemods: `react-codemod` for automated transforms

### React Version Upgrade Process
1. Run official codemods first (`npx codemod@latest`)
2. Adopt concurrent features gradually (Suspense, transitions)
3. Enable React Compiler when available (reduces manual memoization)

### Storybook Integration
Generate stories alongside components for design system documentation:
```bash
npx storybook@latest init
# Component with story
python scripts/component_generator.py Button --with-story
```

## Constraints

### MUST DO
- TypeScript strict mode on all components
- Error boundaries around async operations
- `key` props with stable, unique identifiers (never array index)
- Cleanup functions in `useEffect`
- Semantic HTML and ARIA attributes for accessibility
- Suspense boundaries for async routes

### MUST NOT DO
- Mutate state directly
- Convert Server Components to Client just to access data
- Create functions inside JSX render (causes re-renders)
- Ignore React strict mode warnings
- Skip `loading.tsx`/`error.tsx` on async segments
- Deploy without running `next build` to confirm zero errors

## Quality Gate

Before completing any React feature:
- [ ] TypeScript compiles without errors (`tsc --noEmit`)
- [ ] Error state handled and shown to user
- [ ] Loading state shown only when no data exists
- [ ] Empty state provided for collections
- [ ] Buttons disabled during async operations
- [ ] No accessibility violations (semantic HTML, ARIA, color contrast)
- [ ] Tests passing with React Testing Library
