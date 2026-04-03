---
name: wshobson-game-development
description: Game development patterns for Godot 4 GDScript and Unity ECS/DOTS
---

# Game Development

Covers Godot 4 GDScript patterns (signals, state machines, scenes, resources, object pooling, save systems) and Unity ECS/DOTS patterns (components, systems, jobs, Burst compiler, aspects, baking).

## Key Patterns

- **Godot: signals for decoupling** -- emit signals instead of calling methods on other nodes directly
- **Godot: state machine via Node children** -- each State is a child Node; StateMachine enables/disables processing
- **Godot: Resources for data** -- `extends Resource` with `@export` fields; duplicate at runtime to avoid shared mutation
- **Godot: object pooling** -- pre-instantiate nodes, toggle `visible`/`process_mode` instead of `queue_free()`/`instantiate()`
- **Godot: Autoload singletons sparingly** -- only for truly global systems (GameManager, EventBus)
- **Godot: type everything** -- static typing catches errors and enables better autocomplete
- **Unity ECS: ISystem over SystemBase** -- unmanaged, Burst-compatible, highest performance
- **Unity: Burst compile everything** -- `[BurstCompile]` on systems and jobs for massive speedup
- **Unity: EntityCommandBuffer for structural changes** -- never add/remove components inside jobs directly
- **Unity: Aspects group related components** -- `IAspect` for cleaner system code

## Quick Reference

### Godot: State machine skeleton

```gdscript
# state_machine.gd
class_name StateMachine
extends Node

@export var initial_state: State
var current_state: State
var states: Dictionary = {}

func _ready() -> void:
    for child in get_children():
        if child is State:
            states[child.name] = child
            child.state_machine = self
            child.process_mode = Node.PROCESS_MODE_DISABLED
    if initial_state:
        current_state = initial_state
        current_state.process_mode = Node.PROCESS_MODE_INHERIT
        current_state.enter()

func transition_to(state_name: StringName, msg: Dictionary = {}) -> void:
    var prev := current_state
    prev.exit()
    prev.process_mode = Node.PROCESS_MODE_DISABLED
    current_state = states[state_name]
    current_state.process_mode = Node.PROCESS_MODE_INHERIT
    current_state.enter(msg)
```

### Unity ECS: Burst-compiled system

```csharp
[BurstCompile]
public partial struct MovementSystem : ISystem
{
    [BurstCompile]
    public void OnUpdate(ref SystemState state)
    {
        float dt = SystemAPI.Time.DeltaTime;
        foreach (var (transform, speed) in
            SystemAPI.Query<RefRW<LocalTransform>, RefRO<Speed>>())
        {
            transform.ValueRW.Position +=
                new float3(0, 0, speed.ValueRO.Value * dt);
        }
    }
}
```

### Godot performance tips

```
1. Cache node refs with @onready     (avoid $Node in _process)
2. Object pool frequent spawns       (see Pattern above)
3. Reuse arrays in hot paths         (clear instead of new)
4. Static typing everywhere          (func calc(v: float) -> float)
5. Disable processing when off-screen (set_process(false))
```

### Unity ECS performance tips

```
1. [BurstCompile] on all systems and jobs
2. IJobEntity over manual iteration
3. ScheduleParallel when no write conflicts
4. Enableable components over add/remove (avoid structural changes)
5. Dispose NativeCollections to prevent leaks
```

## When to Use

- Building games in Godot 4 with GDScript (state machines, signals, scenes, save/load)
- Implementing Unity ECS/DOTS for high-entity-count simulations
- Optimizing game performance (object pooling, Burst compilation, cache-friendly data)
- Designing component-based game architectures
- Converting Unity OOP MonoBehaviour code to data-oriented ECS
