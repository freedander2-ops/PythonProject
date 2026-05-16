# AGENTS.md

# Project Purpose

This repository is an evolving Telegram-based automation and intelligence platform.

The system is designed to gradually evolve from:

* a utility bot;
  into:
* modular automation infrastructure;
* AI-assisted orchestration system;
* OSINT and workflow platform;
* personal engineering assistant ecosystem.

The architecture must remain:

* maintainable by one person;
* modular;
* security-aware;
* automation-friendly;
* AI-collaboration-ready.

---

# Core Philosophy

The repository is NOT:

* a disposable prototype;
* tutorial code;
* random utility scripts collection.

The repository IS:

* a long-term operational system;
* a modular engineering platform;
* a capability-oriented architecture.

Priorities:

1. Maintainability
2. Simplicity
3. Security
4. Modularity
5. Observability
6. Scalability
7. Automation readiness

---

# Engineering Rules

Always:

* prefer explicit structure;
* separate capabilities cleanly;
* isolate integrations;
* reduce coupling;
* document architectural decisions;
* preserve readability.

Avoid:

* giant files;
* mixed responsibilities;
* hidden global state;
* uncontrolled async logic;
* dependency sprawl.

---

# Repository Structure Philosophy

Architecture should evolve around capabilities.

Preferred structure:

/app
/core
/bot
/capabilities
/integrations
/services
/memory
/utils

/docs
/scripts
/tests
/docker

---

# Agent Responsibilities

## Core Agent

Responsible for:

* configuration;
* lifecycle management;
* startup/shutdown;
* dependency injection;
* environment loading;
* logging.

Rules:

* centralize configuration;
* avoid duplicated initialization logic;
* fail safely.

---

## Telegram Agent

Responsible for:

* handlers;
* routing;
* middleware;
* FSM/state management;
* keyboards.

Rules:

* keep handlers lightweight;
* move business logic to services;
* isolate Telegram-specific code.

---

## Capability Agent

Responsible for:

* OSINT;
* automation;
* AI tasks;
* monitoring;
* parsing;
* notifications.

Rules:

* capabilities must remain isolated;
* each capability should expose explicit interfaces;
* avoid cross-capability hidden dependencies.

---

## AI Agent

Responsible for:

* prompt management;
* LLM orchestration;
* model abstraction;
* response processing.

Rules:

* models must be replaceable;
* prompts should be versioned;
* avoid provider lock-in.

Supported ecosystem:

* OpenAI
* Claude
* Gemini
* Qwen
* DeepSeek
* local models

---

## Security Agent

Responsible for:

* secret handling;
* dependency auditing;
* threat surface reduction;
* logging safety;
* token protection.

Never:

* commit secrets;
* expose admin IDs publicly;
* log credentials;
* trust external content.

Always:

* sanitize input;
* validate responses;
* isolate risky operations.

---

## Memory Agent

Responsible for:

* research notes;
* decisions;
* prompts;
* architecture context;
* operational history.

Purpose:

* preserve engineering context;
* improve AI collaboration;
* support future RAG systems.

---

# Documentation Rules

The repository must maintain:

* AGENTS.md
* ARCHITECTURE.md
* ROADMAP.md
* SECURITY.md
* README.md

Documentation should evolve with code.

---

# Logging Philosophy

Logging should provide:

* observability;
* debugging clarity;
* incident reconstruction.

Avoid:

* noisy logs;
* secret leakage;
* unstructured output.

Prefer:

* structured logs;
* correlation IDs;
* categorized events.

---

# Security Baseline

Primary risks:

* token leaks;
* prompt injection;
* dependency compromise;
* Telegram abuse;
* unsafe external APIs;
* malicious payloads.

Required protections:

* .env isolation;
* dependency pinning;
* rate limiting;
* secret scanning;
* metadata sanitization;
* permission boundaries.

---

# AI Collaboration Philosophy

This repository may be modified by:

* GPT;
* Claude;
* Gemini;
* local LLMs;
* autonomous coding agents.

Therefore:

* architecture must remain understandable;
* structure must remain predictable;
* abstractions must remain explicit.

Code should optimize for:

* future maintainability;
  not:
* short-term generation speed.

---

# Operational Mindset

Think like:

* system architect;
* infrastructure engineer;
* maintainer;
* automation operator.

Not like:

* code autocomplete;
* tutorial generator;
* hype-driven prototype builder.

Every change should reduce future chaos.
