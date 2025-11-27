# Module Documentation - Data Factory to Microsoft Fabric Migration Assistant

This document provides comprehensive documentation for all modules in the **Data Factory to Microsoft Fabric Migration Assistant** application.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Services](#services)
- [Components](#components)
- [Contexts](#contexts)
- [Hooks](#hooks)
- [Types](#types)
- [Library Utilities](#library-utilities)
- [Validation](#validation)
- [Module Relationships](#module-relationships)

---

## Overview

The application is built using a modern React architecture with TypeScript, following a modular design pattern that separates concerns into distinct layers:

- **Services Layer**: Business logic and API integrations
- **Components Layer**: UI components and pages
- **Contexts Layer**: Global state management
- **Hooks Layer**: Reusable stateful logic
- **Types Layer**: TypeScript type definitions
- **Library Layer**: Utility functions and configurations

---

## Architecture

```
src/
├── services/           # Business logic (40+ services)
├── components/         # React components
│   ├── pages/         # Wizard step pages (11 pages)
│   ├── ui/            # Reusable UI components (50+ components)
│   ├── profiling/     # Profiling-related components
│   └── debug/         # Debug and diagnostic components
├── contexts/          # React Context providers
├── hooks/             # Custom React hooks
├── types/             # TypeScript definitions
├── lib/               # Utility functions
├── utils/             # Graph optimization utilities
├── validation/        # Validation test utilities
├── examples/          # Example ARM templates
└── test/              # Test utilities
```

---

## Services

The services layer contains all business logic modules. Each service is responsible for a specific domain of functionality.

### Authentication Services

#### `authService.ts`
**Purpose**: Handles Azure AD authentication using MSAL (Microsoft Authentication Library).

**Key Features**:
- OAuth 2.0 authentication with PKCE flow
- Service principal authentication support
- Tenant-specific MSAL instance management
- Token refresh and validation
- Workspace access validation

**Key Methods**:
- `loginWithMicrosoft(config)` - Interactive login with Microsoft account
- `loginWithServicePrincipal(credentials)` - Service principal authentication
- `refreshToken(currentToken)` - Refresh expired tokens
- `logout()` - Clear authentication state
- `validateWorkspaceAccess(token, workspaceId)` - Validate permissions

---

### Parser Services

#### `adfParserService.ts`
**Purpose**: Parses Azure Data Factory (ADF) and Synapse Analytics ARM templates.

**Key Features**:
- ARM template JSON parsing and validation
- Component extraction (pipelines, datasets, linked services, triggers)
- Activity parsing with dependency analysis
- Global parameter detection
- Parameterized LinkedService detection
- Profile generation with metrics and insights
- Dependency graph building

**Key Methods**:
- `parseARMTemplate(fileContent)` - Main entry point for parsing
- `generateProfile(components, fileName, fileSize)` - Generate comprehensive profile
- `getDatasetByName(name)` - Retrieve dataset by name
- `getLinkedServiceByName(name)` - Retrieve LinkedService by name
- `getCopyActivityDatasetMappings(copyActivity)` - Get dataset mappings for Copy activity
- `getComponentSummary(components)` - Get summary statistics

**Dependencies**: `globalParameterDetectionService`, `parameterizedLinkedServiceDetectionService`, `folderAnalysisService`

---

#### `globalParameterDetectionService.ts`
**Purpose**: Detects global parameter references in ADF pipeline expressions.

**Key Features**:
- 3 regex patterns for detecting global parameters:
  - Standard: `@pipeline().globalParameters.X`
  - Curly-brace: `@{pipeline().globalParameters.X}`
  - Function-wrapped: `pipeline().globalParameters.X`
- Type mapping from ADF to Fabric
- Pipeline usage tracking

---

#### `parameterizedLinkedServiceDetectionService.ts`
**Purpose**: Detects LinkedServices with parameters (not supported in Fabric connections).

**Key Features**:
- Identifies LinkedServices with parameter definitions
- Tracks affected pipelines and activities
- Generates warning messages for users

---

### Fabric API Services

#### `fabricService.ts`
**Purpose**: Main orchestrator for Fabric API interactions.

**Key Features**:
- Workspace management
- Connection deployment
- Pipeline deployment with dependency resolution
- Variable library creation
- Schedule creation
- Folder structure deployment
- Deployment plan generation

**Key Methods**:
- `getWorkspaces(accessToken)` - Fetch accessible workspaces
- `deployComponents(mappedComponents, accessToken, workspaceId, ...)` - Deploy all components
- `deployConnections(linkedServices, supportedTypes, accessToken, onProgress)` - Deploy connections
- `generateDeploymentPlan(mappedComponents, workspaceId, accessToken)` - Generate downloadable plan

**Dependencies**: `gatewayService`, `connectionService`, `pipelineTransformer`, `activityTransformer`, `scheduleService`, `workspaceIdentityService`

---

#### `fabricApiClient.ts`
**Purpose**: Low-level Fabric REST API client with error handling.

**Key Features**:
- HTTP request handling
- API error parsing and formatting
- Rate limiting integration
- Request/response logging

---

#### `fabricRateLimiter.ts`
**Purpose**: Implements rate limiting for Fabric API calls.

**Key Features**:
- Request throttling
- Retry logic with exponential backoff
- Concurrent request limiting

---

#### `fabricWorkspaceService.ts`
**Purpose**: Workspace-specific API operations.

**Key Features**:
- Workspace metadata retrieval
- Permission validation
- Workspace item listing

---

#### `fabricConnectionsService.ts`
**Purpose**: Connection-specific API operations.

**Key Features**:
- Connection creation
- Connection validation
- Connection metadata retrieval

---

### Connection Services

#### `connectionService.ts`
**Purpose**: Manages connection creation and mapping.

**Key Features**:
- Connection type determination
- Connection payload generation
- LinkedService to Fabric connection mapping
- Failed connector tracking
- Supported connection types loading

**Key Methods**:
- `createConnector(component, accessToken, workspaceId)` - Create a Fabric connection
- `determineConnectionTypePublic(component, connectVia)` - Determine Fabric connection type
- `getConnectionPayload(component, connectionType, connectVia)` - Build API payload
- `mapLinkedServiceToConnection(linkedServiceName)` - Get mapped connection ID
- `loadSupportedConnectionTypes(accessToken)` - Load available connection types

---

#### `connectionDeploymentService.ts`
**Purpose**: Handles bulk connection deployment.

**Key Features**:
- Batch deployment with progress tracking
- Error aggregation
- Deployment status reporting

---

#### `connectionsListService.ts`
**Purpose**: Fetches existing connections from Fabric workspace.

**Key Features**:
- List existing connections
- Filter by type
- Pagination support

---

#### `linkedServiceConnectionService.ts`
**Purpose**: Bridge between ADF LinkedServices and Fabric connections.

**Key Features**:
- LinkedService to connection mapping
- Connection configuration building
- Credential handling

---

#### `linkedServiceMappingBridgeService.ts`
**Purpose**: Creates a bridge between Configure Connections page and Map Components page.

**Key Features**:
- Mapping state persistence
- Cross-page communication
- LinkedService lookup by name

---

#### `existingConnectionsService.ts`
**Purpose**: Manages existing Fabric connections for reuse.

**Key Features**:
- Fetch existing connections
- Match LinkedServices to existing connections
- Connection compatibility checking

---

#### `dynamicConnectorService.ts`
**Purpose**: Handles dynamic connector schema loading.

**Key Features**:
- Schema fetching from Fabric API
- Parameter validation
- Credential type determination

---

#### `supportedConnectionTypesService.ts`
**Purpose**: Manages supported connection type definitions.

**Key Features**:
- Type definition caching
- Parameter schema extraction
- Credential type mapping

---

### Transformer Services

#### `pipelineTransformer.ts`
**Purpose**: Transforms ADF pipeline definitions to Fabric format.

**Key Features**:
- Pipeline structure conversion
- Activity transformation
- Connection reference resolution
- Global parameter expression transformation
- Library variable injection
- Execute Pipeline resolution

**Key Methods**:
- `transformPipelineDefinition(definition, pipelineConnectionMappings)` - Main transformation
- `transformGlobalParameterExpressions(definition, parameterNames, libraryName)` - Convert global params
- `injectLibraryVariables(definition, libraryName, variableNamesWithTypes)` - Add library vars
- `setReferenceMappings(mappings)` - Set reference ID mappings for Custom activities
- `setLinkedServiceBridge(bridge)` - Set LinkedService connection bridge

---

#### `activityTransformer.ts`
**Purpose**: Transforms individual ADF activities to Fabric format.

**Key Features**:
- Activity-specific transformations
- LinkedService reference conversion to `externalReferences.connection`
- Expression format conversion
- Inactive activity marking for failed connectors

**Key Methods**:
- `transformLinkedServiceReferencesToFabric(activity)` - Convert LinkedService refs
- `countInactiveActivities(activities)` - Count activities marked inactive
- `setExternalReferences(activity)` - Set Fabric connection references

---

#### `copyActivityTransformer.ts`
**Purpose**: Specialized transformer for Copy activities.

**Key Features**:
- Source/sink dataset embedding
- Dataset parameter substitution
- Connection mapping for source and sink
- Schema preservation

---

#### `customActivityTransformer.ts`
**Purpose**: Handles Custom activity transformation with 4-tier connection resolution.

**Key Features**:
- 4-tier fallback connection resolution:
  1. Reference ID-based mappings (primary)
  2. Activity name-based mappings
  3. LinkedService bridge (Configure Connections)
  4. ConnectionService fallback
- Multiple LinkedService reference locations:
  - Activity-level: `linkedServiceName`
  - Resource-level: `typeProperties.resourceLinkedService`
  - Reference objects: `typeProperties.referenceObjects.linkedServices[]`
- Detailed logging with emoji indicators

---

#### `pipelineConnectionTransformer.ts`
**Purpose**: Applies connection mappings to pipeline definitions.

**Key Features**:
- Pipeline-level connection transformation
- Activity connection injection
- Missing connection handling

---

#### `pipelineConnectionTransformerService.ts`
**Purpose**: Service wrapper for pipeline connection transformation.

**Key Features**:
- Static method access
- Fabric pipeline payload generation
- Connection mapping summary

---

### Mapping Services

#### `connectorMappingService.ts`
**Purpose**: Maps ADF connector types to Fabric connection types.

**Key Features**:
- 50+ connector type mappings
- Authentication method mapping
- Gateway requirement detection
- Fallback type handling

---

#### `componentMappingService.ts`
**Purpose**: Maps ADF components to Fabric targets.

**Key Features**:
- Default target generation
- Schedule configuration initialization
- Component type mapping

---

#### `componentValidationService.ts`
**Purpose**: Validates component compatibility for migration.

**Key Features**:
- Compatibility status determination
- Warning generation
- Suggestion generation for unsupported components

---

#### `connectorSkipDecisionService.ts`
**Purpose**: Determines if a connector should be skipped during deployment.

**Key Features**:
- Auto-skip decision logic
- Alternative suggestions
- Skip reason generation

---

#### `connectorService.ts`
**Purpose**: General connector operations.

**Key Features**:
- Connector type detection
- Connector validation
- Connector metadata extraction

---

#### `customActivityMappingService.ts`
**Purpose**: Generates Custom activity mapping UI data.

**Key Features**:
- Reference extraction from Custom activities
- Mapping state generation
- Reference ID generation

---

#### `unifiedActivityMappingService.ts`
**Purpose**: Creates unified activity mapping for all activity types.

**Key Features**:
- Activity type categorization
- Reference extraction for all activity types
- Nested activity handling
- Activity group generation for UI

---

### Deployment Services

#### `gatewayService.ts`
**Purpose**: Manages Fabric gateway creation for on-premises connections.

**Key Features**:
- Gateway type detection
- Gateway payload generation
- Gateway creation with retry
- Failed gateway tracking

---

#### `folderDeploymentService.ts`
**Purpose**: Deploys folder structure to Fabric workspace.

**Key Features**:
- Hierarchical folder creation
- Parent folder resolution
- Folder ID mapping generation

---

#### `scheduleService.ts`
**Purpose**: Creates pipeline schedules in Fabric.

**Key Features**:
- Schedule trigger conversion
- Recurrence mapping
- Multi-pipeline schedule handling
- Disabled deployment by default (safety)

---

#### `scheduleConversionService.ts`
**Purpose**: Converts ADF trigger definitions to Fabric schedule format.

**Key Features**:
- Frequency type mapping
- Time zone conversion
- Recurrence pattern translation

---

#### `variableLibraryService.ts`
**Purpose**: Creates Variable Libraries in Fabric for global parameters.

**Key Features**:
- Variable Library payload generation
- Base64 encoding for parts
- Variable type mapping
- Deployment with error handling

---

#### `invokePipelineService.ts`
**Purpose**: Manages Execute Pipeline activity dependencies.

**Key Features**:
- Dependency graph building
- Deployment order calculation
- Circular dependency detection
- Pipeline reference validation

---

#### `pipelineFallbackService.ts`
**Purpose**: Fallback resolution for missing pipeline references.

**Key Features**:
- Pipeline lookup by name in workspace
- Cache for resolved pipeline IDs
- Error handling for missing pipelines

---

### Analysis Services

#### `folderAnalysisService.ts`
**Purpose**: Analyzes and processes folder structure from ADF.

**Key Features**:
- Folder extraction from pipelines
- Depth validation (Fabric limit: 10 levels)
- Folder flattening for deep hierarchies
- Folder tree building

---

#### `pipelineActivityAnalysisService.ts`
**Purpose**: Analyzes activities within pipelines.

**Key Features**:
- Activity extraction (including nested)
- LinkedService reference detection
- Activity type categorization
- Custom activity detection

---

#### `profileExportService.ts`
**Purpose**: Exports profiling data for download.

**Key Features**:
- JSON export generation
- Summary statistics
- Compatibility report generation

---

### Identity Services

#### `managedIdentityService.ts`
**Purpose**: Handles Managed Identity detection and mapping.

**Key Features**:
- Managed Identity usage detection
- Workspace Identity mapping
- Credential configuration

---

#### `workspaceIdentityService.ts`
**Purpose**: Manages Fabric Workspace Identity.

**Key Features**:
- Workspace Identity retrieval
- Application ID extraction
- Service Principal ID mapping

---

---

## Components

### Pages (`src/components/pages/`)

The wizard pages guide users through the migration process.

| Page | Step | Description |
|------|------|-------------|
| `UploadPage.tsx` | 0 | ARM template upload and profiling (no login required) |
| `LoginPage.tsx` | 1 | Azure AD authentication |
| `WorkspacePage.tsx` | 2 | Fabric workspace selection |
| `WorkspaceSelectionPage.tsx` | 2 (alt) | Alternative workspace selection view |
| `ManagedIdentityPage.tsx` | 3 | Managed Identity to Workspace Identity mapping |
| `LinkedServiceConnectionPage.tsx` | 4 | Connection configuration for LinkedServices |
| `EnhancedLinkedServiceConnectionPage.tsx` | 4 (enhanced) | Enhanced connection configuration UI |
| `DeployConnectionsPage.tsx` | 5 | Connection deployment with progress |
| `ValidationPage.tsx` | 6 | Component compatibility validation |
| `GlobalParameterConfigurationPage.tsx` | 7 | Global parameter Variable Library config (conditional) |
| `MappingPage.tsx` | 8 | Component to Fabric target mapping |
| `DeploymentPage.tsx` | 9 | Deployment execution with progress |
| `CompletePage.tsx` | 10 | Migration summary and next steps |
| `SystemValidationPage.tsx` | N/A | System validation and diagnostics |

### Profiling Components (`src/components/profiling/`)

| Component | Description |
|-----------|-------------|
| `ProfilingDashboard.tsx` | Main profiling dashboard with all metrics |
| `MetricsOverview.tsx` | High-level metrics summary cards |
| `ArtifactTables.tsx` | Detailed artifact listings (pipelines, datasets, etc.) |
| `DependencyGraphView.tsx` | D3-based dependency visualization |
| `InsightsPanel.tsx` | AI-generated insights and recommendations |
| `LoadingSkeletons.tsx` | Loading state placeholders |
| `ProfilingErrorBoundary.tsx` | Error boundary for profiling components |

### UI Components (`src/components/ui/`)

The application uses [shadcn/ui](https://ui.shadcn.com/) for accessible UI primitives. Key components include:

| Component | Description |
|-----------|-------------|
| `button.tsx` | Button variants (primary, secondary, ghost, etc.) |
| `card.tsx` | Card container with header, content, footer |
| `dialog.tsx` | Modal dialogs |
| `dropdown-menu.tsx` | Dropdown menus |
| `form.tsx` | Form components with react-hook-form |
| `input.tsx` | Text input fields |
| `select.tsx` | Select dropdowns |
| `table.tsx` | Data tables |
| `tabs.tsx` | Tab navigation |
| `tooltip.tsx` | Tooltips |
| `progress.tsx` | Progress indicators |
| `badge.tsx` | Status badges |
| `alert.tsx` | Alert messages |
| `accordion.tsx` | Collapsible sections |
| `searchable-select.tsx` | Select with search functionality |
| `scroll-area.tsx` | Scrollable containers |
| `separator.tsx` | Visual separators |
| `skeleton.tsx` | Loading skeletons |
| `sonner.tsx` | Toast notifications |
| `switch.tsx` | Toggle switches |
| `checkbox.tsx` | Checkboxes |
| `radio-group.tsx` | Radio button groups |
| `slider.tsx` | Range sliders |

### Layout Components

| Component | Description |
|-----------|-------------|
| `WizardLayout.tsx` | Main wizard navigation layout |
| `WorkspaceDisplay.tsx` | Selected workspace display |
| `WorkspaceSummary.tsx` | Workspace details summary |

### Debug Components (`src/components/debug/`)

| Component | Description |
|-----------|-------------|
| `ScopeDebugPanel.tsx` | Token scope debugging panel |
| `TokenDebugInfo.tsx` | Token information display |
| `TokenDebugPanel.tsx` | Comprehensive token debugging |
| `NavigationDebug.tsx` | Wizard navigation state debugging |

---

## Contexts

### `AppContext.tsx`

**Purpose**: Global application state management using React Context and useReducer.

**State Shape** (`AppState`):
```typescript
{
  currentStep: number;
  auth: AuthState;
  selectedWorkspace: WorkspaceInfo | null;
  availableWorkspaces: WorkspaceInfo[];
  uploadedFile: File | null;
  adfComponents: ADFComponent[];
  selectedComponents: ADFComponent[];
  adfProfile: ADFProfile | null;
  connectionMappings: ConnectionMappingState;
  pipelineConnectionMappings: PipelineConnectionMappings;
  pipelineReferenceMappings: PipelineReferenceMappings;
  linkedServiceConnectionBridge: LinkedServiceConnectionBridge;
  workspaceCredentials: WorkspaceCredentialState;
  deploymentResults: DeploymentResult[];
  connectionDeploymentResults: ConnectionDeploymentResult[];
  isLoading: boolean;
  error: string | null;
  folderHierarchy: FolderTreeNode[];
  folderMappings: Record<string, string>;
  folderDeploymentResults: FolderDeploymentResult[];
  globalParameterReferences: GlobalParameterReference[];
  variableLibraryConfig: VariableLibraryConfig | null;
  globalParameterConfigCompleted: boolean;
}
```

**Key Actions**:
- `SET_CURRENT_STEP` - Navigate wizard steps
- `SET_AUTH` - Update authentication state
- `SET_ADF_COMPONENTS` - Set parsed components
- `SET_ADF_PROFILE` - Set profiling data
- `UPDATE_COMPONENT_SELECTION` - Toggle component selection
- `SET_PIPELINE_CONNECTION_MAPPINGS` - Set connection mappings
- `SET_GLOBAL_PARAMETER_REFERENCES` - Set detected global params
- `SET_VARIABLE_LIBRARY_CONFIG` - Configure Variable Library
- `SET_DEPLOYMENT_RESULTS` - Store deployment results

**Exported Hooks**:
- `useAppContext()` - Access state and dispatch
- `useWizardNavigation()` - Wizard navigation helpers

---

## Hooks

### `useWizardNavigation.ts`
**Purpose**: Wizard navigation logic and step validation.

**Returns**:
```typescript
{
  currentStep: number;
  currentStepName: WizardStep;
  totalSteps: number;
  wizardSteps: WizardStep[];
  canGoNext: boolean;
  canGoPrevious: boolean;
  goNext: () => void;
  goPrevious: () => void;
  goToStep: (step: number) => void;
  getNavigationBlockingReason: (step?: number) => string;
  stepRequiresConfiguration: (stepName: WizardStep) => boolean;
}
```

### `useWorkspaceOperations.ts`
**Purpose**: Workspace-related operations.

**Features**:
- Workspace loading
- Permission validation
- Workspace selection

### `use-mobile.ts`
**Purpose**: Mobile viewport detection.

**Returns**: `boolean` indicating if viewport is mobile-sized.

---

## Types

### Core Types (`src/types/index.ts`)

#### Authentication Types
- `AuthState` - User authentication state
- `TokenScopes` - OAuth token scopes
- `ServicePrincipalAuth` - Service principal credentials
- `TenantConfig` - Azure AD tenant configuration
- `InteractiveLoginConfig` - Interactive login configuration

#### Component Types
- `ADFComponent` - Parsed ADF component
- `FabricTarget` - Target Fabric resource configuration
- `ComponentMapping` - Component to target mapping
- `ValidationRule` - Validation rule definition
- `ComponentSummary` - Component statistics

#### Deployment Types
- `DeploymentResult` - Individual deployment result
- `DeploymentPlan` - Full deployment plan
- `APIRequestDetails` - API request details for debugging
- `ApiError` - API error structure

#### Connection Types
- `LinkedServiceConnection` - LinkedService connection mapping
- `SupportedConnectionType` - Fabric connection type schema
- `ConnectionParameter` - Connection parameter definition
- `CredentialType` - Credential type configuration
- `ConnectionMappingState` - Connection mapping state
- `ConnectionDeploymentResult` - Connection deployment result

#### Activity Mapping Types
- `ActivityConnectionMapping` - Activity to connection mapping
- `PipelineConnectionMappings` - Pipeline-level mappings
- `CustomActivityLinkedServiceReference` - Custom activity reference
- `CustomActivityMapping` - Complete Custom activity mapping
- `ActivityWithReferences` - Unified activity with all references
- `ActivityGroup` - Activity group for UI
- `PipelineMappingSummary` - Pipeline mapping summary

#### Folder Types
- `ADFFolderInfo` - ADF folder information
- `FabricFolder` - Fabric folder representation
- `FolderTreeNode` - Folder hierarchy tree node
- `FolderDeploymentResult` - Folder deployment result

#### Schedule Types
- `FabricScheduleConfig` - Fabric schedule configuration
- `ADFRecurrence` - ADF trigger recurrence
- Specialized: `CronScheduleConfig`, `DailyScheduleConfig`, `WeeklyScheduleConfig`, `MonthlyScheduleConfig`

#### Global Parameter Types
- `GlobalParameterReference` - Detected global parameter
- `VariableLibraryConfig` - Variable Library configuration
- `VariableDefinition` - Variable definition for library

### Profiling Types (`src/types/profiling.ts`)

- `ADFProfile` - Complete profile structure
- `ProfileMetrics` - Metrics and statistics
- `ArtifactBreakdown` - Detailed artifact listings
- `DependencyGraph` - Graph nodes and edges
- `ProfileInsight` - Generated insights
- `PipelineArtifact`, `DatasetArtifact`, `LinkedServiceArtifact`, etc.

### Auth Types (`src/types/auth.ts`)

Extended authentication types for MSAL integration.

---

## Library Utilities

### `msalConfig.ts`
**Purpose**: MSAL configuration for Azure AD.

**Exports**:
- `fabricScopes` - Required OAuth scopes
- Base MSAL configuration

### `msalTenantUtils.ts`
**Purpose**: Tenant-specific MSAL utilities.

**Exports**:
- `validateAndConfigureTenant(tenantId)` - Validate and configure tenant
- `createTenantSpecificMsalInstance(tenantConfig, appId)` - Create MSAL instance
- `createTenantSpecificLoginRequest(tenantConfig)` - Create login request
- `createTenantSpecificSilentRequest(tenantConfig)` - Create silent request

### `authUtils.ts`
**Purpose**: Authentication helper utilities.

**Exports**:
- `isValidAuthState(state)` - Validate auth state structure
- `extractErrorMessage(error)` - Extract error message
- `sanitizeString(str)` - Sanitize input strings

### `tokenUtils.ts`
**Purpose**: Token validation and parsing.

**Exports**:
- `validateAuthenticationResult(result)` - Validate MSAL result
- `validateTokenScopes(token)` - Parse and validate scopes

### `validation.ts`
**Purpose**: ARM template validation utilities.

**Exports**:
- `safeJsonParse(content)` - Safe JSON parsing
- `isValidARMTemplate(template)` - Validate ARM template structure
- `isValidARMResource(resource)` - Validate ARM resource
- `extractComponentName(name)` - Extract component name from ARM path
- `isValidComponentType(type)` - Validate component type

### `stateValidation.ts`
**Purpose**: Application state validation.

**Exports**:
- `createDefaultAppState()` - Create initial app state
- State validation helpers

### `scopeValidation.ts`
**Purpose**: OAuth scope validation.

**Exports**:
- Scope validation utilities

### `utils.ts`
**Purpose**: General utility functions.

**Exports**:
- `cn(...classes)` - Class name merging utility

### `connectorMapping.ts`
**Purpose**: ADF to Fabric connector type mapping definitions.

### `enhancedMappingSuggestions.ts`
**Purpose**: Enhanced mapping suggestions for connectors.

### `systemValidator.ts`
**Purpose**: System validation checks.

### `testHelpers.ts`
**Purpose**: Test helper utilities.

---

## Validation

### `copy-activity-fix-validation.ts`
**Purpose**: Validation tests for Copy activity transformations.

### `copy-activity-test-runner.ts`
**Purpose**: Test runner for Copy activity tests.

### `mapping-fix-test.ts`
**Purpose**: Mapping fix verification tests.

### `pipelineFallbackValidation.ts`
**Purpose**: Pipeline fallback resolution validation.

---

## Module Relationships

### Data Flow

```
UploadPage
    │
    ▼
adfParserService.parseARMTemplate()
    │
    ├── globalParameterDetectionService
    ├── parameterizedLinkedServiceDetectionService
    └── folderAnalysisService
    │
    ▼
AppContext (SET_ADF_COMPONENTS, SET_ADF_PROFILE)
    │
    ▼
LinkedServiceConnectionPage
    │
    ▼
connectionService + dynamicConnectorService
    │
    ▼
DeployConnectionsPage
    │
    ▼
linkedServiceConnectionService.createConnection()
    │
    ▼
MappingPage
    │
    ▼
unifiedActivityMappingService
customActivityMappingService
    │
    ▼
DeploymentPage
    │
    ▼
fabricService.deployComponents()
    │
    ├── folderDeploymentService
    ├── variableLibraryService
    ├── gatewayService
    ├── connectionService
    ├── pipelineTransformer
    │   ├── activityTransformer
    │   ├── copyActivityTransformer
    │   └── customActivityTransformer
    └── scheduleService
    │
    ▼
CompletePage
```

### Service Dependencies

| Service | Depends On |
|---------|------------|
| `fabricService` | `gatewayService`, `connectionService`, `pipelineTransformer`, `activityTransformer`, `scheduleService`, `workspaceIdentityService`, `invokePipelineService` |
| `adfParserService` | `globalParameterDetectionService`, `parameterizedLinkedServiceDetectionService`, `folderAnalysisService` |
| `pipelineTransformer` | `activityTransformer`, `copyActivityTransformer`, `customActivityTransformer`, `pipelineConnectionTransformer` |
| `connectionService` | `dynamicConnectorService`, `connectorMappingService`, `gatewayService`, `fabricApiClient` |
| `customActivityTransformer` | `customActivityMappingService`, `linkedServiceMappingBridgeService`, `connectionService` |

---

## Key Design Patterns

### 1. Service Singleton Pattern
Most services export a singleton instance:
```typescript
export const authService = new AuthService();
export const adfParserService = new ADFParserService();
```

### 2. 4-Tier Fallback Resolution
Custom activity connection resolution uses multiple fallback strategies:
1. Reference ID-based mappings (primary)
2. Activity name-based mappings
3. LinkedService bridge
4. ConnectionService fallback

### 3. Upload-First Profiling
Profiling happens before authentication:
- No login required for initial analysis
- Privacy-first approach
- Informed decision-making before committing

### 4. State Machine Wizard
Navigation follows strict step validation:
- Each step has preconditions
- Blocking reasons are user-friendly
- Steps can be conditional (e.g., global parameters)

### 5. Expression Transformation
Global parameter expressions are transformed:
```
@pipeline().globalParameters.X 
  → @pipeline().libraryVariables.LibName_VariableLibrary_X
```

---

## Best Practices

### Adding New Services

1. Create the service file in `src/services/`
2. Export a singleton instance
3. Add TypeScript types in `src/types/`
4. Document the service in this file
5. Add unit tests in `src/services/__tests__/`

### Adding New Components

1. Create component in appropriate directory
2. Use shadcn/ui primitives where possible
3. Connect to AppContext if needed
4. Add error boundaries for critical components

### Modifying Transformers

1. Ensure backward compatibility
2. Add comprehensive logging
3. Handle edge cases gracefully
4. Update this documentation

---

*Last Updated: November 2025*
