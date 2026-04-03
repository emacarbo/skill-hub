---
name: fp-react
description: Use when applying fp-ts patterns in React -- Option for nullable state, Either for validation, TaskEither for async, RemoteData for loading states. Works with React 18/19, Next.js 14/15.
---

# Functional Programming in React

Practical fp-ts patterns for React apps.

## Quick Reference

| Pattern | Use When |
|---------|----------|
| `Option` | Value might be missing (user not loaded yet) |
| `Either` | Operation might fail (form validation) |
| `TaskEither` | Async operation might fail (API calls) |
| `RemoteData` | Need loading/error/success states |
| `pipe` | Chaining multiple transformations |

## 1. State with Option

```typescript
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'

function UserProfile() {
  const [user, setUser] = useState<O.Option<User>>(O.none)

  return pipe(
    user,
    O.match(
      () => <button onClick={() => handleLogin(...)}>Log In</button>,
      (u) => <div><p>Welcome, {u.name}!</p><button onClick={handleLogout}>Log Out</button></div>
    )
  )
}

// Chaining optional values
function getTheme(profile: Profile): string {
  return pipe(
    profile.user,
    O.flatMap(u => u.settings),
    O.map(s => s.theme),
    O.getOrElse(() => 'light')
  )
}
```

## 2. Form Validation with Either

```typescript
import * as E from 'fp-ts/Either'
import { sequenceS } from 'fp-ts/Apply'
import { getSemigroup } from 'fp-ts/NonEmptyArray'

const validateEmail = (email: string): E.Either<string, string> =>
  email.includes('@') ? E.right(email) : E.left('Invalid email')

const validatePassword = (pw: string): E.Either<string, string> =>
  pw.length >= 8 ? E.right(pw) : E.left('Password must be 8+ chars')

// Collect ALL errors, not just first
const validateAll = sequenceS(E.getApplicativeValidation(getSemigroup<string>()))

function validateForm(form: SignupForm): E.Either<string[], ValidatedForm> {
  return validateAll({
    name: pipe(validateName(form.name), E.mapLeft(e => [e])),
    email: pipe(validateEmail(form.email), E.mapLeft(e => [e])),
    password: pipe(validatePassword(form.password), E.mapLeft(e => [e])),
  })
}

// In component
const handleSubmit = () => {
  pipe(validateForm(form), E.match(
    (errs) => setErrors(errs),
    (valid) => { setErrors([]); submitToServer(valid) }
  ))
}
```

## 3. Data Fetching with TaskEither

```typescript
import * as TE from 'fp-ts/TaskEither'

const fetchJson = <T>(url: string): TE.TaskEither<Error, T> =>
  TE.tryCatch(
    async () => { const res = await fetch(url); if (!res.ok) throw new Error(`HTTP ${res.status}`); return res.json() },
    (err) => err instanceof Error ? err : new Error(String(err))
  )

// Chaining: fetch user then their posts
const fetchUserWithPosts = (userId: string) => pipe(
  fetchJson<User>(`/api/users/${userId}`),
  TE.flatMap(user => pipe(
    fetchJson<Post[]>(`/api/users/${userId}/posts`),
    TE.map(posts => ({ ...user, posts }))
  ))
)

// Parallel calls
import { sequenceT } from 'fp-ts/Apply'
const fetchDashboard = () => pipe(
  sequenceT(TE.ApplyPar)(fetchJson<User>('/api/user'), fetchJson<Stats>('/api/stats')),
  TE.map(([user, stats]) => ({ user, stats }))
)
```

## 4. RemoteData Pattern

State machine replacing `{ data, loading, error }` booleans.

```typescript
type RemoteData<E, A> =
  | { _tag: 'NotAsked' }
  | { _tag: 'Loading' }
  | { _tag: 'Failure'; error: E }
  | { _tag: 'Success'; data: A }

const notAsked = <E, A>(): RemoteData<E, A> => ({ _tag: 'NotAsked' })
const loading = <E, A>(): RemoteData<E, A> => ({ _tag: 'Loading' })
const failure = <E, A>(error: E): RemoteData<E, A> => ({ _tag: 'Failure', error })
const success = <E, A>(data: A): RemoteData<E, A> => ({ _tag: 'Success', data })

function fold<E, A, R>(rd: RemoteData<E, A>, onNotAsked: () => R, onLoading: () => R, onFailure: (e: E) => R, onSuccess: (a: A) => R): R {
  switch (rd._tag) {
    case 'NotAsked': return onNotAsked()
    case 'Loading': return onLoading()
    case 'Failure': return onFailure(rd.error)
    case 'Success': return onSuccess(rd.data)
  }
}

// Usage in component
return fold(state,
  () => <button onClick={execute}>Load User</button>,
  () => <Spinner />,
  (err) => <ErrorMessage message={err.message} onRetry={execute} />,
  (user) => <UserCard user={user} />
)
```

**Why RemoteData > booleans:** `{ data, loading: true, error }` is an impossible state. RemoteData only allows valid states.

## 5. Referential Stability

fp-ts values like `O.some(1)` create new objects each render.

```typescript
// BAD: O.some(1) !== O.some(1) triggers re-renders
const [value, setValue] = useState(O.some(1))

// GOOD: Memoize or depend on raw value
const [rawValue, setRawValue] = useState<number | null>(1)
const value = useMemo(() => O.fromNullable(rawValue), [rawValue])

// ALT: fp-ts-react-stable-hooks
import { useStableO } from 'fp-ts-react-stable-hooks'
const [value, setValue] = useStableO(O.some(1))
```

## 6. React 19 Patterns

```typescript
// useActionState for forms
const [state, formAction, isPending] = useActionState(async (prev, formData) => {
  return pipe(validateForm(Object.fromEntries(formData)), E.match(
    (errors) => ({ errors, success: false }),
    async (valid) => { await saveToServer(valid); return { errors: [], success: true } }
  ))
}, { errors: [], success: false })

// useOptimistic for instant feedback
const [optimisticTodos, addOptimistic] = useOptimistic(todos,
  (state, newTodo: Todo) => [...state, { ...newTodo, pending: true }]
)
```

## When to Use What

| Situation | Use |
|-----------|-----|
| Value might not exist | `Option<T>` |
| Operation might fail (sync) | `Either<E, A>` |
| Async might fail | `TaskEither<E, A>` |
| Loading/error/success UI | `RemoteData<E, A>` |
| Multiple validations | `Either` with validation applicative |
| Prevent fp-ts re-renders | `useMemo` or `fp-ts-react-stable-hooks` |

## Libraries

- [fp-ts](https://github.com/gcanti/fp-ts), [fp-ts-react-stable-hooks](https://github.com/mblink/fp-ts-react-stable-hooks)
- [@devexperts/remote-data-ts](https://github.com/devexperts/remote-data-ts), [io-ts](https://github.com/gcanti/io-ts), [zod](https://github.com/colinhacks/zod)
