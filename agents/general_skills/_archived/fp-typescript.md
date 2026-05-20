---
name: fp-typescript
description: Consolidated functional programming guide for TypeScript -- pipe/flow, Option, Either, TaskEither, ReaderTaskEither, React integration, io-ts/Schema, Effect-TS, and functional optics
version: 1.0.0
source: merged
merged_from:
  - antigravity-fp-pragmatic
  - antigravity-fp-async
  - antigravity-fp-backend
  - antigravity-fp-react
tags:
  - fp-ts
  - typescript
  - functional-programming
  - async
  - error-handling
  - react
  - backend
  - dependency-injection
  - io-ts
  - effect-ts
  - optics
---


<!-- SUMMARY
Scope: Functional programming in TypeScript — fp-ts, Effect-TS, optics
Capabilities: pipe/flow, Option/Either, TaskEither async, ReaderTaskEither DI, io-ts, lenses
Not for: General TypeScript (use typescript-javascript), React state (use react-development)
END SUMMARY -->

# Functional Programming in TypeScript

Pragmatic FP patterns for real codebases. Use FP when it clarifies; skip it when it obscures.

## 1. Core Concepts: pipe, flow, Option, Either

### pipe and flow

`pipe` feeds a value through functions left-to-right. `flow` composes functions without an initial value.

```typescript
import { pipe, flow } from 'fp-ts/function'

// pipe: value first, then transformations
const result = pipe(input, parse, validate, format)

// flow: creates a reusable pipeline (no initial value)
const process = flow(parse, validate, format)
const result = process(input)
```

Use `pipe` for 3+ transformations. Use `flow` when building reusable pipelines.

### Option -- missing values without null

```typescript
import * as O from 'fp-ts/Option'

// Wrap nullable -> Option
const maybeUser = O.fromNullable(possiblyNull) // Some(value) | None

// Chain through potential missing values
const city = pipe(
  O.fromNullable(user),
  O.flatMap(u => O.fromNullable(u.address)),
  O.flatMap(a => O.fromNullable(a.city)),
  O.getOrElse(() => 'Unknown')
)

// Render in React
pipe(
  maybeUser,
  O.match(
    () => <LoginButton />,
    (u) => <UserMenu user={u} />
  )
)
```

Skip Option for simple cases where `user?.address?.city ?? 'Unknown'` suffices.

### Either -- errors as values

```typescript
import * as E from 'fp-ts/Either'

const parseAge = (input: string): E.Either<string, number> => {
  const age = parseInt(input, 10)
  if (isNaN(age)) return E.left('Invalid age')
  if (age < 0) return E.left('Age cannot be negative')
  return E.right(age)
}

// Chain operations that might fail
const getValidEmail = (raw: string): E.Either<string, string> =>
  pipe(
    E.tryCatch(() => JSON.parse(raw), () => 'Invalid JSON'),
    E.flatMap(extractEmail),
    E.flatMap(validateEmail)
  )
```

### Typed discriminated-union errors

```typescript
type AppError =
  | { _tag: 'NotFound'; id: string }
  | { _tag: 'ValidationError'; field: string; message: string }
  | { _tag: 'Unauthorized' }

const handleError = (e: AppError): string => {
  switch (e._tag) {
    case 'NotFound':        return `Item ${e.id} not found`
    case 'ValidationError': return `${e.field}: ${e.message}`
    case 'Unauthorized':    return 'Please log in'
  }
}
```

### Collecting ALL validation errors

```typescript
import { sequenceS } from 'fp-ts/Apply'
import { getSemigroup } from 'fp-ts/NonEmptyArray'

const validateAll = sequenceS(E.getApplicativeValidation(getSemigroup<string>()))

const validateForm = (form: SignupForm): E.Either<string[], ValidatedForm> =>
  validateAll({
    name:     pipe(validateName(form.name),     E.mapLeft(e => [e])),
    email:    pipe(validateEmail(form.email),    E.mapLeft(e => [e])),
    password: pipe(validatePassword(form.password), E.mapLeft(e => [e])),
  })
```

---

## 2. Async Pipelines: TaskEither

`TaskEither<E, A>` = an async operation that either fails with `E` or succeeds with `A`.

### Wrapping promises

```typescript
import * as TE from 'fp-ts/TaskEither'

const fetchJson = <T>(url: string): TE.TaskEither<Error, T> =>
  TE.tryCatch(
    async () => {
      const res = await fetch(url)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res.json()
    },
    (e) => (e instanceof Error ? e : new Error(String(e)))
  )
```

### Chaining with Do notation

```typescript
const processOrder = (orderId: string) =>
  pipe(
    TE.Do,
    TE.bind('order',   () => fetchOrder(orderId)),
    TE.bind('user',    ({ order }) => fetchUser(order.userId)),
    TE.bind('payment', ({ user, order }) => chargePayment(user, order.total)),
    TE.map(({ order, payment }) => ({
      orderId: order.id,
      paymentId: payment.id,
    }))
  )
```

### Parallel execution

```typescript
import { sequenceT } from 'fp-ts/Apply'

// Independent operations run in parallel
const getDashboard = (userId: string) =>
  pipe(
    sequenceT(TE.ApplyPar)(
      fetchUser(userId),
      fetchNotifications(userId),
      fetchActivity(userId)
    ),
    TE.map(([user, notifications, activity]) => ({ user, notifications, activity }))
  )

// Parallel over an array
const fetchAll = pipe(userIds, TE.traverseArray(fetchUser))
```

### Error recovery

```typescript
// Fallback chain
const getData = (id: string) =>
  pipe(
    fetchFromApi(id),
    TE.orElse(() => fetchFromCache(id)),
    TE.getOrElse(() => T.of(defaultValue))
  )

// Recover selectively by error tag
pipe(
  fetchUser(id),
  TE.orElse(err => {
    switch (err._tag) {
      case 'NotFound':    return TE.right(guestUser)
      case 'NetworkError': return fetchFromCache(id)
      default:            return TE.left(err)
    }
  })
)
```

### Retry with backoff

```typescript
const retry = <E, A>(
  op: TE.TaskEither<E, A>, max: number, delayMs = 1000
): TE.TaskEither<E, A> => {
  const attempt = (rem: number, delay: number): TE.TaskEither<E, A> =>
    pipe(
      op,
      TE.orElse(err =>
        rem <= 1
          ? TE.left(err)
          : pipe(
              TE.fromTask(() => new Promise(r => setTimeout(r, delay))),
              TE.chain(() => attempt(rem - 1, delay * 2))
            )
      )
    )
  return attempt(max, delayMs)
}
```

### Executing and unwrapping

```typescript
// fold collapses both channels into a single Task
const msg = await pipe(
  fetchUser(id),
  TE.fold(
    err  => T.of(`Error: ${err.message}`),
    user => T.of(`Hello, ${user.name}`)
  )
)()

// Or get raw Either
const result = await fetchUser(id)()  // Either<Error, User>
```

### Quick reference

| Goal | Combinator |
|------|-----------|
| Wrap promise | `TE.tryCatch(() => promise, toErr)` |
| Transform value | `TE.map(fn)` |
| Transform error | `TE.mapLeft(fn)` |
| Chain async ops | `TE.chain(fn)` / `TE.flatMap(fn)` |
| Run parallel | `sequenceT(TE.ApplyPar)(a, b, c)` |
| Traverse array | `TE.traverseArray(fn)(items)` |
| Recover | `TE.orElse(fn)` |
| Default value | `TE.getOrElse(() => T.of(x))` |
| Handle both | `TE.fold(onErr, onOk)` |
| Accumulate context | `TE.Do` + `TE.bind(...)` |
| Side effect | `TE.tap(fn)` / `TE.tapError(fn)` |
| Filter | `TE.filterOrElse(pred, toErr)` |

---

## 3. Backend DI: ReaderTaskEither

`ReaderTaskEither<R, E, A>` threads dependencies (`R`) through async pipelines automatically.

### Defining services

```typescript
import * as RTE from 'fp-ts/ReaderTaskEither'

type Deps = { db: DatabaseClient; logger: Logger; config: Config }

type UserError =
  | { _tag: 'UserNotFound'; id: string }
  | { _tag: 'EmailExists'; email: string }

export const findById = (
  id: string
): RTE.ReaderTaskEither<Deps, UserError, User> =>
  pipe(
    RTE.ask<Deps>(),
    RTE.flatMap(({ db }) =>
      pipe(
        RTE.fromTaskEither(db.users.findById(id)),
        RTE.flatMap(user =>
          user ? RTE.right(user) : RTE.left({ _tag: 'UserNotFound', id })
        )
      )
    )
  )
```

### Composing services

```typescript
type OrderDeps = UserDeps & ProductDeps & PaymentDeps

export const createOrder = (
  userId: string, items: OrderItem[]
): RTE.ReaderTaskEither<OrderDeps, OrderError, Order> =>
  pipe(
    RTE.Do,
    RTE.bind('user',     () => pipe(UserService.findById(userId), RTE.mapLeft(toOrderError))),
    RTE.bind('products', () => pipe(items, A.traverse(RTE.ApplicativePar)(
      i => ProductService.findById(i.productId)), RTE.mapLeft(toOrderError))),
    RTE.bind('payment',  ({ user, products }) =>
      pipe(PaymentService.charge(user, calcTotal(products, items)), RTE.mapLeft(toOrderError))),
    RTE.flatMap(ctx => persistOrder(ctx))
  )
```

### Layered dependency container

```typescript
// Layer 0: Config (env vars)
// Layer 1: Infrastructure (db, redis, logger) -- depends on config
// Layer 2: Services (hasher, jwt, mailer) -- depends on infra
export type AppDeps = Infrastructure & Services

export const buildDeps = (): TE.TaskEither<Error, AppDeps> =>
  pipe(
    loadConfig(),
    TE.flatMap(buildInfrastructure),
    TE.map(infra => ({ ...infra, ...buildServices(infra) }))
  )
```

### Express / Hono handler adapter

```typescript
// Convert RTE to Express handler
const toHandler = <R, E, A>(
  getDeps: (req: Request) => R,
  handler: (req: Request) => RTE.ReaderTaskEither<R, E, A>,
  onError: (error: E, res: Response) => void
): RequestHandler =>
  async (req, res) => {
    const result = await handler(req)(getDeps(req))()
    pipe(result, E.fold(e => onError(e, res), data => res.json(data)))
  }
```

### Transactions (Prisma)

```typescript
const withTransaction = <R extends { db: PrismaClient }, E, A>(
  program: RTE.ReaderTaskEither<R & { tx: TxClient }, E, A>
): RTE.ReaderTaskEither<R, E | DbError, A> =>
  pipe(
    RTE.ask<R>(),
    RTE.flatMap(deps =>
      RTE.fromTaskEither(TE.tryCatch(
        () => deps.db.$transaction(async tx => {
          const r = await program({ ...deps, tx })()
          if (r._tag === 'Left') throw r.left
          return r.right
        }),
        (e): E | DbError =>
          typeof e === 'object' && e !== null && '_tag' in e
            ? (e as E)
            : { _tag: 'UnknownDbError', cause: e }
      ))
    )
  )
```

### Testing with mock deps

```typescript
const mockDeps: Deps = {
  db: { users: { findById: vi.fn(() => Promise.resolve(null)) } },
  logger: { info: vi.fn() },
  config: testConfig,
}

it('returns UserNotFound', async () => {
  const result = await findById('x')(mockDeps)()
  expect(E.isLeft(result) && result.left._tag).toBe('UserNotFound')
})
```

---

## 4. React Integration

### Option state

```typescript
const [user, setUser] = useState<O.Option<User>>(O.none)

return pipe(
  user,
  O.match(
    () => <button onClick={() => setUser(O.some(fetchedUser))}>Log In</button>,
    (u) => <div>Welcome, {u.name}</div>
  )
)
```

### Either form validation

```typescript
const handleSubmit = () =>
  pipe(
    validateForm(form),
    E.match(
      errs  => setErrors(errs),
      valid => { setErrors([]); submitToServer(valid) }
    )
  )
```

### RemoteData (state machine for async UI)

```typescript
type RemoteData<E, A> =
  | { _tag: 'NotAsked' }
  | { _tag: 'Loading' }
  | { _tag: 'Failure'; error: E }
  | { _tag: 'Success'; data: A }

function fold<E, A, R>(
  rd: RemoteData<E, A>,
  cases: { notAsked: () => R; loading: () => R; failure: (e: E) => R; success: (a: A) => R }
): R {
  switch (rd._tag) {
    case 'NotAsked': return cases.notAsked()
    case 'Loading':  return cases.loading()
    case 'Failure':  return cases.failure(rd.error)
    case 'Success':  return cases.success(rd.data)
  }
}
```

This eliminates impossible states like `{ data: user, loading: true, error: someError }`.

### Referential stability

fp-ts values create new objects each render. Depend on raw primitives in `useEffect` deps, or use `useMemo`:

```typescript
const [rawValue, setRawValue] = useState<number | null>(1)
const optionValue = useMemo(() => O.fromNullable(rawValue), [rawValue])
```

For deep structural equality, use [fp-ts-react-stable-hooks](https://github.com/mblink/fp-ts-react-stable-hooks).

### React 19: useActionState + Either

```typescript
import { useActionState } from 'react'

async function submitAction(prev: FormState, fd: FormData): Promise<FormState> {
  const data = { email: fd.get('email') as string, password: fd.get('password') as string }
  return pipe(
    validateForm(data),
    E.match(
      errors => ({ errors, success: false }),
      async valid => { await saveToServer(valid); return { errors: [], success: true } }
    )
  )
}
```

---

## 5. Runtime Validation: io-ts / Schema

### io-ts (classic fp-ts companion)

```typescript
import * as t from 'io-ts'
import { PathReporter } from 'io-ts/PathReporter'
import * as E from 'fp-ts/Either'

const User = t.type({
  id: t.string,
  name: t.string,
  age: t.number,
  email: t.string,
})
type User = t.TypeOf<typeof User> // { id: string; name: string; age: number; email: string }

// Decode unknown data at runtime
const decode = (raw: unknown): E.Either<string[], User> =>
  pipe(
    User.decode(raw),
    E.mapLeft(errors => PathReporter.report(E.left(errors)))
  )
```

### io-ts branded types (refinements)

```typescript
import { withMessage } from 'io-ts-types'

interface PositiveIntBrand { readonly PositiveInt: unique symbol }
const PositiveInt = t.brand(
  t.number,
  (n): n is t.Branded<number, PositiveIntBrand> => Number.isInteger(n) && n > 0,
  'PositiveInt'
)

const Age = withMessage(PositiveInt, () => 'Age must be a positive integer')
```

### @effect/schema (modern alternative to io-ts)

`@effect/schema` provides the same decode-to-Either workflow with better ergonomics:

```typescript
import { Schema as S } from '@effect/schema'

const User = S.Struct({
  id: S.String,
  name: S.NonEmptyString,
  age: S.Number.pipe(S.int(), S.positive()),
  email: S.String.pipe(S.pattern(/@/)),
})
type User = S.Schema.Type<typeof User>

// Decode returns Either
const result: E.Either<ParseError, User> = S.decodeUnknownEither(User)(rawData)
```

### Integrating with TaskEither pipelines

```typescript
const parseAndFetch = (raw: unknown) =>
  pipe(
    TE.fromEither(decode(raw)),                      // validate input
    TE.flatMap(input => fetchJson<Result>(`/api/${input.id}`)), // then fetch
  )
```

---

## 6. Effect-TS: Modern Alternative to fp-ts

[Effect](https://effect.website) is a production-grade successor that unifies TaskEither, Reader, and more into a single `Effect<A, E, R>` type.

### Key differences from fp-ts

| fp-ts | Effect-TS |
|-------|-----------|
| `TaskEither<E, A>` | `Effect<A, E>` |
| `ReaderTaskEither<R, E, A>` | `Effect<A, E, R>` |
| `pipe(x, TE.map(f))` | `pipe(x, Effect.map(f))` or `x.pipe(Effect.map(f))` |
| Manual DI via Reader | Built-in `Layer` / `Context` system |
| Separate `Option`, `Either` modules | Unified with `Option` and `Either` still available |

### Basic Effect example

```typescript
import { Effect, pipe } from 'effect'

const fetchUser = (id: string) =>
  Effect.tryPromise({
    try: () => fetch(`/api/users/${id}`).then(r => r.json()),
    catch: (e) => new HttpError({ cause: e }),
  })

const program = pipe(
  fetchUser('1'),
  Effect.flatMap(user => sendWelcomeEmail(user.email)),
  Effect.catchTag('HttpError', () => Effect.succeed(fallbackUser)),
)

// Run the effect
Effect.runPromise(program)
```

### Dependency injection with Layers

```typescript
import { Effect, Context, Layer } from 'effect'

// Define a service tag
class Database extends Context.Tag('Database')<Database, {
  readonly findUser: (id: string) => Effect.Effect<User, NotFoundError>
}>() {}

// Implement the service
const DatabaseLive = Layer.succeed(Database, {
  findUser: (id) =>
    Effect.tryPromise({ try: () => prisma.user.findUnique({ where: { id } }), catch: toNotFound }),
})

// Use the service (requirement tracked in R)
const program = Effect.gen(function* () {
  const db = yield* Database
  const user = yield* db.findUser('1')
  return user
}) // Effect<User, NotFoundError, Database>

// Provide implementation at the edge
Effect.runPromise(program.pipe(Effect.provide(DatabaseLive)))
```

### When to choose Effect-TS over fp-ts

- Greenfield projects with complex concurrency (fibers, structured concurrency)
- Need built-in tracing, metrics, and retry policies
- Team willing to adopt a larger runtime
- fp-ts is stable but in maintenance mode; Effect is actively developed

fp-ts remains a solid choice for incremental adoption and smaller projects.

---

## 7. Functional Optics: Lenses and Prisms

Optics provide composable, immutable accessors for nested data. Use [monocle-ts](https://github.com/gcanti/monocle-ts) (fp-ts companion) or `@effect/optics`.

### Lens -- focus on a field in a product type

```typescript
import { Lens } from 'monocle-ts'

interface Address { street: string; city: string }
interface User { name: string; address: Address }

const addressLens = Lens.fromProp<User>()('address')
const cityLens    = Lens.fromProp<Address>()('city')

// Compose to reach nested fields
const userCity = addressLens.compose(cityLens)

const user: User = { name: 'Alice', address: { street: '1st', city: 'NYC' } }
userCity.get(user)                     // 'NYC'
const updated = userCity.set('LA')(user) // new User with city = 'LA', original unchanged
```

### Optional -- focus on a value that might be missing

```typescript
import { Optional } from 'monocle-ts'

interface Profile { user: User | null }

const userOptional = new Optional<Profile, User>(
  s => O.fromNullable(s.user),
  a => s => ({ ...s, user: a })
)

// Compose lens after optional
const profileCity = userOptional.compose(userCity)
profileCity.getOption(profile) // Option<string>
```

### Prism -- focus on one variant of a sum type

```typescript
import { Prism } from 'monocle-ts'

type Shape =
  | { _tag: 'Circle'; radius: number }
  | { _tag: 'Rect'; w: number; h: number }

const circlePrism = Prism.fromPredicate<Shape>(
  (s): s is Extract<Shape, { _tag: 'Circle' }> => s._tag === 'Circle'
)

circlePrism.getOption({ _tag: 'Circle', radius: 5 }) // Some({ _tag: 'Circle', radius: 5 })
circlePrism.getOption({ _tag: 'Rect', w: 3, h: 4 }) // None
```

### When to use optics

- Deeply nested immutable updates (3+ levels)
- Repeated access patterns across the codebase
- State management in Redux / Zustand / XState context

For shallow updates, spread syntax is simpler: `{ ...user, name: 'Bob' }`.

---

## Decision Guide

| Situation | Reach for |
|-----------|-----------|
| Nullable value, simple path | `?.` optional chaining |
| Nullable value, chained transforms | `Option` |
| Sync operation that can fail | `Either` |
| Multiple validation errors | `Either` + applicative validation |
| Async operation that can fail | `TaskEither` |
| Backend service with DI | `ReaderTaskEither` |
| Runtime input validation | `io-ts` or `@effect/schema` |
| Deep nested immutable updates | Lens / Optional (monocle-ts) |
| Greenfield, complex concurrency | Effect-TS |
| Team unfamiliar with FP | Start with `pipe` + `Either`, grow from there |

---

## Libraries

| Library | Purpose |
|---------|---------|
| [fp-ts](https://github.com/gcanti/fp-ts) | Core FP types and combinators |
| [io-ts](https://github.com/gcanti/io-ts) | Runtime type decoding (fp-ts companion) |
| [monocle-ts](https://github.com/gcanti/monocle-ts) | Functional optics (fp-ts companion) |
| [effect](https://effect.website) | Modern all-in-one FP runtime |
| [@effect/schema](https://github.com/Effect-TS/effect/tree/main/packages/schema) | Schema validation for Effect ecosystem |
| [@effect/optics](https://github.com/Effect-TS/effect/tree/main/packages/optics) | Optics for Effect ecosystem |
| [fp-ts-react-stable-hooks](https://github.com/mblink/fp-ts-react-stable-hooks) | Referentially stable React hooks |
| [@devexperts/remote-data-ts](https://github.com/devexperts/remote-data-ts) | RemoteData ADT |
| [zod](https://github.com/colinhacks/zod) | Schema validation (works well alongside fp-ts) |