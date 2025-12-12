# Agent Support Documentation

## Overview

This folder contains machine-parseable knowledge structures designed to support AI agent reasoning capabilities. These decision trees, validation rules, and workflow definitions enable Level 3-5 agent capabilities:

- **Level 3**: Configuration guidance with step-by-step workflows
- **Level 4**: Workflow execution with formalized procedures
- **Level 5**: Complex reasoning with decision trees and validation rules

## Contents

### Decision Trees

| File | Purpose | Nodes | Use Case |
|------|---------|-------|----------|
| `consolidation-method-decision.yaml` | Determine consolidation method (G/E/P/N) | 9 | "What method for 45% ownership?" |
| `elimination-code-selection.yaml` | Select elimination code (S###) | 15+ | "Which elimination for dividend?" |
| `currency-translation-decision.yaml` | Select translation rate type | 12 | "What rate for fixed assets?" |

### Step-by-Step Workflows

| File | Purpose | Steps | Use Case |
|------|---------|-------|----------|
| `workflow-add-subsidiary.yaml` | Add new company to consolidation | 8 | "How do I add a new subsidiary?" |
| `workflow-process-acquisition.yaml` | Record business combination | 10 | "How do I process an acquisition?" |
| `workflow-configure-ic-eliminations.yaml` | Set up IC elimination rules | 7 | "How do I configure IC eliminations?" |
| `workflow-year-end-close.yaml` | Complete annual consolidation | 12 | "What's the year-end close process?" |

### Parameter References

| File | Purpose | Procedures | Use Case |
|------|---------|------------|----------|
| `parameter-reference-consolidation.yaml` | Core consolidation procedures | 4 | "What parameters for P_CONSO_ELIM?" |
| `parameter-reference-eliminations.yaml` | Elimination procedures | 12 | "How to call S085 elimination?" |

### Validation Rules

| File | Purpose | Rules | Use Case |
|------|---------|-------|----------|
| `validation-rules.yaml` | Data validation and period close prerequisites | 21 | "What must be valid before closing?" |

**Validation Categories**:
- **Ownership Validation (OWN-001 to OWN-007)**: Percentage ranges, parent method, circular ownership
- **Balance Sheet Validation (BS-001 to BS-004)**: Assets=Liab+Equity, elimination balance, flow reconciliation
- **Intercompany Reconciliation (IC-001 to IC-004)**: IC pairs netting, partner validation
- **Period Close Prerequisites (PC-001 to PC-006)**: Complete consolidation, exchange rates, eliminations

### Error Handling Patterns

| File | Purpose | Content | Use Case |
|------|---------|---------|----------|
| `error-handling-patterns.yaml` | Error catalog, failure scenarios, debug patterns | 40+ error codes | "Why did elimination fail?" |

**Error Categories**:
- **Configuration Errors**: Missing accounts, flows, journal types
- **Lock Errors**: Consolidation locked, concurrent processing
- **Ownership Errors**: No parent, no shareholders, invalid percentages
- **Elimination Errors**: Prerequisites not met, missing configuration
- **Data Validation Errors**: Invalid account settings

**Recovery Procedures**:
- **FAIL-001**: Missing exchange rates recovery
- **FAIL-002**: Orphan companies resolution
- **FAIL-003**: Missing special account fix
- **FAIL-004**: Locked consolidation handling
- **FAIL-005**: Circular ownership debugging

### Agent Integration Patterns

| File | Purpose | Content | Use Case |
|------|---------|---------|----------|
| `agent-integration-patterns.yaml` | Orchestrate knowledge files | 5 sections | "How do files work together?" |

**Integration Sections**:
- **Request Classification**: Route questions to appropriate files (6 intent categories, 8 entity types)
- **Multi-File Orchestration**: 5 patterns for combining decision trees, workflows, and playbooks
- **Response Assembly**: 4 response templates with structured sections
- **Context Handoff**: Manage state across multi-step interactions
- **Fallback Strategies**: 5-level hierarchy when knowledge base lacks answer

**Orchestration Patterns**:
- **Decision-First**: Use decision tree, then execute appropriate workflow
- **Workflow-Driven**: Step-by-step execution invoking other files as needed
- **Playbook Orchestration**: Complex scenarios using playbook as master controller
- **Troubleshooting Cascade**: Systematic error diagnosis across files
- **Configuration Assembly**: Build configuration from multiple template sources

**Context Management**:
- Session context (ConsoID, company, period, expertise level)
- Workflow context (active workflow, current step, outputs)
- Playbook context (phase, checkpoints, decision results)
- Entity and error context for troubleshooting

### Agent Testing Framework

| File | Purpose | Content | Use Case |
|------|---------|---------|----------|
| `agent-testing-framework.yaml` | Validate agent knowledge base | 4 sections | "How do I verify agent outputs?" |

**Testing Sections**:
- **Test Case Library**: 25+ structured test scenarios for decision trees, workflows, and playbooks
- **Expected Outcomes**: 8 common questions with expected agent responses
- **Validation Queries**: 11 SQL queries to confirm correct execution
- **Edge Case Catalog**: 12 unusual scenarios with expected handling

**Test Coverage**:
- Decision Tree Tests: Method determination, elimination routing, currency translation
- Workflow Tests: Add subsidiary, process acquisition, year-end close
- Playbook Tests: Full acquisition scenario end-to-end
- Validation Categories: Ownership, Elimination, Balance Sheet, Configuration

**Edge Case Categories**:
- Ownership: Circular ownership, treasury shares, multiple paths, de facto control
- Elimination: Partial year, pre-acquisition dividends, negative NCI, method change
- Currency: Hyperinflation, multiple rate sources
- Configuration: Missing accounts, elimination order conflicts

### Business Scenario Playbooks

| File | Purpose | Playbooks | Use Case |
|------|---------|-----------|----------|
| `business-scenario-playbooks.yaml` | End-to-end business scenarios | 5 | "How do I process an acquisition?" |

**Available Playbooks**:
- **Acquisition Playbook**: Complete M&A process from due diligence through first consolidation (IFRS 3)
- **Disposal Playbook**: Deconsolidation with CTA recycling and gain/loss calculation (IFRS 10, IAS 21)
- **Ownership Change Playbook**: Step acquisitions, partial disposals, method changes (IFRS 3, IFRS 10)
- **Year-End Close Playbook**: Complete annual close with validation gates (5 phases)
- **New Entity Onboarding Playbook**: From entity creation through first data submission (6 phases)

**Playbook Features**:
- Entry decision tree references
- Phase-by-phase step sequences with SQL templates
- Validation checkpoints and prerequisites
- Error recovery paths with resolution guidance
- Success criteria for each phase
- Cross-references to workflows, decision trees, and configuration templates

### Configuration Templates

| File | Purpose | Content | Use Case |
|------|---------|---------|----------|
| `configuration-templates.yaml` | Standard configuration patterns | 4 sections | "How do I set up eliminations?" |

**Configuration Sections**:
- **Elimination Configuration (TS070S0/TS071S0)**: Header/detail patterns, system/user templates
- **Special Account Mapping (TS010C0/TS010C1)**: 20+ special account codes with mapping SQL
- **Exchange Rate Setup (TS017R0)**: Rate types (CC/AC/MC/CR/AR/MR/NR), load templates
- **POV Dimension Configuration (TS050G0/TS050G2)**: Dimension setup, required detail types

**Key Templates**:
- Standard elimination templates (S001, S020, S085, User)
- Special account mapping and verification queries
- Exchange rate loading and completeness checking
- Custom dimension creation with hierarchy support

### Knowledge Graph Visualization

| File | Purpose | Content | Use Case |
|------|---------|---------|----------|
| `knowledge-graph.yaml` | Visual relationship maps | 5 sections | "How do files relate to each other?" |

**Graph Sections**:
- **File Dependency Graph**: Which YAML files reference which other files (15 files mapped)
- **Concept Relationship Map**: How consolidation concepts connect across documents (4 clusters)
- **Procedure Call Graph**: Stored procedure dependencies and call chains (20+ procedures)
- **IFRS Standard Mapping**: Which documents cover which accounting standards (10 standards)
- **Table Usage Matrix**: Which database tables are used by which procedures/workflows (8 core tables)

**Concept Clusters**:
- Ownership Cluster: Ownership % → Control → Method → Minority Interest → Indirect Holdings
- Elimination Cluster: IC → Participation → Dividend → MI → Equity Method → User
- Currency Cluster: Rate Types → Translation Method → CTA → Hyperinflation
- Acquisition Cluster: Goodwill → NCI Measurement → Fair Value → Step Acquisition

**Key Visualizations**:
- ASCII file dependency graph showing all 15 files across 5 layers
- Dependency matrix (adjacency matrix format)
- Procedure call tree from P_CONSO_CALCULATE_BUNDLE_INTEGRATION
- IFRS coverage matrix by knowledge file
- Table usage matrix (Read/Write/ReadWrite)

### Example Conversation Transcripts

| File | Purpose | Content | Use Case |
|------|---------|---------|----------|
| `example-conversations.yaml` | Sample multi-turn agent conversations | 6 conversations | "How should agent responses look?" |

**Conversations Included**:
- **CONV-001**: Adding New Subsidiary (Decision-First pattern) - 6 turns
- **CONV-002**: Troubleshooting MI Elimination (Troubleshooting Cascade) - 8 turns
- **CONV-003**: Business Acquisition with Goodwill (Playbook Orchestration) - 10 turns
- **CONV-004**: Configuring IC Elimination (Configuration Assembly) - 6 turns
- **CONV-005**: Year-End Consolidation Close (Workflow-Driven) - 8 turns
- **CONV-006**: Quick Rate Type Decision (Decision Response) - 2 turns

**Demonstrated Techniques**:
- Intent classification at conversation start
- Context maintenance across turns (entity, workflow, error state)
- Checkpoint verification before proceeding
- SQL templates adapted to specific parameters
- Validation queries at each step
- Learning points summarized per conversation

**Metrics**:
- 40 total turns across 6 conversations
- 45+ SQL examples provided
- 25 validation queries demonstrated
- 12 checkpoints with verification

### Format Specification

All decision trees follow this YAML structure:

```yaml
decision_tree:
  name: "Human-readable name"
  version: "1.0"
  description: "What this tree decides"

  # Entry point
  root: "first_node_id"

  # Decision nodes
  nodes:
    node_id:
      type: "decision" | "result" | "input"
      question: "What to evaluate?"
      data_source: "table.column or procedure"
      branches:
        - condition: "expression"
          next: "next_node_id"
        - condition: "default"
          result: "outcome"

  # Final outcomes
  results:
    result_code:
      value: "G"
      description: "Global Integration"
      procedure: "P_CONSO_ELIM_*"
      documentation: "link-to-doc.md"
```

## Agent Usage Pattern

### 1. Load Decision Tree
```python
tree = load_yaml("consolidation-method-decision.yaml")
```

### 2. Gather Required Inputs
```python
inputs = {
    "control_percentage": 45,
    "is_joint_venture": False,
    "has_board_control": True
}
```

### 3. Traverse Tree
```python
current = tree["nodes"][tree["root"]]
while current["type"] != "result":
    condition = evaluate(current, inputs)
    current = tree["nodes"][next_node(condition)]
```

### 4. Return Result with Documentation
```python
result = {
    "method": "G",
    "rationale": ["De facto control via board majority"],
    "documentation": "consolidation-method-determination.md"
}
```

## Integration with Knowledge Base

These decision trees reference the documentation library:

```
11-agent-support/                    <- Decision trees (this folder)
  |
  +-- consolidation-method-decision.yaml
  |     +-- references: 02-consolidation-methods/
  |
  +-- elimination-code-selection.yaml
  |     +-- references: 04-elimination-entries/
  |
  +-- currency-translation-decision.yaml
        +-- references: 05-currency-translation/
```

## Validation Rules

Each decision tree includes embedded validation:

1. **Input Validation**: Required fields, data types, ranges
2. **Path Validation**: All branches lead to valid results
3. **Result Validation**: Each result has associated procedures

## Workflow Format Specification

All workflows follow this YAML structure:

```yaml
workflow:
  name: "Human-readable name"
  version: "1.0"
  description: "What this workflow accomplishes"

  # Before starting
  prerequisites:
    - id: "prereq_1"
      description: "Condition that must be true"
      check: "SQL or manual verification"

  required_inputs:
    - name: "input_name"
      type: "string | integer | decimal | enum | date"
      description: "What this input is for"

  # Sequential steps
  steps:
    - step: 1
      name: "Step name"
      description: "What this step does"
      actions:
        - action: "action_name"
          type: "query | execute | procedure | documentation"
          sql: "SQL to execute"
      validation:
        success_criteria: "What success looks like"
        verify_sql: "SQL to verify"
      checkpoint: true  # Pause for confirmation

  # After completion
  post_workflow:
    next_steps:
      - description: "What to do next"

  troubleshooting:
    - issue: "Common problem"
      causes: ["Cause 1", "Cause 2"]
      solution: "How to fix it"
```

### Prompt Templates Library

| File | Purpose | Content | Use Case |
|------|---------|---------|----------|
| `prompt-templates.yaml` | Optimized system prompts for agent personas | 5 personas | "How should the agent respond?" |

**Core System Prompt**:
- Foundation prompt included in all persona variations
- Covers 10 capabilities, 6 response principles, and context awareness rules
- References all 17 YAML knowledge files and 50+ markdown documents

**Available Personas**:
- **PERSONA-EXPERT**: Technical, concise responses for experienced professionals
  - Response style: Short with complete SQL and IFRS paragraph references
  - Files emphasized: REF-CONSO, REF-ELIM, DT-METHOD, DT-ELIM, RULES-VAL

- **PERSONA-GUIDE**: Step-by-step guidance for learning users
  - Response style: Detailed with explanations, numbered steps, checkpoints
  - Files emphasized: WF-ADDSUB, WF-ACQUIRE, WF-YEAREND, PB-SCENARIOS

- **PERSONA-VALIDATOR**: Verification and QA focus for audit roles
  - Response style: Structured tables with pass/fail status, severity indicators
  - Files emphasized: RULES-VAL, TEST-FRAMEWORK, RULES-ERROR, WF-YEAREND

- **PERSONA-TROUBLESHOOTER**: Error diagnosis for users with problems
  - Response style: Iterative diagnosis with diagnostic queries and follow-up questions
  - Files emphasized: RULES-ERROR, RULES-VAL, REF-ELIM, TEST-FRAMEWORK

- **PERSONA-CONFIGURATOR**: System setup for administrators
  - Response style: Complete SQL templates with all fields and verification
  - Files emphasized: TMPL-CONFIG, WF-ADDSUB, WF-ICELIM, RULES-VAL

**Context Injection Patterns**:
- Session context (ConsoID, Period, User Expertise, Active Workflow)
- Entity context (Company, Method, Ownership percentages, Parent)
- Workflow context (Current step, Completed steps, Outputs, Blockers)
- Error context (Code, Message, Affected entity, Diagnostics, Attempted fixes)

**Response Formatting Templates**:
- Decision Response: Answer → Rationale → IFRS Reference → Caveats → Verification
- Workflow Response: Overview → Prerequisites → Current Step → SQL → Checkpoint → Next
- Troubleshooting Response: Issue → Causes → Diagnostic → Resolution → Prevention
- Configuration Response: Overview → Fields → SQL Template → Dependencies → Verification
- Validation Response: Summary → Results Table → Details → SQL → Recommendations → Status

**Persona Selection Logic**:
- PS-001: User states expertise level (beginner→Guide, expert→Expert, auditor→Validator)
- PS-002: Question type detection ("how do I"→Guide, "what is"→Expert, "why isn't"→Troubleshooter)
- PS-003: Error reported → Switch to Troubleshooter
- PS-004: Pre-close context → Switch to Validator
- PS-005: Complex multi-step scenario → Use Guide

## Agent Integration Pattern

### Using Decision Trees + Workflows Together

```python
# 1. User asks: "Add a 45% owned company"

# 2. First, use decision tree to determine method
tree = load_yaml("consolidation-method-decision.yaml")
method_result = traverse_tree(tree, {"control_percentage": 45})
# Result: method = "E" (Equity Method)

# 3. Then, execute appropriate workflow
workflow = load_yaml("workflow-add-subsidiary.yaml")
for step in workflow["steps"]:
    execute_step(step, inputs)
    if step.get("checkpoint"):
        await user_confirmation()
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-02 | Initial decision trees: method, elimination, currency |
| 1.1 | 2024-12-02 | Added 4 step-by-step workflows for common tasks |
| 1.2 | 2024-12-02 | Added parameter references for 16 stored procedures |
| 1.3 | 2024-12-02 | Added validation rules (21 rules across 4 categories) |
| 1.4 | 2024-12-02 | Added error handling patterns (40+ codes, 5 failure scenarios) |
| 1.5 | 2024-12-02 | Added configuration templates (eliminations, accounts, rates, dimensions) |
| 1.6 | 2024-12-02 | Added business scenario playbooks (5 end-to-end orchestrations) |
| 1.7 | 2024-12-02 | Added agent testing framework (25+ tests, 12 edge cases, 11 validations) |
| 1.8 | 2024-12-02 | Added agent integration patterns (5 orchestration patterns, context management) |
| 1.9 | 2024-12-02 | Added knowledge graph visualization (5 relationship maps, 4 concept clusters) |
| 2.0 | 2024-12-02 | Added example conversation transcripts (6 conversations, 40 turns, all patterns) |
| 2.1 | 2024-12-02 | Added prompt templates library (5 personas, context injection, response formatting) |

---
*Agent Support Documentation | Financial Consolidation Knowledge Base v2.1*
