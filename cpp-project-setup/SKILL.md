---
name: cpp-project-setup
description: "Step-by-step guide for bootstrapping a modern C++23 project from scratch: git init, CMake project layout with include/src/tests, CMakeLists.txt, CMakePresets.json, clang-format, clang-tidy, sanitizers (ASan/UBSan/TSan), unit tests via Catch2 or GoogleTest (asks the user) with 100% coverage enforcement, optional external dependencies via vcpkg or Conan, pre-commit hooks, TDD workflow, and per-project .claude/ directory with its own CLAUDE.md, permissions, agents, and MCP servers. Use this skill whenever the user asks how to start a new C++ project, set up modern C++ tooling, enforce TDD, configure clang-format / clang-tidy / sanitizers / vcpkg / Conan, structure a C++ codebase from zero, or set up Claude Code for a C++ project."
---

# C++ Project Setup — Modern Toolchain & TDD

This skill walks through every step of starting a modern C++ project correctly, in order. No steps are skipped. The result is a project where bad code physically cannot be committed: the compiler is strict, lints run pre-commit, tests are mandatory, and undefined behavior is caught by sanitizers in CI.

---

## Step 1 — Create the project folder and init git

```bash
mkdir my_project && cd my_project
git init
```

Create a `.gitignore` immediately — before any files exist — so nothing leaks into git by accident:

```
# Build directories
build/
build-*/
out/
cmake-build-*/

# Compiled artifacts
*.o
*.obj
*.a
*.lib
*.so
*.so.*
*.dylib
*.dll
*.exe

# Coverage
*.gcov
*.gcda
*.gcno
coverage/
*.profraw
*.profdata

# Editor
.vscode/
.idea/
.cache/
compile_commands.json

# Sanitizer / debugger output
*.dSYM/
core
core.*
```

```bash
git add .gitignore
git commit -m "init: add .gitignore"
```

---

## Step 2 — Pick the compiler and C++ standard

This skill defaults to **C++23**. To target C++20 instead, change `set(CMAKE_CXX_STANDARD 23)` → `20` and `Standard: c++23` → `c++20` in `.clang-format`.

Verify a recent compiler is on `PATH`:

```bash
g++ --version       # GCC ≥ 13 for C++23 (≥ 12 covers C++20)
clang++ --version   # Clang ≥ 17 for C++23 (≥ 14 covers C++20)
cmake --version     # ≥ 3.21 (presets); ≥ 3.25 recommended
```

If you need to install or pin compilers:

- **Linux**: `apt install gcc-13 g++-13 clang-17 clang-tidy-17 clang-format-17`
- **macOS**: `brew install llvm@17 cmake ninja gcovr` (and `clang-format` via the same llvm package)
- **Multiple compilers side-by-side**: use [`update-alternatives`](https://manpages.ubuntu.com/manpages/man1/update-alternatives.1.html) on Linux, or symlink specific versions in `~/bin/`.

Decide once and pin in CMake:

```cmake
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)   # use -std=c++23, not -std=gnu++23
```

---

## Step 3 — Establish the folder structure

Use **`include/` + `src/` separation**. This is the modern standard. Public headers go under `include/<project_name>/` so consumers `#include <my_project/foo.hpp>`. Implementation headers and `.cpp` files live in `src/`.

```
my_project/
├── include/
│   └── my_project/             # public headers (the API)
│       └── my_project.hpp
├── src/                        # implementation files + private headers
│   ├── my_project.cpp
│   └── CMakeLists.txt
├── tests/                      # unit tests (Catch2)
│   ├── test_my_project.cpp
│   └── CMakeLists.txt
├── apps/                       # optional command-line executables
├── benchmarks/                 # optional google-benchmark micro-benchmarks
├── examples/                   # optional usage examples
├── cmake/                      # reusable CMake helper modules
│   └── ProjectWarnings.cmake
├── CMakeLists.txt              # top-level: project(), options, subdirs
├── CMakePresets.json           # debug / release / asan / ubsan / coverage
├── .clang-format
├── .clang-tidy
├── .pre-commit-config.yaml
├── Makefile                    # thin wrapper around cmake / ctest
└── .gitignore
```

Create the scaffold:

```bash
mkdir -p include/my_project src tests cmake apps examples benchmarks

# Public header
cat > include/my_project/my_project.hpp << 'EOF'
#pragma once

namespace my_project {

[[nodiscard]] int add(int a, int b) noexcept;

}  // namespace my_project
EOF

# Implementation
cat > src/my_project.cpp << 'EOF'
#include "my_project/my_project.hpp"

namespace my_project {

int add(int a, int b) noexcept { return a + b; }

}  // namespace my_project
EOF
```

**Why `include/` + `src/`?**
- Public API is visually obvious: anything in `include/` is a contract; anything else is internal.
- `target_include_directories(my_project PUBLIC include)` exposes only the public surface.
- Consumers using `find_package(my_project)` or `add_subdirectory(my_project)` get a clean header set.

---

## Step 4 — Write the top-level CMakeLists.txt

One file is the **single source of truth** for the build — like `pyproject.toml` is for Python. Keep it short; delegate to `src/CMakeLists.txt` and `tests/CMakeLists.txt`.

```cmake
cmake_minimum_required(VERSION 3.21)

project(my_project
    VERSION 0.1.0
    DESCRIPTION "Short description"
    LANGUAGES CXX)

# ── Standard ──────────────────────────────────────────────────────────────────
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Always export compile_commands.json so clangd / clang-tidy work out of the box
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ── Options ───────────────────────────────────────────────────────────────────
option(MY_PROJECT_BUILD_TESTS      "Build unit tests"        ON)
option(MY_PROJECT_BUILD_BENCHMARKS "Build micro-benchmarks"  OFF)
option(MY_PROJECT_ENABLE_COVERAGE  "Enable code coverage"    OFF)
option(MY_PROJECT_ENABLE_ASAN      "Enable AddressSanitizer" OFF)
option(MY_PROJECT_ENABLE_UBSAN     "Enable UBSanitizer"      OFF)
option(MY_PROJECT_ENABLE_TSAN      "Enable ThreadSanitizer"  OFF)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
include(ProjectWarnings)

# ── Library target ────────────────────────────────────────────────────────────
add_subdirectory(src)

# ── Tests ─────────────────────────────────────────────────────────────────────
if(MY_PROJECT_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# ── Benchmarks (optional) ─────────────────────────────────────────────────────
if(MY_PROJECT_BUILD_BENCHMARKS)
    add_subdirectory(benchmarks)
endif()
```

### `src/CMakeLists.txt`

```cmake
add_library(my_project
    my_project.cpp)

target_include_directories(my_project
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>)

target_compile_features(my_project PUBLIC cxx_std_23)

# Apply project-wide strict warnings
project_apply_warnings(my_project)

# Sanitizer / coverage flags (applied conditionally via options)
if(MY_PROJECT_ENABLE_ASAN)
    target_compile_options(my_project PUBLIC -fsanitize=address -fno-omit-frame-pointer)
    target_link_options   (my_project PUBLIC -fsanitize=address)
endif()
if(MY_PROJECT_ENABLE_UBSAN)
    target_compile_options(my_project PUBLIC -fsanitize=undefined)
    target_link_options   (my_project PUBLIC -fsanitize=undefined)
endif()
if(MY_PROJECT_ENABLE_TSAN)
    target_compile_options(my_project PUBLIC -fsanitize=thread)
    target_link_options   (my_project PUBLIC -fsanitize=thread)
endif()
if(MY_PROJECT_ENABLE_COVERAGE)
    target_compile_options(my_project PUBLIC --coverage -O0 -g)
    target_link_options   (my_project PUBLIC --coverage)
endif()
```

### `cmake/ProjectWarnings.cmake`

The single place that defines what "strict" means. Used by every target.

```cmake
# Strict, non-negotiable warnings. Treat warnings as errors.
function(project_apply_warnings TARGET)
    if(MSVC)
        target_compile_options(${TARGET} PRIVATE
            /W4 /WX /permissive-)
    else()
        target_compile_options(${TARGET} PRIVATE
            -Wall -Wextra -Werror -Wpedantic
            -Wshadow -Wnon-virtual-dtor -Wold-style-cast
            -Wcast-align -Woverloaded-virtual -Wconversion
            -Wsign-conversion -Wnull-dereference -Wdouble-promotion
            -Wformat=2 -Wimplicit-fallthrough)
    endif()
endfunction()
```

**Key decisions:**
- `-Werror` / `/WX` — warnings are errors. If the build succeeds, code is clean.
- `-Wshadow`, `-Wconversion`, `-Wsign-conversion` — catch entire classes of bugs the basic `-Wall` misses.
- Sanitizers are **opt-in via options**, not always on, so release builds stay fast.

---

## Step 5 — Write CMakePresets.json

`CMakePresets.json` replaces a sprawl of build scripts. Each preset is a named build configuration. Switch with `cmake --preset <name>`.

```json
{
  "version": 3,
  "cmakeMinimumRequired": { "major": 3, "minor": 21, "patch": 0 },
  "configurePresets": [
    {
      "name": "base",
      "hidden": true,
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "debug",
      "inherits": "base",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "Debug" }
    },
    {
      "name": "release",
      "inherits": "base",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "Release" }
    },
    {
      "name": "asan",
      "inherits": "debug",
      "cacheVariables": {
        "MY_PROJECT_ENABLE_ASAN":  "ON",
        "MY_PROJECT_ENABLE_UBSAN": "ON"
      }
    },
    {
      "name": "tsan",
      "inherits": "debug",
      "cacheVariables": { "MY_PROJECT_ENABLE_TSAN": "ON" }
    },
    {
      "name": "coverage",
      "inherits": "debug",
      "cacheVariables": { "MY_PROJECT_ENABLE_COVERAGE": "ON" }
    }
  ],
  "buildPresets": [
    { "name": "debug",    "configurePreset": "debug" },
    { "name": "release",  "configurePreset": "release" },
    { "name": "asan",     "configurePreset": "asan" },
    { "name": "tsan",     "configurePreset": "tsan" },
    { "name": "coverage", "configurePreset": "coverage" }
  ],
  "testPresets": [
    { "name": "debug",    "configurePreset": "debug",    "output": { "outputOnFailure": true } },
    { "name": "asan",     "configurePreset": "asan",     "output": { "outputOnFailure": true } },
    { "name": "coverage", "configurePreset": "coverage", "output": { "outputOnFailure": true } }
  ]
}
```

**Usage:**

```bash
cmake --preset debug          # configure
cmake --build --preset debug  # build
ctest --preset debug          # test

cmake --preset asan && cmake --build --preset asan && ctest --preset asan
cmake --preset coverage && cmake --build --preset coverage && ctest --preset coverage
```

Each preset gets its own `build/<preset>/` directory. Switching presets does not invalidate other build trees.

---

## Step 6 — Set up unit tests

> **Decision — Catch2 or GoogleTest?**
> Before scaffolding tests, **ask the user** which framework they want:
>
> - **Catch2 v3** (default) — single-header style, less ceremony, great error output, `REQUIRE`/`CHECK` macros, simple tag-based filtering. Best for new projects and solo developers.
> - **GoogleTest** — more enterprise pedigree, richer mocking via GoogleMock, larger ecosystem of fixtures and assertions. Best if the project will be consumed by Google-style codebases or needs heavy mocking.
>
> Both wire identically through CMake's `FetchContent`. Pick once — mixing them is confusing.

The default below is **Catch2**. Skip to the GoogleTest variant further down if the user picked GoogleTest.

### Variant A — Catch2 v3 (default)

`tests/CMakeLists.txt`:

```cmake
include(FetchContent)
FetchContent_Declare(
    Catch2
    GIT_REPOSITORY https://github.com/catchorg/Catch2.git
    GIT_TAG        v3.5.4
)
FetchContent_MakeAvailable(Catch2)

list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)

add_executable(test_my_project
    test_my_project.cpp)

target_link_libraries(test_my_project
    PRIVATE my_project Catch2::Catch2WithMain)

project_apply_warnings(test_my_project)

include(CTest)
include(Catch)
catch_discover_tests(test_my_project)
```

`tests/test_my_project.cpp`:

```cpp
#include "my_project/my_project.hpp"

#include <catch2/catch_test_macros.hpp>

TEST_CASE("add returns the sum of two ints", "[my_project][add]") {
    REQUIRE(my_project::add(2, 3) == 5);
    REQUIRE(my_project::add(-1, 1) == 0);
    REQUIRE(my_project::add(0, 0) == 0);
}
```

`catch_discover_tests` registers every `TEST_CASE` as a separate ctest — so failing tests show up individually in CI, not as one big rolled-up failure.

### Variant B — GoogleTest (if the user picked it)

`tests/CMakeLists.txt`:

```cmake
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
)
# Prevent gtest from overriding compiler/linker options on Windows
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(test_my_project
    test_my_project.cpp)

target_link_libraries(test_my_project
    PRIVATE my_project GTest::gtest_main)

project_apply_warnings(test_my_project)

include(CTest)
include(GoogleTest)
gtest_discover_tests(test_my_project)
```

`tests/test_my_project.cpp`:

```cpp
#include "my_project/my_project.hpp"

#include <gtest/gtest.h>

TEST(MyProjectAdd, ReturnsSumOfTwoInts) {
    EXPECT_EQ(my_project::add(2, 3),  5);
    EXPECT_EQ(my_project::add(-1, 1), 0);
    EXPECT_EQ(my_project::add(0, 0),  0);
}
```

For mocking, swap `GTest::gtest_main` for `GTest::gmock_main` and `#include <gmock/gmock.h>`.

### Build and run (either variant)

```bash
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
```

---

## External dependencies — vcpkg or Conan (optional)

`FetchContent` works for one-off dependencies (the test framework above), but real projects usually need many libraries — Boost, fmt, spdlog, Eigen, abseil, etc. Two free, mature C++ package managers handle this:

- **[vcpkg](https://vcpkg.io)** (Microsoft, MIT-licensed) — manifest mode, integrates via a CMake toolchain file. Best for purely-CMake projects.
- **[Conan](https://conan.io)** (JFrog, MIT-licensed) — Python-based, generates CMake files you `include()`. Best when you also distribute binaries or use multiple build systems.

> **Decision — which one?**
> Before adding either to a project, **ask the user**: vcpkg or Conan, or stick with `FetchContent`? If they have no preference, default to **vcpkg manifest mode** (less Python plumbing, integrates more cleanly with modern CMake).

### Variant A — vcpkg manifest mode

Bootstrap once per machine:

```bash
git clone https://github.com/microsoft/vcpkg.git ~/.vcpkg
~/.vcpkg/bootstrap-vcpkg.sh                    # Linux/macOS
# ~/.vcpkg/bootstrap-vcpkg.bat                 # Windows
export VCPKG_ROOT=~/.vcpkg                      # add to ~/.bashrc / ~/.zshrc
```

Add a `vcpkg.json` at the project root:

```json
{
  "name": "my-project",
  "version-string": "0.1.0",
  "dependencies": [
    "fmt",
    "spdlog",
    "eigen3"
  ]
}
```

Add the toolchain to `CMakePresets.json` (top-level `cacheVariables`):

```json
"cacheVariables": {
  "CMAKE_TOOLCHAIN_FILE": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
}
```

Use the libraries in CMake:

```cmake
find_package(fmt    CONFIG REQUIRED)
find_package(spdlog CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)

target_link_libraries(my_project
    PUBLIC fmt::fmt spdlog::spdlog Eigen3::Eigen)
```

vcpkg will fetch, build, and cache the libraries on first `cmake --preset debug`.

### Variant B — Conan

Bootstrap once per machine:

```bash
pip install --user conan
conan profile detect --force
```

Add a `conanfile.txt` at the project root:

```ini
[requires]
fmt/10.2.1
spdlog/1.13.0
eigen/3.4.0

[generators]
CMakeDeps
CMakeToolchain

[layout]
cmake_layout
```

Install dependencies:

```bash
conan install . --build=missing --output-folder=build/conan
```

Tell CMake to use Conan's toolchain (add to `CMakePresets.json` `cacheVariables`):

```json
"cacheVariables": {
  "CMAKE_TOOLCHAIN_FILE": "${sourceDir}/build/conan/conan_toolchain.cmake"
}
```

Then use libraries the same way as with vcpkg:

```cmake
find_package(fmt    REQUIRED)
find_package(spdlog REQUIRED)
find_package(Eigen3 REQUIRED)
```

### Comparison

| | vcpkg | Conan | FetchContent |
|---|---|---|---|
| Install once | `bootstrap-vcpkg.sh` | `pip install conan` | (none, built into CMake) |
| Per-project file | `vcpkg.json` | `conanfile.txt` | `FetchContent_Declare` in CMakeLists |
| Library cache | Per-machine, shared | Per-machine, shared | Per-build, recompiled |
| Best for | New projects, CMake-only | Multi-language, binary distribution | One-off deps (test frameworks) |

Whichever you pick, **use only one per project**. Mixing is painful.

---

## Step 7 — Configure clang-format and clang-tidy

These are the C++ analogs of `ruff` (format + lint) and `mypy` (static analysis). Ship config files at the project root so every developer and CI runner gets the same behavior.

### `.clang-format`

```yaml
# Based on LLVM style with project tweaks
BasedOnStyle: LLVM
Language: Cpp
Standard: c++23
ColumnLimit: 100
IndentWidth: 4
TabWidth: 4
UseTab: Never
PointerAlignment: Left
ReferenceAlignment: Left
AllowShortFunctionsOnASingleLine: Empty
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false
BreakBeforeBraces: Attach
NamespaceIndentation: None
SortIncludes: CaseSensitive
IncludeBlocks: Regroup
SpaceAfterCStyleCast: false
SpacesBeforeTrailingComments: 2
```

### `.clang-tidy`

Pick checks that catch real bugs and modernization opportunities. Disable the noisy or stylistic ones.

```yaml
Checks: >
    bugprone-*,
    modernize-*,
    performance-*,
    readability-*,
    cppcoreguidelines-*,
    -modernize-use-trailing-return-type,
    -readability-identifier-length,
    -readability-magic-numbers,
    -cppcoreguidelines-avoid-magic-numbers,
    -cppcoreguidelines-pro-bounds-pointer-arithmetic,
    -cppcoreguidelines-pro-bounds-array-to-pointer-decay,
    -cppcoreguidelines-pro-type-vararg

WarningsAsErrors: '*'
HeaderFilterRegex: '^.*include/my_project/.*\.hpp$'
FormatStyle: file
```

**Run them manually first:**

```bash
clang-format -i $(git ls-files '*.cpp' '*.hpp')        # format in place
clang-tidy -p build/debug $(git ls-files '*.cpp')      # lint
```

`compile_commands.json` (auto-generated by CMake) tells clang-tidy how to compile each file. Without it, clang-tidy doesn't know your include paths or flags.

---

## Step 8 — Configure pre-commit hooks

Pre-commit is the same tool used by Python projects, and works perfectly with C++. Install it once:

```bash
pip install --user pre-commit
# or: brew install pre-commit
```

There are two ways to configure the hooks. Pick one per project.

### Option A — Remote repos (default, recommended for shared projects)

Pre-commit downloads and manages clang-format / clang-tidy itself. Versions are pinned in the config — consistent across all developer machines.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-clang-format
    rev: v17.0.6
    hooks:
      - id: clang-format
        types_or: [c++, c]

  - repo: https://github.com/pocc/pre-commit-hooks
    rev: v1.3.5
    hooks:
      - id: clang-tidy
        args: [-p=build/debug, --warnings-as-errors=*]

  - repo: https://github.com/cheshirekow/cmake-format-precommit
    rev: v0.6.13
    hooks:
      - id: cmake-format
      - id: cmake-lint
```

### Option B — System tools (recommended for solo projects)

Use the exact `clang-format` and `clang-tidy` already on your `PATH`. Single source of truth for tool versions.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: clang-format
        name: clang-format
        language: system
        entry: clang-format -i
        types_or: [c++, c]

      - id: clang-tidy
        name: clang-tidy
        language: system
        entry: clang-tidy -p build/debug --warnings-as-errors=*
        types: [c++]
        pass_filenames: true
```

**Tradeoff summary:**

| | Option A (remote) | Option B (system) |
|---|---|---|
| Tool versions | Pre-commit manages its own | Your system clang-format / clang-tidy |
| Setup | Works on any machine | Requires clang tools installed |
| Consistency with `make check` | May differ | Always identical |
| Best for | Team projects, CI | Solo projects, tight control |

Install the hooks:

```bash
pre-commit install
```

From now on, every `git commit` runs clang-format and clang-tidy. A failing hook blocks the commit.

---

## Step 9 — Add a Makefile

`make check` is the single command to run the entire quality suite locally. It wraps cmake + ctest + clang-tidy + coverage so you don't need to remember the long flag combinations.

```makefile
.PHONY: help configure build test asan tsan coverage tidy format check clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

configure: ## Configure debug build
	cmake --preset debug

build: configure ## Build (debug)
	cmake --build --preset debug

test: build ## Run unit tests (debug)
	ctest --preset debug

asan: ## Build + run tests under AddressSanitizer + UBSan
	cmake --preset asan && cmake --build --preset asan && ctest --preset asan

tsan: ## Build + run tests under ThreadSanitizer
	cmake --preset tsan && cmake --build --preset tsan && ctest --preset tsan

coverage: ## Build + run tests with coverage; report
	cmake --preset coverage && cmake --build --preset coverage && ctest --preset coverage
	gcovr --root . --filter 'src/' --filter 'include/' \
	      --txt --print-summary \
	      --fail-under-line 100 \
	      --object-directory build/coverage

tidy: build ## Run clang-tidy on all source files
	clang-tidy -p build/debug --warnings-as-errors=* $$(git ls-files 'src/*.cpp' 'src/*.hpp')

format: ## Auto-format all C++ files in place
	clang-format -i $$(git ls-files '*.cpp' '*.hpp')

check: format tidy test asan coverage ## Full quality suite

clean: ## Remove all build directories
	rm -rf build/
```

`gcovr --fail-under-line 100` is the C++ analog of pytest's `fail_under = 100`. Coverage is enforced — not aspirational.

---

## Step 10 — Commit the project skeleton

```bash
git add CMakeLists.txt CMakePresets.json src/ include/ tests/ cmake/ \
        .clang-format .clang-tidy .pre-commit-config.yaml Makefile
git commit -m "init: project scaffold with toolchain"
```

Pre-commit runs for the first time — it auto-formats and lints the files you just staged.

---

## TDD Workflow — The Daily Loop

TDD has one rule: **tests are the specification. Code is the implementation.** The test is written first, against an interface that does not exist yet.

### The cycle

```
1. Write a failing test in tests/test_*.cpp
2. ctest --preset debug → see RED (test fails, often a link error or REQUIRE failure)
3. Write the minimum code in src/ to make the test pass
4. ctest --preset debug → see GREEN
5. Refactor if needed → ctest still GREEN
6. make check → full suite passes (format + tidy + tests + asan + coverage)
7. git commit
```

### Enforce the cycle with coverage

`gcovr --fail-under-line 100` causes `make coverage` to fail if any line in `src/` is not executed by a test. Untested code paths cannot be merged.

```bash
make coverage
# ...
# error: failed minimum line coverage (got 87.0%, minimum 100.0%)
```

### Slow tests

Mark long-running tests so they're excluded from the inner TDD loop. Catch2 supports tags:

```cpp
TEST_CASE("full convergence run", "[.slow]") {  // dot prefix = excluded by default
    // ...
}
```

Run only fast tests (default):

```bash
ctest --preset debug
```

Run all including slow ones:

```bash
ctest --preset debug -V                     # all visible tests
./build/debug/tests/test_my_project '[.]'   # explicitly include hidden tags
```

### Sanitizer-driven testing

Run the test suite under sanitizers regularly — they catch undefined behavior, use-after-free, data races that pass in normal Debug builds.

```bash
make asan      # AddressSanitizer + UBSanitizer
make tsan      # ThreadSanitizer (run separately — incompatible with ASan)
```

CI should run **all three** of: `make test` (debug), `make asan`, `make coverage`. Adding `make tsan` is recommended if the codebase has any threading.

### Test file naming and layout

```
tests/
├── CMakeLists.txt
├── test_my_project.cpp        # one file per source unit
└── test_another_module.cpp
```

- One test file per source unit — easy to find tests for any given file.
- Test case names describe behavior: `TEST_CASE("add returns sum of two ints")`, not `TEST_CASE("test1")`.
- Group with tags: `[my_project][add]` lets you run subsets via `ctest -R '\[add\]'`.

### Compiler warnings are non-negotiable

With `-Werror`, this is rejected at compile time:

```cpp
int add(int a, int b) {
    int unused;          // ❌ -Wunused-variable → build fails
    return a + b;
}
```

Warnings are catching bugs you would otherwise debug at runtime. Treat the compiler as a free static analyzer.

---

## Full bootstrap command sequence

```bash
# 1. Create project
mkdir my_project && cd my_project
git init

# 2. Gitignore
# (create .gitignore as shown above)
git add .gitignore && git commit -m "init: add .gitignore"

# 3. Scaffold
mkdir -p include/my_project src tests cmake apps examples benchmarks
# (create headers, src files, CMakeLists.txt files, presets, config files as shown)

# 4. Configure & build
cmake --preset debug
cmake --build --preset debug
ctest --preset debug

# 5. Install pre-commit hooks
pre-commit install

# 6. Commit skeleton
git add CMakeLists.txt CMakePresets.json src/ include/ tests/ cmake/ \
        .clang-format .clang-tidy .pre-commit-config.yaml Makefile
git commit -m "init: project scaffold with toolchain"

# 7. Start TDD
# Write tests/test_*.cpp first, then implement in src/
```

---

## Step 11 — Create per-project .claude/

Every project gets its own `.claude/` directory. This gives Claude Code project-specific context, permissions, agents, and MCP servers — independent of the user's global `~/.claude/` settings.

```
my_project/
└── .claude/
    ├── CLAUDE.md              # Project-specific instructions for Claude
    ├── settings.local.json    # Project permissions + MCP servers (gitignored)
    └── agents/                # Custom sub-agent definitions for this project
        └── codebase-reviewer.md
```

### `.claude/CLAUDE.md` — Instructions for Claude

This is the first file Claude reads when opening this project. Write it for Claude, not for humans. Keep it short and authoritative.

```markdown
# Project: my_project

## Environment
- C++23 via GCC ≥ 12 or Clang ≥ 14
- CMake ≥ 3.21, Ninja, clang-format, clang-tidy, gcovr
- Build directories: `build/debug`, `build/asan`, `build/coverage` (all gitignored)

## Toolchain
- Configure: `cmake --preset debug`
- Build:     `cmake --build --preset debug`
- Tests:     `ctest --preset debug`
- Format:    `make format`
- Lint:      `make tidy`
- Sanitize:  `make asan` and `make tsan`
- Coverage:  `make coverage`
- Full:      `make check`

## Rules
- Tests are the specification. Never modify a test to make it pass.
- Coverage is enforced at 100%. Every new code path needs a test.
- `-Werror` is on. The build either succeeds clean or fails — there are no warnings.
- Pre-commit hooks must pass. Never use `--no-verify`.
- Run `make asan` before declaring a feature done — UB hides in seemingly-passing tests.

## Before making changes
1. Run `make check` — it must pass before you start
2. Read the relevant header in `include/my_project/` to understand the public contract
```

### `.claude/settings.local.json` — Permissions and MCP servers

Pre-approve the commands Claude will need so it does not prompt on every run:

```json
{
  "permissions": {
    "allow": [
      "Bash(make check)",
      "Bash(make build)",
      "Bash(make test)",
      "Bash(make asan)",
      "Bash(make coverage)",
      "Bash(make tidy)",
      "Bash(make format)",
      "Bash(cmake --preset *)",
      "Bash(cmake --build --preset *)",
      "Bash(ctest --preset *)",
      "Bash(clang-format*)",
      "Bash(clang-tidy*)",
      "Bash(gcovr*)",
      "Bash(pre-commit run*)"
    ]
  },
  "mcpServers": {}
}
```

`settings.local.json` contains machine-specific paths — **add it to `.gitignore`**. Commit a `settings.json` with the non-secret structure if you want shared project defaults.

### `.claude/agents/` — Custom sub-agents

Define project-specific sub-agents for specialized tasks:

```markdown
---
name: codebase-reviewer
description: "Reviews C++ code changes against project standards. Use when reviewing a PR or before merging a feature branch."
---

# Codebase Reviewer

When reviewing code in this project:

1. Build clean: `make check` must pass with zero warnings
2. Coverage is still 100% (`make coverage`)
3. Sanitizer suite passes: `make asan` and `make tsan`
4. clang-tidy reports zero issues
5. Public API changes have a corresponding test in `tests/`
6. No use of raw `new` / `delete`, raw owning pointers, or C-style casts

Report: list of violations (if any), or "LGTM" with a one-line summary.
```

Add CLAUDE.md and agents to git; keep settings.local.json out:

```bash
echo ".claude/settings.local.json" >> .gitignore
git add .claude/CLAUDE.md .claude/agents/
git commit -m "chore: add per-project Claude configuration"
```

---

## Final folder structure

```
my_project/
├── .claude/
│   ├── CLAUDE.md                  # Instructions for Claude Code
│   ├── settings.local.json        # Permissions + MCPs (gitignored)
│   └── agents/
│       └── codebase-reviewer.md   # Custom sub-agent
├── include/
│   └── my_project/
│       └── my_project.hpp
├── src/
│   ├── CMakeLists.txt
│   └── my_project.cpp
├── tests/
│   ├── CMakeLists.txt
│   └── test_my_project.cpp
├── cmake/
│   └── ProjectWarnings.cmake
├── apps/                          # optional
├── benchmarks/                    # optional
├── examples/                      # optional
├── CMakeLists.txt
├── CMakePresets.json
├── .clang-format
├── .clang-tidy
├── .pre-commit-config.yaml
├── Makefile
└── .gitignore
```

---

## Tool summary

| Tool | Role | Configured in |
|------|------|---------------|
| `cmake` | Build system generator (single source of truth) | `CMakeLists.txt`, `CMakePresets.json` |
| `ninja` | Fast build tool used under cmake | (selected in `CMakePresets.json`) |
| `gcc` / `clang` | C++ compiler with strict warnings + `-Werror` | `cmake/ProjectWarnings.cmake` |
| `clang-format` | Formatter (replaces hand-tuned style) | `.clang-format` |
| `clang-tidy` | Static analyzer + modernizer | `.clang-tidy` |
| `Catch2` or `GoogleTest` | Unit test framework (ask user which) | `tests/CMakeLists.txt` (via FetchContent) |
| `vcpkg` or `Conan` | External library package manager (optional) | `vcpkg.json` / `conanfile.txt` + toolchain file |
| `ctest` | Test runner; integrates with Catch2 | `tests/CMakeLists.txt` |
| `gcovr` | Coverage with `--fail-under-line 100` enforcement | `Makefile` `coverage` target |
| AddressSanitizer / UBSan / TSan | Runtime UB / memory / race detection | `cmake/` options + `CMakePresets.json` |
| `pre-commit` | Blocks commits that fail format / tidy | `.pre-commit-config.yaml` |
| `Makefile` | Single entry point for all quality commands | `Makefile` |
| `.claude/` | Per-project Claude instructions, permissions, agents, MCPs | `.claude/CLAUDE.md`, `settings.local.json`, `agents/` |
