# PATH C: Technical Designer Agent/Skill
## Implementation Report & Roadmap

**Version**: 2.0
**Last Updated**: 2024-12-04
**Target Users**: Software Developers, Software Architects
**Status**: **P0 COMPLETE** - Knowledge base ready for implementation

---

## Executive Summary

This report provides the complete roadmap for building a Claude Code agent or skill that implements code for new or existing features and bugs. The agent will link the existing technical infrastructure with business requirements, ensuring implementations follow established patterns while maintaining alignment with financial consolidation theory.

### Implementation Status

| Priority | Artifact | Status |
|----------|----------|--------|
| **P0** | Code Pattern Library | ✅ **COMPLETE** |
| **P0** | Stored Procedure Templates | ✅ **COMPLETE** |
| **P0** | Handler Template Library | ✅ **COMPLETE** |
| P1 | Migration Script Templates | ⏭️ Covered in Code Pattern Library |
| P1 | Test Scenario Library | ⏭️ Covered in Code Pattern Library |

### Implemented Artifacts (2024-12-04)

| Artifact | Location | Content |
|----------|----------|---------|
| Code Pattern Library | `11-agent-support/code-pattern-library.yaml` | 12 patterns (handlers, SPs, jobs, DTOs, tests, scripts) |
| Stored Procedure Templates | `11-agent-support/stored-procedure-templates.yaml` | 8 templates (eliminations, calculations, views, helpers) |
| Handler Template Library | `11-agent-support/handler-template-library.yaml` | 10 templates (EF, legacy, jobs, imports, exports) |

---

## 1. Vision & Objectives

### 1.1 What We're Building

A Claude Code agent/skill that:
- **Designs** technical implementations with architecture guidance
- **Generates** code following project patterns and conventions
- **Maps** business requirements to technical components
- **Creates** database schemas, stored procedures, and migrations
- **Implements** API handlers following message broker patterns
- **Produces** tests with business validation context

### 1.2 Target User Scenarios

| User | Scenario | Agent Capability |
|------|----------|------------------|
| **Developer** | "Implement new elimination type S095" | Generate procedure, handler, tests following patterns |
| **Developer** | "Fix bug in minority interest calculation" | Trace issue, identify fix, generate patch with tests |
| **Architect** | "Design new IC matching feature" | Create architecture, identify components, plan implementation |
| **Architect** | "Migrate service X to Entity Framework" | Follow EF recipes, generate entities, create tests |
| **Developer** | "Add validation rule for ownership" | Generate rule, validation handler, error messages |
| **Architect** | "What pattern should I use for this?" | Recommend pattern based on similar implementations |

### 1.3 Success Criteria

- Generated code compiles and follows project conventions
- 90%+ pattern compliance with existing codebase
- Business logic correctly reflects consolidation theory
- Tests provide meaningful coverage of business scenarios

---

## 2. Existing Knowledge Base Assets

### 2.1 Technical Implementation Documentation

| Asset | Location | Use Case |
|-------|----------|----------|
| **Stored Procedures Catalog** | `07-database-implementation/stored-procedures-catalog.md` | Pattern reference for new procedures |
| **Data Tables Catalog** | `07-database-implementation/data-tables-catalog.md` | Schema reference, FK relationships |
| **Indexes Reference** | `07-database-implementation/indexes-reference.md` | Index patterns |
| **Consolidation Services** | `08-application-layer/consolidation-services.md` | Service patterns |
| **Job Scheduling** | `08-application-layer/job-scheduling-services.md` | Hangfire patterns |
| **Data Import Services** | `08-application-layer/data-import-services.md` | Import patterns |

### 2.2 API Documentation

| Asset | Location | Use Case |
|-------|----------|----------|
| **API Index** | `api-index.yaml` | Handler catalog, method signatures |
| **Endpoint Files** | `api-*-endpoints.yaml` (16 files) | Parameter specs, responses |
| **Architecture Diagrams** | `api-architecture-diagrams.yaml` | Data flow patterns |
| **Common Types** | `api-common-types.yaml` | Shared DTOs, enums |

### 2.3 Business Logic Documentation

| Asset | Location | Use Case |
|-------|----------|----------|
| **Elimination Entries** | `04-elimination-entries/` | Elimination code logic |
| **Core Calculations** | `03-core-calculations/` | Calculation formulas |
| **Consolidation Methods** | `02-consolidation-methods/` | Method-specific logic |
| **Quick Reference Card** | `20-appendices/quick-reference-card.md` | Codes, queries, patterns |

### 2.4 Project Standards (from CLAUDE.md)

| Standard | Reference | Use Case |
|----------|-----------|----------|
| **EF Migration Rules** | `docs/EF_Migration/LINQ_to_EF_MigrationRules.md` | EF patterns |
| **Message Handler Pattern** | `CLAUDE.md` (Architecture section) | Handler signatures |
| **Frontend Patterns** | `applying-frontend-patterns` skill | TypeScript/Knockout patterns |
| **Test Patterns** | `guiding-test-creation` skill | MonaTestFacade patterns |

---

## 3. Knowledge Base Gaps

### 3.1 Critical Gaps (Must Close for Effective Implementation)

| Gap | Impact | Effort | Priority | Status |
|-----|--------|--------|----------|--------|
| **Code Pattern Library** | Cannot generate consistent code | High | P0 | ✅ **COMPLETE** |
| **Stored Procedure Templates** | Cannot scaffold new procedures | Medium | P0 | ✅ **COMPLETE** |
| **Handler Template Library** | Cannot scaffold new handlers | Medium | P0 | ✅ **COMPLETE** |

#### 3.1.1 Code Pattern Library ✅ COMPLETE
**Location**: `11-agent-support/code-pattern-library.yaml`
**Content**: 12 extractable patterns with placeholders:
- EF Read Handler (Recipe 4)
- EF Write Handler with Transaction
- LINQ-to-SQL Legacy Handler (reference)
- Elimination Stored Procedure
- Calculation Stored Procedure
- Hangfire Background Job
- Request/Response DTO
- Consolidation Data DTO
- Service Test with MonaTestFacade
- Database Update Script
- Stored Procedure Migration Script
- Translation Key Insert

#### 3.1.2 Stored Procedure Templates ✅ COMPLETE
**Location**: `11-agent-support/stored-procedure-templates.yaml`
**Content**: 8 comprehensive templates:
- Standard Elimination Procedure (P_CONSO_ELIM_*)
- Intercompany Elimination Procedure (P_CONSO_ELIM_INTERCOMPANY_*)
- Calculation/Integration Procedure (P_CONSO_CALCULATE_*)
- View/Query Procedure (P_VIEW_*)
- Helper/Utility Procedure (P_CONSO_HELPER_*)
- Event Procedure (P_CONSO_EVENT_*)
- System Procedure (P_SYS_*)
- Matching Procedure (P_CONSO_MATCHING_*)

Includes: Error handling patterns, key tables, special account/flow functions, step numbers

#### 3.1.3 Handler Template Library ✅ COMPLETE
**Location**: `11-agent-support/handler-template-library.yaml`
**Content**: 10 complete handler templates:
- EF Read/List Handler (pagination, filtering, sorting)
- EF Read Single Entity Handler
- EF Write Handler (Create/Update with UpdateHelper)
- EF Delete Handler (with dependency check)
- Job Trigger Handler (Hangfire pattern)
- Stored Procedure Call Handler
- LINQ-to-SQL Legacy Handler (reference/migration)
- Consolidation Handler (integration, eliminations)
- Import Handler (3-phase file upload)
- Export Handler (file generation)

Includes: Handler signatures overview, validation methods reference (14 methods), registration patterns

### 3.2 Important Gaps (Should Close for Quality)

| Gap | Impact | Effort | Priority | Status |
|-----|--------|--------|----------|--------|
| **Migration Script Templates** | Manual script creation | Low | P1 | ⏭️ Covered in Code Pattern Library |
| **Test Scenario Library** | Limited test coverage | Medium | P1 | ⏭️ Covered in Code Pattern Library |
| **Error Message Catalog** | Inconsistent error handling | Low | P1 | ⏭️ Covered in api-error-catalog.yaml |

#### 3.2.1 Migration Script Templates - COVERED
**Status**: Already included in `code-pattern-library.yaml` (Patterns 10, 11, 12)
- Pattern 10: `update_script` - Database Update Script with $$REVISION syntax
- Pattern 11: `stored_procedure_script` - Stored Procedure Migration Script
- Pattern 12: `translation_insert` - Translation Key Insert with all 14 language codes

#### 3.2.2 Test Scenario Library - COVERED
**Status**: Already included in `code-pattern-library.yaml` (Pattern 9)
- Pattern 9: `service_test` - Service Test with MonaTestFacade
- Test naming convention (T### format)
- Test numbering ranges (T10-T59)
- Permission and validation test examples

### 3.3 Nice-to-Have Gaps (Enhance Implementation Quality)

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| **Performance Patterns** | May miss optimization opportunities | Medium | P2 |
| **Security Patterns** | May miss security considerations | Medium | P2 |
| **Logging Patterns** | Inconsistent logging | Low | P2 |

---

## 4. Implementation Roadmap

### Phase 1: Code Generation Foundation (Weeks 1-2)

#### 4.1.1 Agent Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Implementation Request                    │
│        (Feature/Bug description + requirements)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Design Orchestrator                       │
│  - Requirement parsing                                       │
│  - Architecture planning                                     │
│  - Component identification                                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ Business Mapper   │ │ Pattern Matcher   │ │ Code Generator    │
│ - Theory lookup   │ │ - Similar code    │ │ - Templates       │
│ - Logic extract   │ │ - Pattern select  │ │ - Scaffolding     │
│ - Validation req  │ │ - Convention chk  │ │ - Integration     │
└───────────────────┘ └───────────────────┘ └───────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Base                            │
│  - Code patterns & templates                                 │
│  - Existing codebase reference                               │
│  - Business logic documentation                              │
└─────────────────────────────────────────────────────────────┘
```

#### 4.1.2 Deliverables
- [ ] Pattern library connector
- [ ] Template engine
- [ ] Code scaffolding framework
- [ ] Codebase pattern analyzer

### Phase 2: Database Layer Generation (Weeks 3-4)

#### 4.2.1 Database Generation Capabilities

| Capability | Implementation |
|------------|----------------|
| **Stored Procedure Generation** | Template-based with business logic injection |
| **Table Schema Generation** | Following TS*/TD* conventions |
| **Index Generation** | Based on query patterns |
| **Migration Script Generation** | UpdateScript format with versioning |

#### 4.2.2 Stored Procedure Patterns

```sql
-- ELIMINATION PROCEDURE TEMPLATE
CREATE PROCEDURE [dbo].[P_CONSO_ELIM_{ELIMINATION_NAME}]
    @ConsoID INT,
    @CompanyIDs NVARCHAR(MAX) = NULL,
    @errorinfo NVARCHAR(MAX) = '' OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- 1. Initialize
        DECLARE @ElimCode NVARCHAR(10) = '{ELIM_CODE}';
        DECLARE @JournalTypeID INT;

        SELECT @JournalTypeID = JournalTypeID
        FROM TS020S0 WHERE ConsoID = @ConsoID AND JournalTypeCode = @ElimCode;

        -- 2. Delete existing journals for this elimination
        DELETE FROM TD045C2
        WHERE ConsoID = @ConsoID
          AND JournalTypeID = @JournalTypeID
          AND ({COMPANY_FILTER});

        -- 3. Calculate elimination amounts
        {CALCULATION_LOGIC}

        -- 4. Create elimination journals
        INSERT INTO TD045C2 (ConsoID, JournalTypeID, CompanyID, AccountID,
                             FlowID, Amount, DebitCredit)
        {INSERT_SELECT}

    END TRY
    BEGIN CATCH
        SET @errorinfo = ERROR_MESSAGE();
    END CATCH
END
```

#### 4.2.3 Deliverables
- [ ] Stored procedure generator
- [ ] Table schema generator
- [ ] Index recommendation engine
- [ ] Migration script generator

### Phase 3: Service Layer Generation (Weeks 5-6)

#### 4.3.1 Service Layer Capabilities

| Capability | Implementation |
|------------|----------------|
| **Message Handler Generation** | EF pattern (Recipe 4) |
| **DTO Generation** | Request/Response with validation |
| **Service Method Generation** | Business logic wrapper |
| **Job Generation** | Hangfire background job |

#### 4.3.2 Handler Pattern (EF - Recipe 4)

```csharp
// EF MESSAGE HANDLER TEMPLATE
internal static async Task {HandlerName}(
    SessionController helper,
    EF.MonaDbContext db,
    MessageValidationHelper validation,
    IDictionary<string, object> responseMessage,
    bool debug)
{
    // 1. Parse and validate request
    var request = helper.GetRequestValue<{RequestDTO}>(nameof({HandlerName}));

    validation
        .Required(request.ConsoID, nameof(request.ConsoID))
        {ADDITIONAL_VALIDATIONS};

    if (validation.HasErrors)
    {
        responseMessage["errors"] = validation.Errors;
        return;
    }

    // 2. Business logic
    {BUSINESS_LOGIC}

    // 3. Data access
    var result = await db.{EntitySet}
        .Where(x => x.ConsoID == request.ConsoID)
        {QUERY_LOGIC}
        .ToListAsync();

    // 4. Map to response
    var response = result.Select(x => new {ResponseDTO}
    {
        {PROPERTY_MAPPINGS}
    });

    responseMessage["{handler_name}"] = response;
}
```

#### 4.3.3 Deliverables
- [ ] Handler code generator
- [ ] DTO generator
- [ ] Service method generator
- [ ] Job scaffolding generator

### Phase 4: Test Generation (Weeks 7-8)

#### 4.4.1 Test Generation Capabilities

| Capability | Implementation |
|------------|----------------|
| **Unit Test Generation** | MonaTestFacade pattern |
| **Integration Test Generation** | Database + handler tests |
| **Scenario-Based Tests** | Business scenario coverage |
| **Edge Case Detection** | Automatic edge case identification |

#### 4.4.2 Test Pattern (MonaTestFacade)

```csharp
// TEST CLASS TEMPLATE
[TestClass]
public class {FeatureName}ServiceTests : MonaTestBase
{
    [TestMethod]
    public async Task T001_{TestScenario}_ShouldSucceed()
    {
        // Arrange
        using var facade = new MonaTestFacade();
        var consoId = facade.CreateTestConsolidation();
        {ARRANGE_LOGIC}

        // Act
        var result = await facade.ExecuteHandler<{ResponseDTO}>(
            "{HandlerName}",
            new {RequestDTO}
            {
                ConsoID = consoId,
                {REQUEST_PROPERTIES}
            });

        // Assert
        Assert.IsFalse(facade.Helper.LogHelper.HasErrors,
            facade.Helper.LogHelper.GetErrorMessage());
        {ASSERTIONS}
    }

    [TestMethod]
    public async Task T002_{EdgeCase}_ShouldHandleGracefully()
    {
        // Arrange
        using var facade = new MonaTestFacade();
        {EDGE_CASE_ARRANGE}

        // Act
        var result = await facade.ExecuteHandler<{ResponseDTO}>(
            "{HandlerName}",
            {EDGE_CASE_REQUEST});

        // Assert
        {EDGE_CASE_ASSERTIONS}
    }
}
```

#### 4.4.3 Deliverables
- [ ] Unit test generator
- [ ] Integration test generator
- [ ] Edge case detector
- [ ] Test data generator

### Phase 5: Architecture Guidance (Weeks 9-10)

#### 4.5.1 Architecture Capabilities

| Capability | Implementation |
|------------|----------------|
| **Pattern Recommendation** | Analyze requirement, suggest pattern |
| **Component Planning** | Identify all needed components |
| **Dependency Analysis** | Map dependencies, suggest order |
| **Review & Validation** | Check implementation against patterns |

#### 4.5.2 Implementation Planning Template

```markdown
# Implementation Plan: {Feature Name}

## Architecture Overview
- Pattern: {recommended pattern}
- Components: {component list}
- Dependencies: {dependency list}

## Implementation Steps

### Step 1: Database Layer
- [ ] Create stored procedure: P_CONSO_{NAME}
- [ ] Add table columns (if needed): {columns}
- [ ] Create indexes: {indexes}
- [ ] Migration script: UpdateScript-V{version}.sql

### Step 2: Service Layer
- [ ] Create handler: {HandlerName}Service.cs
- [ ] Create DTOs: {Request/Response}DTO.cs
- [ ] Register handler: MessagesBroker/Util.cs
- [ ] Add to api-{category}-endpoints.yaml

### Step 3: Business Logic
- [ ] Implement calculation: {method name}
- [ ] Add validation rules: {validation list}
- [ ] Error handling: {error codes}

### Step 4: Testing
- [ ] Unit tests: {test class}
- [ ] Integration tests: {test scenarios}
- [ ] Manual test plan: {test cases}

### Step 5: Documentation
- [ ] Update theory document: {document}
- [ ] Update API documentation: {yaml file}
- [ ] Update cross-reference: {entries}

## Verification Checklist
- [ ] Code compiles without warnings
- [ ] All tests pass
- [ ] Pattern compliance verified
- [ ] Business logic matches theory
- [ ] Documentation updated
```

#### 4.5.3 Deliverables
- [ ] Pattern recommendation engine
- [ ] Implementation planner
- [ ] Dependency mapper
- [ ] Review assistant

---

## 5. Claude Code Integration

### 5.1 Skill Implementation

```markdown
# Technical Designer Skill

## Skill Trigger
When user mentions:
- "implement feature X"
- "design solution for Y"
- "create stored procedure for Z"
- "generate handler for A"
- "scaffold tests for B"

## Skill Flow
1. Parse implementation request
2. Analyze business requirements (theory lookup)
3. Match to existing patterns
4. Generate implementation plan
5. Scaffold code components
6. Generate tests
7. Provide integration guidance

## Skill Output
- Implementation plan
- Generated code files
- Test scaffolding
- Documentation updates
```

### 5.2 Agent Implementation

```markdown
# Technical Designer Agent

## Agent Capabilities
- Full feature implementation (multi-file)
- Architecture design sessions
- Code review with pattern validation
- Refactoring with business context

## Agent Mode
Use fc-developer agent for step-by-step implementation
Use fc-implementation-planner for architecture planning
```

### 5.3 Integration with Existing Skills/Agents

| Existing | Integration Point |
|----------|-------------------|
| `fc-implementation-planner` | Architecture planning |
| `fc-developer` | Step-by-step implementation |
| `fc-code-reviewer` | Pattern compliance validation |
| `fc-test-implementer` | Test generation |
| `fc-database` | Database migration |
| `linq-to-ef-migrator` | EF migration |
| `guiding-test-creation` | Test patterns |

---

## 6. Pattern Reference

### 6.1 Elimination Code Implementation Pattern

```
When implementing new elimination type (S0XX):

1. DATABASE LAYER
   - Create P_CONSO_ELIM_{NAME}
   - Add to P_CONSO_ELIM dispatcher (IF block)
   - Add journal type to TS020S0

2. CONFIGURATION
   - Add elimination to TS070S0
   - Configure account mappings in TS071S0
   - Set execution Level (order)

3. SERVICE LAYER
   - Handler already exists: Consolidation_Execute
   - Results via: Elimination_GetEliminations

4. THEORY ALIGNMENT
   - Reference: 04-elimination-entries/
   - Validate: Calculation matches theory
   - Document: Add to elimination-code-catalog

5. TESTING
   - Setup: Create test companies with ownership
   - Input: Prepare elimination source data
   - Execute: Run consolidation with Elims flag
   - Verify: Check TD045C2 journals
```

### 6.2 Calculation Implementation Pattern

```
When implementing new calculation:

1. IDENTIFY THEORY
   - Source: 03-core-calculations/ or direct_consolidation_chunks/
   - Formula: Extract mathematical formula
   - Inputs: Identify required data sources
   - Outputs: Identify result tables

2. DATABASE LAYER
   - Create P_CALC_{NAME} or add to existing P_CALC_*
   - Input tables: TD030B2, TS014C0, etc.
   - Output: TD035C2 or calculation-specific table

3. INTEGRATION
   - Trigger: From P_CONSO_CALCULATE_* or standalone
   - Parameters: @ConsoID, @CompanyIDs, @errorinfo

4. TESTING
   - Known value tests: Use examples from theory
   - Edge cases: Zero values, missing data, circular refs
```

### 6.3 API Handler Implementation Pattern

```
When implementing new API handler:

1. DETERMINE TYPE
   - Read-only query → GET pattern
   - Create/Update → POST/PUT pattern
   - Long-running → Job pattern
   - File operation → Import/Export pattern

2. CREATE DTOs
   - Request DTO with validation attributes
   - Response DTO matching frontend needs

3. IMPLEMENT HANDLER
   - Use EF pattern (Recipe 4) for new code
   - Follow validation pattern (MessageValidationHelper)
   - Use async/await throughout

4. REGISTER
   - Add to MessagesBroker routing
   - Document in api-{category}-endpoints.yaml

5. TEST
   - Unit test: Handler logic
   - Integration test: Full request/response cycle
```

---

## 7. Success Metrics

### 7.1 Code Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Compilation Success | 100% | Build verification |
| Pattern Compliance | 90%+ | Code review |
| Test Coverage | 80%+ | Coverage tools |
| Documentation Sync | 100% | Review checklist |

### 7.2 Efficiency Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Scaffolding Time | < 5 minutes | Timing |
| Manual Code Reduction | 70%+ | Line count comparison |
| Rework Rate | < 10% | Issue tracking |

### 7.3 Business Alignment Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Theory Accuracy | 95%+ | Expert review |
| Calculation Correctness | 100% | Test validation |
| Requirement Fulfillment | 95%+ | Acceptance testing |

---

## 8. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Generated code doesn't compile | High | Low | Template validation, build checks |
| Pattern drift from codebase | Medium | Medium | Regular pattern library updates |
| Business logic errors | High | Medium | Theory validation, expert review |
| Over-reliance on generation | Medium | Medium | Review requirements, edge case focus |

---

## 9. Next Steps

### ✅ Completed (2024-12-04)
1. ~~Close P0 gap: Create Code Pattern Library~~ → `code-pattern-library.yaml`
2. ~~Extract templates from existing codebase~~ → 12 patterns extracted
3. ~~Create stored procedure templates~~ → `stored-procedure-templates.yaml` (8 templates)
4. ~~Create handler template library~~ → `handler-template-library.yaml` (10 templates)

### Optional Future Enhancements
1. Create Claude Code agent definition (`.claude/agents/fc-technical-designer.md`)
2. Create skill definition (`.claude/skills/designing-technical-implementations/SKILL.md`)
3. Integrate with existing workflow orchestration

### Knowledge Base Ready
The PATH C knowledge base is now complete with:
- **30 total templates** across 3 YAML files
- **Extractable patterns** with placeholders for code generation
- **Real codebase references** from actual implementation files
- **Cross-references** to related documentation

---

## Appendix A: Template Placeholders Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{ELIMINATION_NAME}` | Elimination type name | `MINORITYINTEREST` |
| `{ELIM_CODE}` | Elimination code | `S085` |
| `{CALCULATION_LOGIC}` | Business calculation SQL | `SELECT ... GROUP BY ...` |
| `{HandlerName}` | Handler method name | `Elimination_GetEliminations` |
| `{RequestDTO}` | Request DTO class | `GetEliminationsRequest` |
| `{ResponseDTO}` | Response DTO class | `EliminationDTO` |
| `{BUSINESS_LOGIC}` | C# business logic | `var amounts = Calculate(...)` |

## Appendix B: Existing Pattern Sources

| Pattern | Source File | Notes |
|---------|-------------|-------|
| EF Handler | `CompanyService.cs` | Recipe 4 reference |
| Elimination SP | `P_CONSO_ELIM_MINORITYINTEREST.sql` | Standard pattern |
| Integration SP | `P_CONSO_CALCULATE_BUNDLE_INTEGRATION.sql` | Calculation pattern |
| Test Class | `CompanyServiceTests.cs` | MonaTestFacade usage |
| DTO | `CompanyDTO.cs` | Standard structure |

---

*Report Version: 2.0 | Updated: 2024-12-04 | Path: C - Technical Designer Agent/Skill | Status: P0 COMPLETE*
