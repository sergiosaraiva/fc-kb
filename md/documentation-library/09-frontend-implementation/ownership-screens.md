# Ownership Screens: Frontend Implementation

## Document Metadata
- **Category**: Frontend Implementation
- **Theory Source**: Implementation-specific (Knockout.js MVVM pattern)
- **Implementation Files**:
  - `Sigma.Mona.WebApplication/Screens/Ownership/Ownership.ts` - TypeScript ViewModel
  - `Sigma.Mona.WebApplication/Screens/Ownership/Ownership.cshtml` - Razor View
  - `Sigma.Mona.WebApplication/Screens/Ownership/OwnershipController.cs` - MVC Controller
  - `Sigma.Mona.WebApplication/Screens/Ownership/OwnershipService.cs` - Backend Service
  - `Sigma.Database/dbo/Stored Procedures/P_VIEW_OWNERSHIP.sql` - Data retrieval
  - `Sigma.Database/dbo/Stored Procedures/P_VIEW_OWNERSHIP_DETAIL.sql` - Detail retrieval
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full screen implementation documented)
- **Compliance Status**: Frontend architecture reference

## Executive Summary

The Ownership screen in Prophix.Conso provides an interface for viewing and editing company ownership structures. It displays shareholders (who owns the company) and participations (what the company owns) with both financial rights and voting rights tracked separately. The implementation follows the project's standard **TypeScript/Knockout.js MVVM pattern** with service-based backend communication.

## Architecture Overview

### Component Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ownership Screen                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Company Selection (Dropdown/Grid)                       │    │
│  │  - CompanyCode, CompanyName                              │    │
│  │  - GroupPerc, MinorPerc, GroupCtrlPerc                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────┐     ┌─────────────────────┐           │
│  │   Shareholders      │     │   Participations    │           │
│  │   (Who owns this)   │     │   (What this owns)  │           │
│  │                     │     │                     │           │
│  │   - FinAmount       │     │   - FinAmount       │           │
│  │   - FinPercent      │     │   - FinPercent      │           │
│  │   - VotingAmount    │     │   - VotingAmount    │           │
│  │   - ControlPercent  │     │   - ControlPercent  │           │
│  └─────────────────────┘     └─────────────────────┘           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Calculate Indirect Percentages (Action)                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ownership.cshtml (View)                       │
│   - Knockout.js bindings                                         │
│   - DevExpress grids                                             │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ data-bind
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ownership.ts (ViewModel)                      │
│   - Observable properties                                        │
│   - Service communication                                        │
│   - UI logic                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Message Broker
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OwnershipService.cs (Service)                 │
│   - Message handlers                                             │
│   - Business logic                                               │
│   - Database calls                                               │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Stored Procedure
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    P_VIEW_OWNERSHIP*.sql                         │
│   - Data retrieval                                               │
│   - Percentage calculation                                       │
└─────────────────────────────────────────────────────────────────┘
```

## TypeScript Implementation

### Service Interface (Ownership.ts)

```typescript
export namespace OwnershipService {
    // Message handlers
    export const handlerGetOwnership = "Ownership_GetOwnership";
    export const handlerSaveOwnership = "Ownership_SaveOwnership";
    export const handlerLaunchCalculateIndirectPercentagesJob =
        "Ownership_LaunchCalculateIndirectPercentagesJob";

    // Data structures
    export interface OwnerShipDetail {
        OtherCompanyID: number;
        OtherCompanyCode: string;
        OtherCompanyName: string;
        CurFinAmount?: number;
        RefFinAmount?: number;
        CurFinPercent?: number;
        RefFinPercent?: number;
        CurVotingAmount?: number;
        RefVotingAmount?: number;
        CurControlPercent?: number;
        RefControlPercent?: number;
        CompanyFinRightsIssued?: number;
        CompanyVotingRightsIssued?: number;
        hasChanged: boolean;
    }

    export interface OwnershipItem extends BaseItem {
        CompanyID: number;
        CompanyCode: string;
        CompanyName: string;
        IsParentCompany: string;
        OwnershipFinancialRights: number;
        OwnershipVotingRights: number;
        GroupPerc: string;
        MinorPerc: string;
        GroupCtrlPerc: string;
        Shareholders: OwnerShipDetail[];
        Participations: OwnerShipDetail[];
        EntityVersion: EntityVersion[];
    }
}
```

### Observable ViewModel Pattern

```typescript
export interface OwnerShipDetailObservable {
    OtherCompanyID: KnockoutObservable<number>;
    OtherCompanyCode: KnockoutObservable<string>;
    OtherCompanyName: KnockoutObservable<string>;
    CurFinAmount?: KnockoutObservable<number>;
    RefFinAmount?: KnockoutObservable<number>;
    CurFinPercent?: KnockoutObservable<any>;
    RefFinPercent?: KnockoutObservable<number>;
    CurVotingAmount?: KnockoutObservable<number>;
    RefVotingAmount?: KnockoutObservable<number>;
    CurControlPercent?: KnockoutObservable<any>;
    RefControlPercent?: KnockoutObservable<number>;
    hasChanged: KnockoutObservable<boolean>;
}

export interface OwnershipItemObservable {
    Shareholders: KnockoutObservableArray<OwnerShipDetailObservable>;
    Participations: KnockoutObservableArray<OwnerShipDetailObservable>;
    OwnershipFinancialRights: KnockoutObservable<number>;
    OwnershipVotingRights: KnockoutObservable<number>;
    CompanyID: KnockoutObservable<number>;
    CompanyCode: KnockoutObservable<string>;
    CompanyName: KnockoutObservable<string>;
    GroupPerc: KnockoutObservable<string>;
    MinorPerc: KnockoutObservable<string>;
    GroupCtrlPerc: KnockoutObservable<string>;
}
```

## Backend Service Implementation

### OwnershipService.cs DTOs

```csharp
public class OwnerShipDetailDTO
{
    public int OtherCompanyID { get; set; }
    public string OtherCompanyCode { get; set; }
    public string OtherCompanyName { get; set; }
    public long? CurFinAmount { get; set; }
    public long? RefFinAmount { get; set; }
    public decimal? CurFinPercent { get; set; }
    public decimal? RefFinPercent { get; set; }
    public long? CurVotingAmount { get; set; }
    public long? RefVotingAmount { get; set; }
    public decimal? CurControlPercent { get; set; }
    public decimal? RefControlPercent { get; set; }
    public long? CompanyFinRightsIssued { get; set; }
    public long? CompanyVotingRightsIssued { get; set; }
}

public class OwnerShipDTO
{
    public int CompanyID { get; set; }
    public string CompanyCode { get; set; }
    public string CompanyName { get; set; }
    public bool IsParentCompany { get; set; }
    public long? OwnershipFinancialRights { get; set; }
    public long? OwnershipVotingRights { get; set; }
    public decimal? GroupPerc { get; set; }
    public decimal? MinorPerc { get; set; }
    public decimal? GroupCtrlPerc { get; set; }
    public List<OwnerShipDetailDTO> Shareholders { get; set; }
    public List<OwnerShipDetailDTO> Participations { get; set; }
    public EntityVersion[] EntityVersion { get; set; }
}
```

### Message Handler Pattern

```csharp
internal static void GetOwnership(SessionController helper,
    Message requestMessage, Message responseMessage)
{
    using var db = DAOFactory.CreateDataContext();

    // Access control
    helper.EnsureAccessRight(db, UserActions.Ownership_GetOwnership);

    // Parameter validation
    var validation = new MessageValidationHelper(
        logHelper: helper.LogHelper,
        messageItem: requestMessage);

    var companyId = validation.ValidateID("CompanyId", required: true);
    if (helper.LogHelper.HasErrors) goto EXIT;

    var consoID = helper.WorkingConsoID;
    var refConsoID = helper.RefWorkingConsoID;

    // Data retrieval via stored procedure
    var shareholders = db.P_VIEW_OWNERSHIP_DETAIL(
        consoID, refConsoID, companyId, 'S', helper.UserCustomerID)
        .Select(x => MapToDTO(x)).ToList();

    var participations = db.P_VIEW_OWNERSHIP_DETAIL(
        consoID, refConsoID, companyId, 'P', helper.UserCustomerID)
        .Select(x => MapToDTO(x)).ToList();

    // Response construction
    responseMessage["scf_items"] = new OwnerShipDTO
    {
        CompanyID = companyId.Value,
        Shareholders = shareholders,
        Participations = participations,
        // ... other properties
    };

EXIT:
    helper.LogHelper.AddLogResults(responseMessage);
}
```

## Data Flow

### Get Ownership Request

```
1. User selects company in UI
   │
   ▼
2. Ownership.ts calls service
   OwnershipService.handlerGetOwnership
   { CompanyId: selectedId }
   │
   ▼
3. Message Broker routes to handler
   OwnershipService.GetOwnership()
   │
   ▼
4. Stored procedure called
   P_VIEW_OWNERSHIP_DETAIL(consoID, refConsoID, companyId, 'S')
   P_VIEW_OWNERSHIP_DETAIL(consoID, refConsoID, companyId, 'P')
   │
   ▼
5. Response sent to client
   { scf_items: OwnerShipDTO }
   │
   ▼
6. TypeScript maps to observables
   Knockout updates UI bindings
```

### Save Ownership Request

```
1. User edits ownership amounts
   │
   ▼
2. hasChanged flags set on modified rows
   │
   ▼
3. Save triggered
   OwnershipService.handlerSaveOwnership
   { changes: modifiedDetails[] }
   │
   ▼
4. Backend validation
   - Validate percentages
   - Check total <= issued rights
   │
   ▼
5. Update TS015S0
   - NbrFinRights
   - NbrVotingRights
   │
   ▼
6. Trigger recalculation job (optional)
   P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES
```

## Key UI Features

### Financial vs Voting Rights Display

```
┌─────────────────────────────────────────────────────────────────┐
│  Shareholders of Company ABC                                     │
├───────────────┬───────────────────┬───────────────────┬─────────┤
│ Company       │ Financial         │ Voting            │ Change  │
│               │ Amount │ Percent  │ Amount │ Percent  │         │
├───────────────┼────────┼──────────┼────────┼──────────┼─────────┤
│ Parent Corp   │ 800    │ 80.00%   │ 900    │ 90.00%   │   [ ]   │
│ Investor Ltd  │ 150    │ 15.00%   │ 100    │ 10.00%   │   [ ]   │
│ Treasury      │  50    │  5.00%   │   0    │  0.00%   │   [ ]   │
├───────────────┼────────┼──────────┼────────┼──────────┼─────────┤
│ TOTAL         │ 1000   │ 100.00%  │ 1000   │ 100.00%  │         │
└───────────────┴────────┴──────────┴────────┴──────────┴─────────┘
```

### Reference Period Comparison

The UI displays both current and reference period values:
- `CurFinAmount` / `RefFinAmount`
- `CurFinPercent` / `RefFinPercent`
- `CurVotingAmount` / `RefVotingAmount`
- `CurControlPercent` / `RefControlPercent`

### Calculate Indirect Percentages

Button triggers background job:
```typescript
export const handlerLaunchCalculateIndirectPercentagesJob =
    "Ownership_LaunchCalculateIndirectPercentagesJob";

// Calls P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES
// Updates GroupPerc, MinorPerc, GroupCtrlPerc
// Handles circular ownership via matrix algebra
```

## Entity Locking

### Shared Lock Pattern

```csharp
using (var updateHelper = includeEntities
    ? new EntityUpdateHelper(helper, LockingModes.Shared, db)
    : null)
{
    if (includeEntities && companyId.HasValue)
    {
        updateHelper.LockEntity(
            EntityTypes.Company,
            CompanyService.GetEntityKey(consoID, companyId.Value));
    }
    // ... data retrieval
}
```

### EntityVersion Tracking

```csharp
public class OwnerShipDTO
{
    // ... other properties
    public EntityVersion[] EntityVersion { get; set; }
}

// Client sends EntityVersion with save
// Server validates version hasn't changed
// Prevents concurrent modification conflicts
```

## Related Documentation

- [Consolidation Screens](consolidation-screens.md) - Related screen patterns
- [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) - Business logic
- [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md) - Control calculation
- [Direct and Indirect Holdings](../06-ownership-structure/direct-indirect-holdings.md) - Ownership chains

---
*Document 38 of 50+ | Batch 13: Application Services & Frontend Implementation | Last Updated: 2024-12-01*
