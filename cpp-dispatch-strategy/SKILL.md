---
name: cpp-dispatch-strategy
description: >
  Decision guide for choosing C++ dispatch mechanisms based on which architectural layer
  you are working in. The core model: every C++ codebase has three dispatch layers, each
  with its own correct mechanism — virtual OO at the architecture boundary, template traits
  in the compute layer, constexpr if at the hardware layer. Mixing mechanisms across layers
  is the root cause of most C++ dispatch performance and maintainability problems.
  Trigger: user is designing a C++ backend/plugin interface, choosing between virtual dispatch
  and templates, unsure which polymorphism mechanism to use, designing a numerical or compute
  kernel, asking "when should I use virtual functions vs templates", or working on a C++
  codebase with multiple swappable backends.
  Do NOT use for basic language questions ("how do I write a virtual function") or for
  non-C++ dispatch questions.
  Action: identifies which layer the user is working in, applies the matching mechanism,
  backs it up with the work-per-call rule and 8-dimension tradeoff matrix if needed, and
  shows the hybrid code pattern that combines all three layers correctly.
  Limitations: C++ only; assumes C++17 minimum (C++20 for Concepts); does not cover GPU
  kernel dispatch (CUDA), dynamic library loading (dlopen), or std::variant/std::visit in depth.
  Relationships: pairs with cpp-project-setup (project scaffolding and CMake); for naming
  the architecture layers use the naming-convention skill; does not apply to Rust or Python.
  Examples: "should I use virtual or templates for my plugin interface?" → identify layer
  (architecture), recommend OO, show hybrid pattern; "my hot loop is slow, I'm using virtual
  functions" → identify layer (compute), explain templates-win + work-per-call rule;
  "how do I handle CPU feature selection without runtime overhead?" → identify layer (hardware),
  show constexpr if pattern.
---

# C++ Dispatch Strategy — Three Layers, Three Mechanisms

Every C++ codebase that handles variability (multiple backends, pluggable strategies, hardware
paths) has three distinct layers of abstraction. Each layer has a natural dispatch mechanism.
Applying the wrong mechanism to a layer creates either unnecessary performance cost or
unnecessary design complexity.

**Step 1: identify the layer. Step 2: apply its mechanism.**

---

## The Three-Layer Model

```
┌──────────────────────────────────────────────────────────┐
│  ARCHITECTURE LAYER — Virtual OO                         │
│                                                          │
│  Question: "Which backend am I using?"                   │
│  Decided at: runtime (config, command-line, user input)  │
│  Mechanism: abstract base class + virtual dispatch       │
│  Cost: ~3 ns per coarse-grained call (noise)             │
├──────────────────────────────────────────────────────────┤
│  COMPUTE LAYER — Concepts-constrained templates          │
│                                                          │
│  Question: "How do I process each element?"              │
│  Decided at: compile time (type is known inside backend) │
│  Mechanism: template traits, monomorphization, inlining  │
│  Cost: zero (call disappears into generated code)        │
├──────────────────────────────────────────────────────────┤
│  HARDWARE LAYER — constexpr if                           │
│                                                          │
│  Question: "Which CPU path do I take?"                   │
│  Decided at: build time (CPU feature flags baked in)     │
│  Mechanism: constexpr if, eliminates dead branch fully   │
│  Cost: zero (dead branch never compiled)                 │
└──────────────────────────────────────────────────────────┘
```

The layers are nested: architecture layer selects the backend, compute layer runs inside it,
hardware layer runs inside the compute loop.

---

## Layer identification guide

### Are you at the architecture layer?

Yes if:
- The variant is selected at runtime (config file, command-line flag, user input, database row)
- You need to add new variants later without recompiling all callers
- The interface will cross a shared-library (`.so`/`.dll`) boundary
- Multiple callers use the same interface without knowing the concrete type

**→ Use virtual OO.** Abstract base class, pure virtual methods, concrete implementations in
separate translation units.

### Are you at the compute layer?

Yes if:
- You are *inside* a concrete backend implementation
- The concrete type is fixed from the moment you enter the function
- The function is called in a loop (potentially millions of times per operation)
- The body needs to inline for SIMD vectorization to work

**→ Use template traits.** Parameterize on the concrete type. The compiler stamps out
a specialized copy; the call disappears into inlined assembly.

### Are you at the hardware layer?

Yes if:
- The choice is a CPU feature (AVX2 vs. scalar, BMI2 vs. software fallback, NEON vs. x86)
- The feature set is fixed at build time (not runtime)
- You want zero overhead: no branch, no pointer, just the right code compiled in

**→ Use `constexpr if`.** The compiler evaluates the condition at compile time and discards
the dead branch entirely from the generated binary.

---

## Hybrid code pattern

The three layers nest naturally. The architecture layer dispatches once; the compute and
hardware layers run millions of times with zero overhead:

```cpp
// ── ARCHITECTURE LAYER: virtual OO ──────────────────────────────────
// Type selection happens at runtime (config/command-line chooses backend)
class ComputeBackend {
public:
    virtual void apply(Input& in, const Context& ctx) = 0;
    virtual double evaluate(const Input& in) const = 0;
    virtual ~ComputeBackend() = default;
};

// ── COMPUTE LAYER: templates ─────────────────────────────────────────
// Type is fixed inside ConcreteBackend; compiler monomorphizes and inlines
class ConcreteBackend : public ComputeBackend {
public:
    void apply(Input& in, const Context& ctx) override {
        // virtual dispatch got us here once (~3 ns, irrelevant)
        // now hand off to the template compute layer:
        process_elements</*HasAVX2=*/true>(in.items(), ctx.generator());
    }

private:
    template <bool HardwareCap>
    void process_elements(ItemStore& items, const WorkUnit& unit) {
        #pragma omp parallel for schedule(dynamic)
        for (size_t i = 0; i < items.size(); ++i) {
            // ── HARDWARE LAYER: constexpr if ──────────────────────────
            // Dead branch eliminated at compile time; no runtime branch
            if constexpr (HardwareCap) {
                items.update(i, fast_compute(items.packed(i), unit));
            } else {
                items.update(i, scalar_compute(items.packed(i), unit));
            }
        }
    }
};
```

The vtable boundary is crossed **once** per coarse operation (~3 ns, irrelevant against the
work inside). The compile-time boundaries are crossed **millions of times** — zero overhead,
vectorizable by the compiler.

**This pattern appears throughout production C++:**
- **Eigen**: templates for inner-loop math, function-pointer dispatch for BLAS/LAPACK
- **LLVM**: virtual classes for the pass infrastructure, templates for IR manipulation
- **VTK**: virtual hierarchies for pipeline filters, templates parameterized on scalar type for inner pixel loops

---

## When layers are ambiguous — the 4-question checklist

If you are unsure which layer you are in, answer these four questions:

| Question | Points to |
|---|---|
| Is the concrete type known at compile time? | No → OO; Yes → templates |
| Is the call in a tight inner loop (< 100 ns work per call)? | Yes → templates; No → OO is fine |
| Do you need separate compilation or a stable ABI? | Yes → OO |
| Is the team fluent in template metaprogramming? | No → prefer OO |

### Work-per-call rule (simplest heuristic)

Look at how much work happens *inside* the dispatched call:

| Work per call | Mechanism | Why |
|---|---|---|
| < 10 ns (bit ops, arithmetic) | Template / inline | Vtable cost ≈ work cost; dispatch dominates |
| 10–100 ns (small functions) | Grey zone — measure | Depends on call frequency and cache |
| > 100 ns (kernel-level) | OO is fine | Dispatch overhead is unmeasurable noise |

---

## The 8-dimension tradeoff matrix (reference)

| Dimension | Virtual OO | Templates (traits) |
|---|---|---|
| Runtime cost | Vtable indirection (~1–5 ns) | Zero (inlined) |
| Compile time | Fast (separate compilation) | Slow (headers everywhere) |
| Binary size | One copy per function | N copies (code bloat) |
| Add new variant | New `.cpp` + relink | Recompile all callers |
| ABI stability | Stable across `.so` boundary | None (header-only) |
| Error messages | Clear type-mismatch errors | Template error novels |
| Debuggability | `gdb` shows real types | Mangled symbol names |
| Runtime type switch | Natural (swap pointer) | Impossible without type erasure |

**API vs. ABI:**
- **API** = source-level contract (function names, types, signatures)
- **ABI** = binary-level contract (memory layout, vtable structure, calling conventions)

OO fixes the ABI because the abstract base class header locks the vtable layout. A new
backend compiled into a separate `.so` loads against an old binary without recompilation.
Templates destroy ABI stability — the full implementation lives in headers.

---

## Where templates win (3 signatures)

**Signature 1 — Type fixed at compile time.** CPU feature flags, platform selection,
compile-time configuration: use `constexpr if`. The compiler eliminates the dead branch.

**Signature 2 — Trivial body that must inline.** Functions called inside tight loops do
nanoseconds of work. Virtual dispatch would dominate, and the vtable call is an opaque wall
that blocks SIMD auto-vectorization entirely.

**Signature 3 — Optimization across the call boundary.** When the compiler sees the full
template implementation in a header, it can inline, constant-propagate, dead-code-eliminate,
and auto-vectorize. A virtual call is an opaque boundary that prevents all of these.

---

## CRTP + C++20 Concepts (complements, not replacements)

**CRTP** (Curiously Recurring Template Pattern) gives virtual-like behavior without a vtable
by inheriting from a template parameterized on the derived class. But `Base<A>` and `Base<B>`
are *different types* — no common base pointer exists. The moment you need runtime backend
selection, CRTP requires type erasure, which is just a hand-rolled vtable.

**C++20 Concepts** constrain the compute-layer template with named, readable requirements:

```cpp
template <typename B>
concept Backend = requires(B b, Input& in, const Context& ctx) {
    { b.apply(in, ctx)   } -> std::same_as<void>;
    { b.evaluate(in)     } -> std::same_as<double>;
};
```

Concepts improve the compute layer's error messages and serve as executable documentation.
They do *not* solve runtime-dispatch problems.

> CRTP and Concepts belong in the **compute layer**. They cannot replace OO at the
> **architecture layer** when runtime backend selection is required.

---

## Virtual syntax cheat-sheet

These three uses of `virtual` are unrelated to each other and frequently confused:

| Syntax | Meaning |
|---|---|
| `virtual void f()` | Dispatched through vtable at runtime |
| `virtual void f() = 0` | Pure virtual — derived class *must* implement; class is abstract |
| `class B : virtual public A` | Shared base in diamond inheritance — unrelated to dispatch |
| `virtual class X` | **Does not exist in C++** |

The architecture-layer pattern uses abstract classes (pure virtual = 0) exclusively.
Virtual base classes (diamond inheritance) are a separate mechanism rarely needed in practice.
